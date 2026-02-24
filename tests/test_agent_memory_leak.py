import unittest
from unittest.mock import patch, MagicMock
from opencore.core.agent import Agent
from opencore.llm.base import LLMResponse


class TestAgentMemoryLeak(unittest.TestCase):
    def test_message_history_unbounded(self):
        """Test that adding messages increases the history size."""
        agent = Agent(
            name="TestAgent",
            role="Tester",
            system_prompt="System Prompt"
        )

        # Add 150 messages manually
        for i in range(150):
            agent.add_message("user", f"Message {i}")

        # Verify it has 151 messages (1 system + 150 user)
        self.assertEqual(len(agent.messages), 151)

    @patch("opencore.core.agent.get_llm_provider")
    def test_message_history_truncation(self, mock_get_provider):
        """Test that think() truncates the message history."""
        # Mock provider
        mock_provider = MagicMock()
        mock_provider.chat.return_value = LLMResponse(
            content="I am thinking.",
            tool_calls=None
        )
        mock_get_provider.return_value = mock_provider

        agent = Agent(
            name="TestAgent",
            role="Tester",
            system_prompt="System Prompt"
        )

        # Add 150 messages manually (0 to 149)
        for i in range(150):
            agent.add_message("user", f"Message {i}")

        # Call think() which should trigger pruning
        agent.think()

        # Logic:
        # Initial: 1 (sys) + 150 (user) = 151
        # Pruning (MAX=100): Keep 1 (sys) + last 100 (user) = 101
        # Think response: +1 (assistant) = 102

        self.assertEqual(len(agent.messages), 102)

        # Check system prompt is preserved
        self.assertTrue("System Prompt" in agent.messages[0]["content"])

        # Check that the messages after system prompt are the most recent ones
        # The last user message added was "Message 149"
        # Since 'assistant' response is last,
        # the one before it is the last user message
        self.assertEqual(agent.messages[-2]["content"], "Message 149")

        # The first retained user message should be Message 50
        # (since we keep last 100 from 0..149, i.e., 50..149)
        # Message at index 1 should be "Message 50"
        self.assertEqual(agent.messages[1]["content"], "Message 50")
