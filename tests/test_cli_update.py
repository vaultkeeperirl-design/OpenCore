import unittest
from unittest.mock import patch, MagicMock
import sys
import subprocess # Import real subprocess to access exception classes
from opencore.cli.update import update_system

class TestCliUpdate(unittest.TestCase):
    @patch('opencore.cli.update.subprocess')
    @patch('opencore.cli.update.Path')
    def test_update_system_success(self, mock_path, mock_subprocess):
        # Configure mock to have real exception class
        mock_subprocess.CalledProcessError = subprocess.CalledProcessError
        mock_subprocess.DEVNULL = subprocess.DEVNULL

        # Mock Path
        mock_file_obj = MagicMock()
        mock_path.return_value.resolve.return_value = mock_file_obj
        mock_repo_root = mock_file_obj.parent.parent.parent

        # Mock .git existence
        (mock_repo_root / ".git").exists.return_value = True

        # Mock git version check (success)
        mock_subprocess.run.return_value.returncode = 0

        # Run function
        with patch('sys.stdout', new=MagicMock()):
             update_system()

        # Verify calls
        mock_subprocess.check_call.assert_any_call(["git", "pull"], cwd=mock_repo_root)
        mock_subprocess.check_call.assert_any_call(
            [sys.executable, "-m", "pip", "install", "-e", "."],
            cwd=mock_repo_root
        )

    @patch('opencore.cli.update.subprocess')
    @patch('opencore.cli.update.Path')
    def test_update_system_no_git_repo(self, mock_path, mock_subprocess):
        mock_subprocess.CalledProcessError = subprocess.CalledProcessError
        mock_subprocess.DEVNULL = subprocess.DEVNULL

        # Mock Path
        mock_file_obj = MagicMock()
        mock_path.return_value.resolve.return_value = mock_file_obj
        mock_repo_root = mock_file_obj.parent.parent.parent

        # Mock .git NOT exists
        (mock_repo_root / ".git").exists.return_value = False

        # Mock git version check (success)
        mock_subprocess.run.return_value.returncode = 0

        # Expect exit
        with self.assertRaises(SystemExit) as cm:
            with patch('sys.stdout', new=MagicMock()):
                update_system()
        self.assertEqual(cm.exception.code, 1)

    @patch('opencore.cli.update.subprocess')
    @patch('opencore.cli.update.Path')
    def test_update_system_git_not_installed(self, mock_path, mock_subprocess):
        mock_subprocess.CalledProcessError = subprocess.CalledProcessError
        mock_subprocess.DEVNULL = subprocess.DEVNULL

        # Mock git version check failure
        mock_subprocess.run.side_effect = FileNotFoundError

        with self.assertRaises(SystemExit) as cm:
            with patch('sys.stdout', new=MagicMock()):
                update_system()
        self.assertEqual(cm.exception.code, 1)
