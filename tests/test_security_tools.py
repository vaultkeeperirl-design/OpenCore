import unittest
import os
import tempfile
from unittest.mock import patch
from opencore.tools.base import read_file, write_file, list_files, execute_command


class TestSecurityTools(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.gettempdir()
        self.test_file_path = os.path.join(self.temp_dir, "hacked_read.txt")

    def test_path_traversal_read(self):
        # Try to read a file outside the current directory
        # The tool should block read access from outside CWD
        try:
            with open(self.test_file_path, "w") as f:
                f.write("secret")
        except OSError:
            pass

        result = read_file(self.test_file_path)
        self.assertTrue(
            result.startswith("Error: Access denied"),
            f"Should fail reading {self.test_file_path} with access denied, got: {result}"
        )

    def test_path_traversal_write(self):
        target = os.path.join(self.temp_dir, "hacked_write.txt")
        result = write_file(target, "data")
        self.assertTrue(
            result.startswith("Error: Access denied"),
            f"Should fail writing {target} with access denied, got: {result}"
        )

    def test_path_traversal_list(self):
        # Try to list temp dir or ..
        result = list_files(self.temp_dir)
        self.assertTrue(
            result.startswith("Error: Access denied"),
            f"Should fail listing {self.temp_dir} with access denied, got: {result}"
        )

        result = list_files("..")
        self.assertTrue(
            result.startswith("Error: Access denied"),
            f"Should fail listing .. with access denied, got: {result}"
        )

    def test_valid_access(self):
        # Test writing and reading a file in current dir
        filename = "test_safe.txt"
        content = "safe content"

        # Ensure cleanup
        if os.path.exists(filename):
            os.remove(filename)

        try:
            write_res = write_file(filename, content)
            self.assertIn("successfully", write_res)

            read_res = read_file(filename)
            self.assertEqual(read_res, content)

            list_res = list_files(".")
            self.assertIn(filename, list_res)

        finally:
            if os.path.exists(filename):
                os.remove(filename)


class TestUnrestrictedAccess(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.gettempdir()
        self.test_file_path = os.path.join(self.temp_dir, "test_unrestricted.txt")
        self.outfile = os.path.join(self.temp_dir, "test_echo_shell.txt")
        self.outfile_no_shell = os.path.join(self.temp_dir, "test_echo_no_shell.txt")

    @patch.dict(os.environ, {"ALLOW_UNSAFE_SYSTEM_ACCESS": "true"})
    def test_unrestricted_access(self):
        # With the flag set, we should be able to access temp dir
        # Write
        res_write = write_file(self.test_file_path, "unrestricted")
        self.assertIn("written successfully", res_write)

        # Read
        res_read = read_file(self.test_file_path)
        self.assertEqual(res_read, "unrestricted")

        # List
        res_list = list_files(self.temp_dir)
        self.assertIn(os.path.basename(self.test_file_path), res_list)

        # Cleanup
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

    @patch.dict(os.environ, {"ALLOW_UNSAFE_SYSTEM_ACCESS": "true"})
    def test_unrestricted_command(self):
        # Use redirection to verify shell=True behavior
        if os.path.exists(self.outfile):
            os.remove(self.outfile)

        # This command relies on shell redirection
        output = execute_command(f"echo shell_enabled > {self.outfile}")

        # If shell=True, file should exist and output should be empty
        self.assertTrue(os.path.exists(self.outfile), "File not created, shell redirection failed")

        with open(self.outfile, 'r') as f:
            content = f.read().strip()
        self.assertEqual(content, "shell_enabled")

        # Cleanup
        os.remove(self.outfile)

    @patch.dict(os.environ, {"ALLOW_UNSAFE_SYSTEM_ACCESS": "false"})
    def test_restricted_command_behavior(self):
        # Verify that without the flag, redirection does NOT work (shell=False)
        if os.path.exists(self.outfile_no_shell):
            os.remove(self.outfile_no_shell)

        # This command should fail to redirect if shell=False
        output = execute_command(f"echo shell_disabled > {self.outfile_no_shell}")

        self.assertFalse(os.path.exists(self.outfile_no_shell), "File created, but should not have been (shell=False expected)")
        self.assertIn(">", output)
        self.assertIn("shell_disabled", output)


class TestSafetyGuard(unittest.TestCase):
    @patch.dict(os.environ, {"ALLOW_UNSAFE_SYSTEM_ACCESS": "true"})
    def test_blocks_dangerous_commands(self):
        # Even with unsafe access enabled, we should block rm -rf /
        dangerous_cmds = [
            "rm -rf /",
            "rm -rf /*",
            "rd /s /q c:\\",
            "rd /s /q /",
            "  rm -rf /  ", # Spaces should be stripped
            "sudo rm -rf /", # Should be caught by substring search
        ]

        for cmd in dangerous_cmds:
            with self.subTest(cmd=cmd):
                result = execute_command(cmd)
                self.assertIn("Error: Command blocked by safety guard", result)
                self.assertIn("is not allowed", result)

    @patch.dict(os.environ, {"ALLOW_UNSAFE_SYSTEM_ACCESS": "true"})
    def test_allows_safe_commands(self):
        # Safe commands should still work
        result = execute_command("echo safe")
        self.assertEqual(result.strip(), "safe")


if __name__ == "__main__":
    unittest.main()
