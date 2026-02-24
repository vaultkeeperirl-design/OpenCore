import unittest
from unittest.mock import patch, MagicMock
from opencore.core.agent import Agent
from opencore.core.swarm import Swarm
from opencore.llm.base import LLMResponse

class TestAgentProviders(unittest.TestCase):
    @patch("opencore.core.agent.get_llm_provider")
    def test_agent_uses_custom_model(self, mock_get_provider):
        # Setup mock response
        mock_provider = MagicMock()
        mock_provider.chat.return_value = LLMResponse(content="Hello from Gemini", tool_calls=None)
        mock_get_provider.return_value = mock_provider

        # Initialize agent with a Vertex AI model
        agent = Agent("GeminiAgent", "Tester", "Test prompt", model="vertex_ai/gemini-pro")

        # Act
        response = agent.chat("Hi")

        # Assert
        self.assertEqual(response, "Hello from Gemini")
        mock_get_provider.assert_called_once_with("vertex_ai/gemini-pro", is_custom_model=False)

    @patch("opencore.core.swarm.is_provider_available", return_value=True)
    @patch("opencore.config.settings.llm_model", None)
    @patch("opencore.core.agent.get_llm_provider")
    def test_swarm_respects_model_config(self, mock_get_provider, mock_is_provider_avail):
        # Setup mock response
        mock_provider = MagicMock()
        mock_provider.chat.return_value = LLMResponse(content="Hello from Ollama", tool_calls=None)
        mock_get_provider.return_value = mock_provider

        # Initialize Swarm
        swarm = Swarm(default_model="ollama/llama3")

        # Verify main agent model
        self.assertEqual(swarm.agents["Manager"].model, "ollama/llama3")

        # Create sub-agent with specific model
        swarm.create_agent("SubAgent", "Worker", "Work", model="bedrock/anthropic.claude-v2")
        self.assertEqual(swarm.agents["SubAgent"].model, "bedrock/anthropic.claude-v2")

        # Chat with main agent
        swarm.chat("Hi")

        # Verify get_llm_provider was called with main agent's model
        mock_get_provider.assert_called_with("ollama/llama3", is_custom_model=False)

    @patch("opencore.core.agent.get_llm_provider")
    def test_provider_chat_called_correctly(self, mock_get_provider):
        # Test that messages are passed correctly
        mock_provider = MagicMock()
        mock_provider.chat.return_value = LLMResponse(content="Test Response", tool_calls=None)
        mock_get_provider.return_value = mock_provider

        agent = Agent("TestAgent", "Tester", "System Prompt", model="gpt-4o")
        agent.chat("User Message")

        mock_provider.chat.assert_called_once()
        kwargs = mock_provider.chat.call_args.kwargs
        messages = kwargs["messages"]

        # Check message structure
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[1]["role"], "user")
        self.assertEqual(messages[1]["content"], "User Message")
