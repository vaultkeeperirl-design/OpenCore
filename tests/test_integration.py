import unittest
from unittest.mock import MagicMock, patch
from opencore.core.swarm import Swarm
from opencore.interface.api import app
from opencore.llm.base import LLMResponse, ToolCall, ToolCallFunction
from fastapi.testclient import TestClient

client = TestClient(app)


class TestIntegration(unittest.TestCase):
    def test_api_chat_flow(self):
        with patch("opencore.interface.api.swarm") as mock_swarm:
            mock_swarm.chat.return_value = "Hello from Manager!"
            mock_swarm.agents = {"Manager": MagicMock()}
            mock_swarm.get_graph_data.return_value = {"nodes": [], "edges": []}

            response = client.post("/chat", json={"message": "Hi"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json()["response"],
                "Hello from Manager!"
            )

    @patch("opencore.core.agent.get_llm_provider")
    def test_swarm_delegation_flow(self, mock_get_provider):
        # We need distinct mock providers for each agent if we want state?
        # Or just simulate behavior based on inputs.

        # Swarm setup
        # Note: Swarm calls settings.llm_model during init
        with patch("opencore.config.settings.llm_model", "gpt-4o"):
            swarm = Swarm("Manager")
            swarm.create_agent("Coder", "Developer", "Code stuff")

        # Mock provider instance
        mock_provider = MagicMock()
        mock_get_provider.return_value = mock_provider

        # Define side effect function to simulate conversation flow
        def chat_side_effect(messages, tools=None):
            # Check who is calling based on system prompt in messages[0]
            system_content = messages[0]["content"]

            # 1. Manager Logic
            if "Manager" in system_content:
                last_msg = messages[-1]

                # First call: User asks to code -> Manager delegates
                if last_msg["role"] == "user":
                    return LLMResponse(
                        content=None,
                        tool_calls=[
                            ToolCall(
                                id="call_1",
                                function=ToolCallFunction(
                                    name="delegate_task",
                                    arguments='{"to_agent": "Coder", "task": "Code X"}'
                                )
                            )
                        ]
                    )

                # Second call: Tool output (from Coder) -> Manager finishes
                elif last_msg["role"] == "tool":
                    return LLMResponse(
                        content="Done.",
                        tool_calls=None
                    )

            # 2. Coder Logic
            elif "Coder" in system_content:
                return LLMResponse(
                    content="Code written.",
                    tool_calls=None
                )

            # Fallback
            return LLMResponse(content="Error.", tool_calls=None)

        mock_provider.chat.side_effect = chat_side_effect

        print("Starting chat...")
        response = swarm.chat("Code X")
        print(f"Response: {response}")

        # Verify calls were made
        # 1. Manager -> delegate
        # 2. Coder -> responds (called via tool execution inside Manager)
        # 3. Manager -> final response
        self.assertEqual(mock_provider.chat.call_count, 3)
        self.assertEqual(response, "Done.")


if __name__ == "__main__":
    unittest.main()
