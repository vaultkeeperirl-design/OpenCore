import unittest
from unittest.mock import patch, MagicMock
import os
from opencore.tools.base import execute_command

class TestCommandPathTraversal(unittest.TestCase):

    @patch.dict(os.environ, {"ALLOW_UNSAFE_SYSTEM_ACCESS": "false"})
    @patch("opencore.tools.base.subprocess.run")
    def test_blocks_absolute_path_args(self, mock_run):
        # Command: cat /etc/passwd
        # Should be blocked because /etc/passwd is outside CWD
        result = execute_command("cat /etc/passwd")

        self.assertIn("Error: Access denied", result)
        self.assertIn("Path traversal detected", result)
        mock_run.assert_not_called()

    @patch.dict(os.environ, {"ALLOW_UNSAFE_SYSTEM_ACCESS": "false"})
    @patch("opencore.tools.base.subprocess.run")
    def test_blocks_relative_path_traversal(self, mock_run):
        # Command: cat ../outside.txt
        result = execute_command("cat ../outside.txt")

        self.assertIn("Error: Access denied", result)
        mock_run.assert_not_called()

    @patch.dict(os.environ, {"ALLOW_UNSAFE_SYSTEM_ACCESS": "false"})
    @patch("opencore.tools.base.subprocess.run")
    def test_allows_safe_args(self, mock_run):
        # Command: cat safe.txt
        # Should be allowed
        mock_run.return_value = MagicMock(stdout="content", stderr="")

        execute_command("cat safe.txt")

        mock_run.assert_called_once()

    @patch.dict(os.environ, {"ALLOW_UNSAFE_SYSTEM_ACCESS": "false"})
    @patch("opencore.tools.base.subprocess.run")
    def test_allows_flags(self, mock_run):
        # Command: ls -la
        # Should be allowed (-la is safe)
        mock_run.return_value = MagicMock(stdout="total 0", stderr="")

        execute_command("ls -la")

        mock_run.assert_called_once()

    @patch.dict(os.environ, {"ALLOW_UNSAFE_SYSTEM_ACCESS": "false"})
    @patch("opencore.tools.base.subprocess.run")
    def test_blocks_absolute_command_path(self, mock_run):
        # Command: /bin/ls
        # Should be blocked because /bin/ls is outside CWD
        result = execute_command("/bin/ls")

        self.assertIn("Error: Access denied", result)
        self.assertIn("/bin/ls", result)
        mock_run.assert_not_called()

    @patch.dict(os.environ, {"ALLOW_UNSAFE_SYSTEM_ACCESS": "false"})
    @patch("opencore.tools.base.subprocess.run")
    def test_grep_path_traversal(self, mock_run):
        # Command: grep "pattern" /etc/passwd
        # Should block /etc/passwd
        result = execute_command('grep "pattern" /etc/passwd')

        self.assertIn("Error: Access denied", result)
        mock_run.assert_not_called()

if __name__ == "__main__":
    unittest.main()
