import unittest
import os
import shutil
from unittest.mock import patch
from opencore.cli.onboard import run_onboarding


class TestOnboarding(unittest.TestCase):
    def setUp(self):
        # Backup .env if exists
        if os.path.exists(".env"):
            shutil.move(".env", ".env.bak")

    def tearDown(self):
        # Remove generated .env
        if os.path.exists(".env"):
            os.remove(".env")
        # Restore backup
        if os.path.exists(".env.bak"):
            shutil.move(".env.bak", ".env")

    @patch('opencore.cli.onboard.verify_connection')
    @patch('builtins.input')
    def test_run_onboarding_openai(self, mock_input, mock_verify):
        mock_verify.return_value = (True, "Mock Success")
        # Sequence of inputs:
        # 1. LLM Provider (1: OpenAI) -> "1"
        # 2. API Key -> "sk-test-key"
        mock_input.side_effect = [
            "1",           # choice (OpenAI)
            "sk-test-key",  # api_key
        ]

        run_onboarding()

        self.assertTrue(os.path.exists(".env"))
        with open(".env", "r") as f:
            content = f.read()

        self.assertIn("APP_ENV=production", content)
        self.assertIn("HOST=127.0.0.1", content)
        self.assertIn("PORT=8000", content)
        self.assertIn("LLM_MODEL=gpt-4o", content)
        self.assertIn("OPENAI_API_KEY=sk-test-key", content)

    @patch('opencore.cli.onboard.verify_connection')
    @patch('builtins.input')
    def test_run_onboarding_grok(self, mock_input, mock_verify):
        mock_verify.return_value = (True, "Mock Success")
        # Sequence of inputs:
        # 1. LLM Provider (6: Grok) -> "6" (was 5)
        # 2. API Key -> "xai-test-key"
        mock_input.side_effect = [
            "6",           # choice (Grok)
            "xai-test-key",  # api_key
        ]

        run_onboarding()

        self.assertTrue(os.path.exists(".env"))
        with open(".env", "r") as f:
            content = f.read()

        self.assertIn("APP_ENV=production", content)
        self.assertIn("LLM_MODEL=xai/grok-2-vision-1212", content)
        self.assertIn("XAI_API_KEY=xai-test-key", content)

    @patch('opencore.cli.onboard.verify_connection')
    @patch('builtins.input')
    def test_run_onboarding_ollama(self, mock_input, mock_verify):
        mock_verify.return_value = (True, "Mock Success")
        # Sequence of inputs:
        # 1. Choice -> "3" (Ollama)
        # 2. Model -> "ollama/qwen"
        # 3. Base URL -> "http://ollama:11434"
        mock_input.side_effect = [
            "3",
            "ollama/qwen",
            "http://ollama:11434",
        ]

        run_onboarding()

        with open(".env", "r") as f:
            content = f.read()

        self.assertIn("APP_ENV=production", content)
        self.assertIn("LLM_MODEL=ollama/qwen", content)
        self.assertIn("OLLAMA_API_BASE=http://ollama:11434", content)

    @patch('opencore.cli.onboard.verify_connection')
    @patch('builtins.input')
    def test_run_onboarding_gemini_success(self, mock_input, mock_verify):
        mock_verify.return_value = (True, "Mock Success")
        mock_input.side_effect = ["4", "gemini-key"]

        run_onboarding()

        with open(".env", "r") as f:
            content = f.read()
        self.assertIn("LLM_MODEL=gemini/gemini-2.0-flash", content)
        self.assertIn("GEMINI_API_KEY=gemini-key", content)

    @patch('opencore.cli.onboard.verify_connection')
    @patch('builtins.input')
    def test_run_onboarding_gemini_fail_skip(self, mock_input, mock_verify):
        mock_verify.return_value = (False, "Fail")
        mock_input.side_effect = ["4", "gemini-key", "n"]

        run_onboarding()

        with open(".env", "r") as f:
            content = f.read()
        self.assertIn("LLM_MODEL=gemini/gemini-2.0-flash", content)
        self.assertIn("GEMINI_API_KEY=gemini-key", content)


if __name__ == "__main__":
    unittest.main()
