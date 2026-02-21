import unittest
from unittest.mock import MagicMock, patch
from opencore.core.agent import Agent

class TestAgent(unittest.TestCase):
    def test_agent_initialization(self):
        agent = Agent("TestBot", "Tester", "You test things.")
        self.assertEqual(agent.name, "TestBot")
        # System message is added
        self.assertEqual(len(agent.messages), 1)
        self.assertEqual(agent.messages[0]["content"], "You are TestBot, a Tester. You test things.")

    @patch("opencore.core.agent.completion")
    def test_agent_think_exception(self, mock_completion):
        # Simulate an exception (e.g., missing API key)
        mock_completion.side_effect = Exception("API Key missing")

        agent = Agent("TestBot", "Tester", "You test things.")
        response = agent.think()
        self.assertTrue("Error during thought process" in response)
        self.assertTrue("API Key missing" in response)

    @patch("opencore.core.agent.completion")
    def test_agent_chat_mock(self, mock_completion):
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Hello there!"
        mock_message.tool_calls = None
        mock_response.choices = [MagicMock(message=mock_message)]
        mock_completion.return_value = mock_response

        agent = Agent("TestBot", "Tester", "You test things.")
        response = agent.chat("Hi")

        self.assertEqual(response, "Hello there!")
        # Messages: System, User, Assistant
        self.assertEqual(len(agent.messages), 3)
        self.assertEqual(agent.messages[1]["role"], "user")
        self.assertEqual(agent.messages[2]["role"], "assistant")
