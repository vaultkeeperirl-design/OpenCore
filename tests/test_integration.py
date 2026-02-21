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

    @patch("opencore.core.agent.completion")
    def test_swarm_delegation_flow(self, mock_completion):
        swarm = Swarm("Manager")
        swarm.create_agent("Coder", "Developer", "Code stuff")

        # Define side effect function to simulate conversation flow
        def completion_side_effect(*args, **kwargs):
            messages = kwargs.get("messages")
            # Check who is calling based on system prompt in messages[0]
            system_content = messages[0]["content"]

            if "Manager" in system_content:
                last_msg = messages[-1]

                # Check if this is the first user message or a tool response
                if last_msg["role"] == "user":
                    # First call: Manager decides to delegate
                    msg = MagicMock()
                    msg.content = None
                    tc = MagicMock()
                    tc.id = "call_1"
                    tc.function.name = "delegate_task"
                    tc.function.arguments = '{"to_agent": "Coder", "task": "Code X"}'
                    msg.tool_calls = [tc]

                    resp = MagicMock()
                    resp.choices = [MagicMock(message=msg)]
                    return resp

                elif last_msg["role"] == "tool":
                    # Second call: Manager receives tool output and finishes
                    msg = MagicMock()
                    msg.content = "Done."
                    msg.tool_calls = None
                    resp = MagicMock()
                    resp.choices = [MagicMock(message=msg)]
                    return resp

            elif "Coder" in system_content:
                # Coder simply replies
                msg = MagicMock()
                msg.content = "Code written."
                msg.tool_calls = None
                resp = MagicMock()
                resp.choices = [MagicMock(message=msg)]
                return resp

            # Fallback
            msg = MagicMock()
            msg.content = "Error."
            msg.tool_calls = None
            resp = MagicMock()
            resp.choices = [MagicMock(message=msg)]
            return resp

        mock_completion.side_effect = completion_side_effect

        print("Starting chat...")
        response = swarm.chat("Code X")
        print(f"Response: {response}")

        # Verify calls were made
        # 1. Manager -> delegate
        # 2. Coder -> responds
        # 3. Manager -> final response
        self.assertEqual(mock_completion.call_count, 3)
        self.assertEqual(response, "Done.")

if __name__ == "__main__":
    unittest.main()
