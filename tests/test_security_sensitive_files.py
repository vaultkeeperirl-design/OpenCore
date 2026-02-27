import unittest
import os
from unittest.mock import patch
from opencore.tools.base import read_file, write_file, list_files, _is_safe_path
from opencore.config import settings

class TestSensitiveFiles(unittest.TestCase):
    def setUp(self):
        # Create a dummy .env file
        with open(".env", "w") as f:
            f.write("SECRET=12345")

        # Ensure we are in a safe mode
        self.original_allow_unsafe = settings.allow_unsafe_system_access
        # We need to mock settings.allow_unsafe_system_access because it's a property that reads env var
        # But for this test, let's assume default is False, or patch it.
        # Since settings is instantiated at module level, patching os.environ might not work
        # if the property caches or if we don't reload.
        # But settings.allow_unsafe_system_access reads os.getenv every time.

        self.patcher = patch.dict(os.environ, {"ALLOW_UNSAFE_SYSTEM_ACCESS": "false"})
        self.patcher.start()

    def tearDown(self):
        # Cleanup
        if os.path.exists(".env"):
            os.remove(".env")

        self.patcher.stop()

    def test_read_env_blocked(self):
        result = read_file(".env")
        self.assertIn("Access denied", result)

    def test_write_env_blocked(self):
        result = write_file(".env", "NEW_SECRET=67890")
        self.assertIn("Access denied", result)

        # Verify content wasn't changed
        with open(".env", "r") as f:
            content = f.read()
        self.assertEqual(content, "SECRET=12345")

    def test_list_files_hides_env(self):
        result = list_files(".")
        self.assertNotIn(".env", result)

        # Double check that .env actually exists
        self.assertTrue(os.path.exists(".env"))

    def test_git_blocked(self):
        # Create a dummy .git directory
        if not os.path.exists(".git"):
             os.makedirs(".git")
             with open(".git/config", "w") as f:
                 f.write("config")

        try:
            result = read_file(".git/config")
            self.assertIn("Access denied", result)

            result = list_files(".git")
            self.assertIn("Access denied", result)

        finally:
            # Cleanup .git if we created it (careful not to delete real .git if running in repo root)
            # The test runner might be running in repo root.
            # So we should be careful.
            # _is_safe_path blocks .git in path components.
            pass

    def test_is_safe_path_sensitive(self):
        self.assertFalse(_is_safe_path(".env"))
        self.assertFalse(_is_safe_path("./.env"))
        self.assertFalse(_is_safe_path("subdir/.env"))
        self.assertFalse(_is_safe_path(".DS_Store"))
        self.assertFalse(_is_safe_path(".git/config"))

if __name__ == '__main__':
    unittest.main()
