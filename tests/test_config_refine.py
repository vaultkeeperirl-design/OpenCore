import unittest
from unittest.mock import patch, MagicMock
from opencore.config import Settings

class TestConfigRefine(unittest.TestCase):
    @patch("opencore.config.load_dotenv")
    @patch("opencore.config.get_qwen_credentials")
    @patch("opencore.config.get_auth_status")
    @patch("os.getenv")
    def test_model_normalization_on_reload(self, mock_getenv, mock_auth_status, mock_qwen, mock_load_dotenv):
        # Mock dependencies
        mock_qwen.return_value = None
        mock_auth_status.return_value = {"google": False}

        # Test Case 1: Deprecated Gemini Model
        mock_getenv.side_effect = lambda key, default=None: "gemini/gemini-1.5-flash-latest" if key == "LLM_MODEL" else default
        settings = Settings()
        self.assertEqual(settings.llm_model, "gemini/gemini-2.0-flash")

        # Test Case 2: Deprecated Grok Model
        mock_getenv.side_effect = lambda key, default=None: "openai/grok-2-1212" if key == "LLM_MODEL" else default
        settings = Settings()
        self.assertEqual(settings.llm_model, "xai/grok-2-vision-1212")

        # Test Case 3: Valid Model (No Change)
        mock_getenv.side_effect = lambda key, default=None: "gpt-4o" if key == "LLM_MODEL" else default
        settings = Settings()
        self.assertEqual(settings.llm_model, "gpt-4o")

    @patch("opencore.config.set_key")
    @patch("opencore.config.load_dotenv")
    @patch("opencore.config.get_qwen_credentials")
    @patch("opencore.config.get_auth_status")
    @patch("os.getenv")
    def test_model_normalization_on_update(self, mock_getenv, mock_auth_status, mock_qwen, mock_load_dotenv, mock_set_key):
        # Mock dependencies
        mock_qwen.return_value = None
        mock_auth_status.return_value = {"google": False}

        def getenv_side_effect(key, default=None):
            if key == "LLM_MODEL":
                return "gpt-4o"
            if key == "PORT":
                return "8000"
            if key == "HEARTBEAT_INTERVAL":
                return "3600"
            return default

        mock_getenv.side_effect = getenv_side_effect

        settings = Settings()

        # Test Update with Deprecated Gemini Model
        settings.update_env({"LLM_MODEL": "gemini/gemini-1.5-flash-latest"})
        mock_set_key.assert_any_call(".env", "LLM_MODEL", "gemini/gemini-2.0-flash")

        # Test Update with Deprecated Grok Model
        settings.update_env({"LLM_MODEL": "openai/grok-2-1212"})
        mock_set_key.assert_any_call(".env", "LLM_MODEL", "xai/grok-2-vision-1212")

if __name__ == "__main__":
    unittest.main()
