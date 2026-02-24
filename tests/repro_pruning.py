
import unittest
from opencore.core.agent import Agent

class TestAgentPruning(unittest.TestCase):
    def test_pruning_breaks_tool_chain(self):
        agent = Agent("Test", "Tester", "System prompt")

        # Manually populate history to limit
        # Pattern: User, Assistant (tool), Tool
        # We want to arrange it so that pruning cuts off the Assistant but leaves the Tool.

        # Max history is 100.
        # preserved system prompt is 1.

        # Let's fill with 99 filler messages.
        for i in range(99):
             agent.add_message("user", f"filler {i}")

        # Now we are at 1 + 99 = 100 messages.

        # Add a tool chain at the "boundary"
        # We need to add enough messages so that the next prune slices right between a tool call and result.

        # _prune_messages logic:
        # if len > 101:
        #    keep system
        #    keep last 100

        # So if we have 102 messages.
        # It keeps msg[0] and msg[-100:].
        # Meaning msg[1] is dropped.

        # Let's verify what happens when msg[1] is a tool call and msg[2] is a tool result.

        # Clear filler, let's be precise.
        agent.messages = [{"role": "system", "content": "sys"}]

        # We want msg[1] to be Assistant(tool_call)
        # msg[2] to be Tool(result)
        # And we want them to be the "oldest" messages that are candidates for pruning.

        # msg[1]
        agent.messages.append({
            "role": "assistant",
            "content": None,
            "tool_calls": [{"id": "call_1", "function": {"name": "test", "arguments": "{}"}}]
        })

        # msg[2]
        agent.messages.append({
            "role": "tool",
            "tool_call_id": "call_1",
            "content": "result"
        })

        # Now we add filler to push these to the "chopping block".
        # We need total length to exceed 101.
        # Currently length is 3.
        # We need 99 more messages to reach 102.

        for i in range(99):
            agent.messages.append({"role": "user", "content": f"filler {i}"})

        # Total length: 1 (sys) + 1 (asst) + 1 (tool) + 99 (filler) = 102.

        self.assertEqual(len(agent.messages), 102)
        self.assertEqual(agent.messages[1]["role"], "assistant") # The one to be dropped
        self.assertEqual(agent.messages[2]["role"], "tool")      # The one to be kept (initially)

        # Trigger pruning
        agent._prune_messages()

        # Expected:
        # Original length: 102
        # Naive prune to 101 (removing msg[1] which was Assistant).
        # msg[1] became Tool.
        # New prune logic should detect msg[1] is Tool and remove it.
        # So final length should be 100.

        self.assertEqual(len(agent.messages), 100)

        # Check first message after system prompt
        first_msg = agent.messages[1]

        # It should NOT be a tool message. It should be the first "filler" user message.
        self.assertNotEqual(first_msg["role"], "tool")
        self.assertEqual(first_msg["content"], "filler 0")

        print("Confirmed: Pruning correctly removed orphaned tool message.")

if __name__ == '__main__':
    unittest.main()
