import unittest
from unittest.mock import MagicMock
from opencore.core.swarm import Swarm
from opencore.core.agent import Agent

class TestAttachments(unittest.TestCase):
    def test_image_attachment(self):
        swarm = Swarm()
        agent = swarm.agents["Manager"]

        # Mock think to avoid LLM call
        agent.think = MagicMock(return_value="Mock response")

        attachments = [
            {"name": "test.png", "type": "image/png", "content": "data:image/png;base64,1234"}
        ]

        # Call chat
        swarm.chat("Look at this", attachments=attachments)

        # Verify
        last_message = agent.messages[-1]
        print(f"DEBUG: Last message content: {last_message['content']}")

        self.assertEqual(last_message["role"], "user")
        self.assertIsInstance(last_message["content"], list)
        self.assertEqual(len(last_message["content"]), 2)

        # Check text part
        self.assertEqual(last_message["content"][0]["type"], "text")
        self.assertIn("Look at this", last_message["content"][0]["text"])

        # Check image part
        self.assertEqual(last_message["content"][1]["type"], "image_url")
        self.assertEqual(last_message["content"][1]["image_url"]["url"], "data:image/png;base64,1234")

    def test_text_attachment(self):
        swarm = Swarm()
        agent = swarm.agents["Manager"]
        agent.think = MagicMock(return_value="Mock response")

        attachments = [
            {"name": "notes.txt", "type": "text/plain", "content": "Hello World"}
        ]

        swarm.chat("Read this", attachments=attachments)

        last_message = agent.messages[-1]
        self.assertEqual(last_message["role"], "user")
        self.assertIsInstance(last_message["content"], list)
        # Should be 1 item: text block with appended content
        self.assertEqual(len(last_message["content"]), 1)

        self.assertEqual(last_message["content"][0]["type"], "text")
        self.assertIn("Read this", last_message["content"][0]["text"])
        self.assertIn("[Attachment: notes.txt]", last_message["content"][0]["text"])
        self.assertIn("Hello World", last_message["content"][0]["text"])

if __name__ == "__main__":
    unittest.main()
