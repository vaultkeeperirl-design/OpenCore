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

    @patch('builtins.input')
    def test_run_onboarding_openai(self, mock_input):
        # Sequence of inputs:
        # 1. Environment (default: production) -> "development"
        # 2. Host (default) -> ""
        # 3. Port (default) -> ""
        # 4. LLM Provider (1: OpenAI) -> "1"
        # 5. Model name -> "gpt-4o-test"
        # 6. API Key -> "sk-test-key"
        # 7. Heartbeat -> ""
        mock_input.side_effect = [
            "development", # app_env
            "",            # host
            "",            # port
            "1",           # choice (OpenAI)
            "gpt-4o-test", # model
            "sk-test-key", # api_key
            ""             # heartbeat
        ]

        run_onboarding()

        self.assertTrue(os.path.exists(".env"))
        with open(".env", "r") as f:
            content = f.read()

        self.assertIn("APP_ENV=development", content)
        self.assertIn("HOST=0.0.0.0", content)
        self.assertIn("PORT=8000", content)
        self.assertIn("LLM_MODEL=gpt-4o-test", content)
        self.assertIn("OPENAI_API_KEY=sk-test-key", content)

    @patch('builtins.input')
    def test_run_onboarding_ollama(self, mock_input):
        # Sequence of inputs:
        # 1. Environment -> ""
        # 2. Host -> ""
        # 3. Port -> ""
        # 4. Choice -> "3" (Ollama)
        # 5. Model -> "ollama/qwen"
        # 6. Base URL -> "http://ollama:11434"
        # 7. Heartbeat -> ""
        mock_input.side_effect = [
            "",
            "",
            "",
            "3",
            "ollama/qwen",
            "http://ollama:11434",
            ""
        ]

        run_onboarding()

        with open(".env", "r") as f:
            content = f.read()

        self.assertIn("APP_ENV=production", content)
        self.assertIn("LLM_MODEL=ollama/qwen", content)
        self.assertIn("OLLAMA_API_BASE=http://ollama:11434", content)

if __name__ == "__main__":
    unittest.main()
