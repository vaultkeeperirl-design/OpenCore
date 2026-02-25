import unittest
from unittest.mock import MagicMock, patch
from opencore.core.agent import Agent
from opencore.config import settings
import os

class TestAgentMemory(unittest.TestCase):
    def setUp(self):
        # Reset settings
        settings.max_history = 100
        self.agent = Agent("TestBot", "Tester", "System Prompt")

    def tearDown(self):
        settings.max_history = 100

    def test_default_max_history(self):
        self.assertEqual(settings.max_history, 100)
        # Add 101 user messages (total 102 with system prompt)
        for i in range(101):
            self.agent.add_message("user", f"msg {i}")

        self.assertEqual(len(self.agent.messages), 102) # 1 sys + 101 user

        self.agent._prune_messages()

        # Should keep system + last 100 messages = 101 total
        self.assertEqual(len(self.agent.messages), 101)
        self.assertEqual(self.agent.messages[0]["role"], "system")
        # msg 0 should be pruned, msg 1 should be first user message
        self.assertEqual(self.agent.messages[1]["content"], "msg 1")

    def test_pruning_custom_limit(self):
        settings.max_history = 5
        # Add 10 user messages (total 11)
        for i in range(10):
            self.agent.add_message("user", f"msg {i}")

        # 1 sys + 10 user = 11 messages. Limit 5.
        # prune -> 1 sys + last 5 user = 6 messages.

        self.agent._prune_messages()
        self.assertEqual(len(self.agent.messages), 6)
        self.assertEqual(self.agent.messages[0]["role"], "system")
        self.assertEqual(self.agent.messages[1]["content"], "msg 5")
        self.assertEqual(self.agent.messages[-1]["content"], "msg 9")

    def test_orphaned_tool_pruning(self):
        # Scenario where pruning leaves a tool output without its calling assistant message
        settings.max_history = 1

        # 1. System
        # 2. User: call tool
        # 3. Assistant: tool call
        # 4. Tool: result

        self.agent.add_message("user", "use tool")
        self.agent.add_message("assistant", "calling tool...")
        self.agent.add_message("tool", "tool result")

        # Current state: [Sys, User, Asst, Tool] (4 msgs)
        # Limit 1.
        # Logic: Keep last 1 message -> [Tool]
        # Result before orphan check: [Sys, Tool]
        # Orphan check should remove Tool because it's the first message after system and role is tool

        self.agent._prune_messages()

        self.assertEqual(len(self.agent.messages), 1)
        self.assertEqual(self.agent.messages[0]["role"], "system")

    def test_max_history_zero_pruning(self):
        settings.max_history = 0
        self.agent.add_message("user", "Hello")
        self.agent.add_message("assistant", "Hi there")

        self.agent._prune_messages()

        self.assertEqual(len(self.agent.messages), 1)
        self.assertEqual(self.agent.messages[0]["role"], "system")

if __name__ == '__main__':
    unittest.main()
