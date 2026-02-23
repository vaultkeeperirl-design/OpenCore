import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from opencore.interface.api import app

client = TestClient(app)

class TestApiConfig(unittest.TestCase):
    @patch("os.getenv")
    def test_get_config_includes_new_keys(self, mock_getenv):
        # Setup mock to return True for our keys when checked
        def side_effect(key, default=None):
            if key in ["DASHSCOPE_API_KEY", "GEMINI_API_KEY", "GROQ_API_KEY"]:
                return "dummy_key"
            return default

        mock_getenv.side_effect = side_effect

        response = client.get("/config")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertTrue(data.get("HAS_DASHSCOPE_KEY"))
        self.assertTrue(data.get("HAS_GEMINI_KEY"))
        self.assertTrue(data.get("HAS_GROQ_KEY"))

    @patch("os.getenv")
    def test_get_config_missing_keys(self, mock_getenv):
        # Setup mock to return default or None
        def side_effect(key, default=None):
            return default

        mock_getenv.side_effect = side_effect

        response = client.get("/config")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertFalse(data.get("HAS_DASHSCOPE_KEY"))
        self.assertFalse(data.get("HAS_GEMINI_KEY"))
        self.assertFalse(data.get("HAS_GROQ_KEY"))

if __name__ == "__main__":
    unittest.main()
