import unittest
from unittest.mock import patch, MagicMock
from opencore.core.agent import Agent
from opencore.core.swarm import Swarm

class TestAgentProviders(unittest.TestCase):
    @patch("opencore.core.agent.completion")
    def test_agent_uses_custom_model(self, mock_completion):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hello from Gemini"
        mock_response.choices[0].message.tool_calls = None
        mock_completion.return_value = mock_response

        # Initialize agent with a Vertex AI model
        agent = Agent("GeminiAgent", "Tester", "Test prompt", model="vertex_ai/gemini-pro")

        # Act
        response = agent.chat("Hi")

        # Assert
        self.assertEqual(response, "Hello from Gemini")
        mock_completion.assert_called_once()
        call_args = mock_completion.call_args
        self.assertEqual(call_args.kwargs["model"], "vertex_ai/gemini-pro")

    @patch("opencore.config.settings.llm_model", None)
    @patch("opencore.core.agent.completion")
    def test_swarm_respects_model_config(self, mock_completion):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hello from Ollama"
        mock_response.choices[0].message.tool_calls = None
        mock_completion.return_value = mock_response

        # Initialize Swarm
        swarm = Swarm(default_model="ollama/llama3")

        # Verify main agent model
        self.assertEqual(swarm.agents["Manager"].model, "ollama/llama3")

        # Create sub-agent with specific model
        swarm.create_agent("SubAgent", "Worker", "Work", model="bedrock/anthropic.claude-v2")
        self.assertEqual(swarm.agents["SubAgent"].model, "bedrock/anthropic.claude-v2")

        # Chat with main agent
        swarm.chat("Hi")

        # Verify litellm was called with main agent's model
        call_args = mock_completion.call_args
        self.assertEqual(call_args.kwargs["model"], "ollama/llama3")

    @patch("opencore.core.agent.completion")
    def test_litellm_completion_called_correctly(self, mock_completion):
        # Test that messages are passed correctly
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test Response"
        mock_response.choices[0].message.tool_calls = None
        mock_completion.return_value = mock_response

        agent = Agent("TestAgent", "Tester", "System Prompt", model="gpt-4o")
        agent.chat("User Message")

        mock_completion.assert_called_once()
        kwargs = mock_completion.call_args.kwargs
        messages = kwargs["messages"]

        # Check message structure
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[1]["role"], "user")
        self.assertEqual(messages[1]["content"], "User Message")
