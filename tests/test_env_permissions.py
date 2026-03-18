import unittest
import os
import tempfile
import stat
from unittest.mock import patch
from opencore.config import Settings

class TestEnvPermissions(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory to isolate test files
        self.test_dir = tempfile.TemporaryDirectory()
        self.env_path = os.path.join(self.test_dir.name, ".env")

    def tearDown(self):
        self.test_dir.cleanup()

    @patch("opencore.config.load_dotenv")
    @patch("opencore.config.set_key")
    def test_update_env_sets_secure_permissions(self, mock_set_key, mock_load_dotenv):
        # Change the working directory for the test
        original_cwd = os.getcwd()
        os.chdir(self.test_dir.name)

        try:
            settings = Settings()
            updates = {"LLM_MODEL": "gpt-4o"}

            # The file does not exist yet
            self.assertFalse(os.path.exists(".env"))

            # Create/update the file
            settings.update_env(updates)

            # The file should now exist
            self.assertTrue(os.path.exists(".env"))

            # Check permissions
            file_stat = os.stat(".env")
            # We want to check if the permissions are 0o600
            # Note: The exact bits returned by os.stat include file type bits.
            # We mask them with stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO (0o777)
            permissions = file_stat.st_mode & 0o777
            self.assertEqual(permissions, 0o600)

            # Test updates to an existing file
            # Change permissions to something else to see if they are corrected
            os.chmod(".env", 0o644)
            self.assertEqual(os.stat(".env").st_mode & 0o777, 0o644)

            updates2 = {"HEARTBEAT_INTERVAL": 3600}
            settings.update_env(updates2)

            # Permissions should be reset to 0o600
            self.assertEqual(os.stat(".env").st_mode & 0o777, 0o600)

        finally:
            os.chdir(original_cwd)

if __name__ == "__main__":
    unittest.main()
