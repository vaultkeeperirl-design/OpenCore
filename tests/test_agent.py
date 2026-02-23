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
        # Simulate a generic exception
        mock_completion.side_effect = Exception("Some random error")

        agent = Agent("TestBot", "Tester", "You test things.")
        with patch("opencore.core.agent.logger") as mock_logger:
            response = agent.think()
            self.assertTrue("Error during thought process" in response)
            self.assertTrue("Some random error" in response)
            # Should call exception for unknown errors
            mock_logger.exception.assert_called_once()

    @patch("opencore.core.agent.completion")
    def test_agent_think_xai_exception(self, mock_completion):
        # Simulate the specific xAI exception
        error_msg = 'litellm.BadRequestError: XaiException - {"code":"Client specified an invalid argument","error":"Incorrect API key provided: gs***UQ. You can obtain an API key from https://console.x.ai."}'
        mock_completion.side_effect = Exception(error_msg)

        agent = Agent("TestBot", "Tester", "You test things.")

        with patch("opencore.core.agent.logger") as mock_logger:
            response = agent.think()

            expected_msg = "SYSTEM ALERT: LLM configuration invalid or missing. Please configure your provider in Settings."
            self.assertEqual(response, expected_msg)

            # Verify we logged a warning but NOT an exception (stack trace)
            mock_logger.warning.assert_called_once()
            mock_logger.exception.assert_not_called()

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
