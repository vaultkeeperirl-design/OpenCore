import unittest
import json
from unittest.mock import MagicMock, patch
from opencore.core.agent import Agent
from opencore.llm.base import LLMResponse

class TestAgent(unittest.TestCase):
    def test_agent_initialization(self):
        agent = Agent("TestBot", "Tester", "You test things.")
        self.assertEqual(agent.name, "TestBot")
        # System message is added
        self.assertEqual(len(agent.messages), 1)
        self.assertEqual(agent.messages[0]["content"], "You are TestBot, a Tester. You test things.")

    @patch("opencore.core.agent.get_llm_provider")
    def test_agent_think_exception(self, mock_get_provider):
        # Simulate a generic exception
        mock_provider = MagicMock()
        mock_provider.chat.side_effect = Exception("Some random error")
        mock_get_provider.return_value = mock_provider

        agent = Agent("TestBot", "Tester", "You test things.")
        response = agent.think()
        self.assertTrue("Error during thought process" in response)
        self.assertTrue("Some random error" in response)

    @patch("opencore.core.agent.get_llm_provider")
    def test_agent_think_xai_exception(self, mock_get_provider):
        # Simulate the specific xAI exception (or general auth error now handled by factory/provider)
        mock_provider = MagicMock()
        mock_provider.chat.side_effect = Exception('Incorrect API key provided')
        mock_get_provider.return_value = mock_provider

        agent = Agent("TestBot", "Tester", "You test things.")
        response = agent.think()

        expected_msg = "SYSTEM ALERT: LLM configuration invalid or missing (Incorrect API key provided). Please configure your provider in Settings."
        self.assertEqual(response, expected_msg)

    @patch("opencore.core.agent.get_llm_provider")
    def test_agent_chat_mock(self, mock_get_provider):
        mock_provider = MagicMock()
        mock_provider.chat.return_value = LLMResponse(content="Hello there!", tool_calls=None)
        mock_get_provider.return_value = mock_provider

        agent = Agent("TestBot", "Tester", "You test things.")
        response = agent.chat("Hi")

        self.assertEqual(response, "Hello there!")
        # Messages: System, User, Assistant
        self.assertEqual(len(agent.messages), 3)
        self.assertEqual(agent.messages[1]["role"], "user")
        self.assertEqual(agent.messages[2]["role"], "assistant")

    def test_normalize_tool_call_dict(self):
        agent = Agent("TestBot", "Tester", "You test things.")
        tool_call = {
            "id": "call_123",
            "function": {
                "name": "test_tool",
                "arguments": '{"arg": "value"}'
            }
        }
        tid, name, args = agent._normalize_tool_call(tool_call)
        self.assertEqual(tid, "call_123")
        self.assertEqual(name, "test_tool")
        self.assertEqual(args, {"arg": "value"})

    def test_normalize_tool_call_object(self):
        agent = Agent("TestBot", "Tester", "You test things.")

        class MockToolCall:
            def __init__(self):
                self.id = "call_456"
                self.function = MagicMock()
                self.function.name = "test_tool_obj"
                self.function.arguments = '{"arg": "value2"}'

        tool_call = MockToolCall()
        tid, name, args = agent._normalize_tool_call(tool_call)
        self.assertEqual(tid, "call_456")
        self.assertEqual(name, "test_tool_obj")
        self.assertEqual(args, {"arg": "value2"})
