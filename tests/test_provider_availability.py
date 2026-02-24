import unittest
from unittest.mock import patch
import os
from opencore.llm.factory import is_provider_available, get_available_model_list
from opencore.core.swarm import Swarm
from opencore.config import settings

class TestProviderAvailability(unittest.TestCase):
    def setUp(self):
        # Clear env vars before each test to ensure isolation
        self.env_patcher = patch.dict(os.environ, {}, clear=True)
        self.env_patcher.start()
        settings.reload()

    def tearDown(self):
        self.env_patcher.stop()

    def test_is_provider_available(self):
        # OpenAI
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            self.assertTrue(is_provider_available("openai/gpt-4o"))
            self.assertTrue(is_provider_available("gpt-4o"))

        self.assertFalse(is_provider_available("openai/gpt-4o"))

        # Ollama
        with patch.dict(os.environ, {"OLLAMA_API_BASE": "http://localhost:11434"}):
            self.assertTrue(is_provider_available("ollama/llama3"))

        self.assertFalse(is_provider_available("ollama/llama3"))

    def test_create_agent_validation(self):
        # Setup Swarm with mocked key
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            settings.reload()
            swarm = Swarm()

            # Valid model
            result = swarm.create_agent("Agent1", "Role", "Inst", model="openai/gpt-4o")
            self.assertIn("created successfully", result)

            # Invalid model (no key for anthropic)
            result = swarm.create_agent("Agent2", "Role", "Inst", model="anthropic/claude-3")
            self.assertIn("Error: Provider for model 'anthropic/claude-3' is not configured", result)

    def test_tool_schema_description(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test", "ANTHROPIC_API_KEY": "sk-ant-test"}):
             settings.reload()
             swarm = Swarm()
             # Manager created in init
             agent = swarm.get_agent("Manager")

             # Check schema
             create_agent_tool = next(t for t in agent.tool_definitions if t["function"]["name"] == "create_agent")
             desc = create_agent_tool["function"]["parameters"]["properties"]["model"]["description"]

             self.assertIn("openai/gpt-4o", desc)
             self.assertIn("anthropic/claude-3-opus", desc)
