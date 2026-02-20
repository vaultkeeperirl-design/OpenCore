import unittest
from unittest.mock import MagicMock
from opencore.core.agent import Agent

class TestAgent(unittest.TestCase):
    def test_agent_initialization(self):
        agent = Agent("TestBot", "Tester", "You test things.")
        self.assertEqual(agent.name, "TestBot")
        self.assertEqual(len(agent.messages), 1)
        self.assertEqual(agent.messages[0]["content"], "You are TestBot, a Tester. You test things.")

    def test_agent_think_no_api_key(self):
        # Ensure no API key is present
        agent = Agent("TestBot", "Tester", "You test things.")
        agent.client = None
        response = agent.think()
        self.assertEqual(response, "Error: No API Key provided.")

    def test_agent_chat_mock(self):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Hello there!"
        mock_message.tool_calls = None
        mock_response.choices = [MagicMock(message=mock_message)]
        mock_client.chat.completions.create.return_value = mock_response

        agent = Agent("TestBot", "Tester", "You test things.", client=mock_client)
        response = agent.chat("Hi")

        self.assertEqual(response, "Hello there!")
        self.assertEqual(len(agent.messages), 3) # System, User, Assistant
        self.assertEqual(agent.messages[1]["role"], "user")
        self.assertEqual(agent.messages[2]["role"], "assistant")

if __name__ == "__main__":
    unittest.main()
