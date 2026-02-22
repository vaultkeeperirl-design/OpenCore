import unittest
import os
from opencore.tools.base import read_file, write_file, list_files


class TestSecurityTools(unittest.TestCase):
    def test_path_traversal_read(self):
        # Try to read a file outside the current directory
        # We assume /tmp exists and is accessible for writing (for setup)
        # but the tool should block read access from outside CWD

        # Note: In the sandbox, /tmp is writable.
        try:
            with open("/tmp/hacked_read.txt", "w") as f:
                f.write("secret")
        except OSError:
            pass  # Maybe permissions issue, but usually /tmp is writable

        # The tool should return an error message starting with
        # "Error: Access denied" if fixed.
        # Currently it will succeed or return a generic error if file
        # doesn't exist.

        result = read_file("/tmp/hacked_read.txt")
        # If vulnerable, it returns "secret" or generic error.
        # If fixed, it returns "Error: Access denied - Path traversal "
        # "detected."

        # We assert that it returns the specific access denied error.
        self.assertTrue(
            result.startswith("Error: Access denied"),
            f"Should fail reading /tmp/hacked_read.txt with access denied, "
            f"got: {result}"
        )

    def test_path_traversal_write(self):
        result = write_file("/tmp/hacked_write.txt", "data")
        self.assertTrue(
            result.startswith("Error: Access denied"),
            f"Should fail writing /tmp/hacked_write.txt with access denied, "
            f"got: {result}"
        )

    def test_path_traversal_list(self):
        # Try to list /tmp or ..
        result = list_files("/tmp")
        self.assertTrue(
            result.startswith("Error: Access denied"),
            f"Should fail listing /tmp with access denied, got: {result}"
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


if __name__ == "__main__":
    unittest.main()
