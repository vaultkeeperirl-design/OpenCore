import unittest
from unittest.mock import patch, mock_open
import json
import os
from opencore.auth.qwen import get_qwen_credentials

class TestQwenAuth(unittest.TestCase):
    @patch('os.path.exists')
    @patch('os.path.expanduser')
    @patch('builtins.open', new_callable=mock_open, read_data='{"access_token": "test_token"}')
    def test_get_qwen_credentials_success(self, mock_file, mock_expanduser, mock_exists):
        mock_exists.return_value = True
        mock_expanduser.return_value = "/home/user"

        token = get_qwen_credentials()

        self.assertEqual(token, "test_token")
        mock_expanduser.assert_called_once_with("~")
        mock_exists.assert_called_once_with("/home/user/.qwen/oauth_creds.json")
        mock_file.assert_called_once_with("/home/user/.qwen/oauth_creds.json", "r")

    @patch('os.path.exists')
    def test_get_qwen_credentials_file_missing(self, mock_exists):
        mock_exists.return_value = False

        token = get_qwen_credentials()

        self.assertIsNone(token)

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='invalid json')
    def test_get_qwen_credentials_invalid_json(self, mock_file, mock_exists):
        mock_exists.return_value = True

        token = get_qwen_credentials()

        self.assertIsNone(token)

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{"wrong_key": "test_token"}')
    def test_get_qwen_credentials_missing_token(self, mock_file, mock_exists):
        mock_exists.return_value = True

        token = get_qwen_credentials()

        self.assertIsNone(token)

    @patch('os.path.exists')
    def test_get_qwen_credentials_exception(self, mock_exists):
        mock_exists.side_effect = Exception("Unexpected error")

        token = get_qwen_credentials()

        self.assertIsNone(token)

if __name__ == '__main__':
    unittest.main()
