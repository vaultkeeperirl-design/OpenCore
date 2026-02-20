import unittest
from unittest.mock import MagicMock, patch
from opencore.core.swarm import Swarm
from opencore.interface.api import app
from fastapi.testclient import TestClient

client = TestClient(app)

class TestIntegration(unittest.TestCase):
    def test_api_chat_flow(self):
        with patch("opencore.interface.api.swarm") as mock_swarm:
            mock_swarm.chat.return_value = "Hello from Manager!"
            mock_swarm.agents = {"Manager": MagicMock()}

            response = client.post("/chat", json={"message": "Hi"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["response"], "Hello from Manager!")

    def test_swarm_delegation_flow(self):
        swarm = Swarm("Manager")

        swarm.create_agent("Coder", "Developer", "Code stuff")
        coder = swarm.agents["Coder"]
        coder.client = MagicMock()
        coder_response = MagicMock()

        # Setup Coder response
        coder_msg = MagicMock()
        coder_msg.content = "Code written."
        coder_msg.tool_calls = None
        coder_response.choices = [MagicMock(message=coder_msg)]

        coder.client.chat.completions.create.return_value = coder_response

        manager = swarm.agents["Manager"]
        manager.client = MagicMock()

        # Tool call response
        tool_call_msg = MagicMock()
        tool_call_msg.content = None

        # Correctly setup tool_call mock
        tool_call = MagicMock()
        tool_call.id = "call_1"
        tool_call.function.name = "delegate_task"
        tool_call.function.arguments = '{"to_agent": "Coder", "task": "Code X"}'

        tool_call_msg.tool_calls = [tool_call]

        # Final response
        final_msg = MagicMock()
        final_msg.content = "Done."
        final_msg.tool_calls = None

        # Set side effect
        manager.client.chat.completions.create.side_effect = [
            MagicMock(choices=[MagicMock(message=tool_call_msg)]),
            MagicMock(choices=[MagicMock(message=final_msg)])
        ]

        print("Starting chat...")
        response = swarm.chat("Code X")
        print(f"Response: {response}")

        print("Manager calls:", manager.client.chat.completions.create.call_count)
        print("Coder calls:", coder.client.chat.completions.create.call_count)

        # Verify Coder was called
        coder.client.chat.completions.create.assert_called()

if __name__ == "__main__":
    unittest.main()
