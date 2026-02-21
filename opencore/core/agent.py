import json
from typing import List, Dict, Any, Callable
from dotenv import load_dotenv
from litellm import completion

load_dotenv()


class Agent:
    def __init__(self, name: str, role: str, system_prompt: str, model: str = "gpt-4o", client: Any = None):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.model = model
        self.messages: List[Dict[str, Any]] = [
            {"role": "system", "content": f"You are {name}, a {role}. {system_prompt}"}
        ]
        self.tools: Dict[str, Callable] = {}
        self.tool_definitions: List[Dict[str, Any]] = []

        # Client is kept for backward compatibility but logic uses litellm which handles auth via env vars
        self.client = client

    def register_tool(self, func: Callable, schema: Dict[str, Any]):
        """
        Registers a tool (function) to be used by the agent.
        The schema must follow the OpenAI tool definition format:
        {
            "type": "function",
            "function": {
                "name": "function_name",
                "description": "...",
                "parameters": { ... }
            }
        }
        """
        self.tools[schema["function"]["name"]] = func
        self.tool_definitions.append(schema)

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

    def _execute_tool_calls(self, tool_calls: List[Any]):
        """Executes a list of tool calls and appends results to messages."""
        for tool_call in tool_calls:
            func_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            if func_name in self.tools:
                print(f"[{self.name}] Executing {func_name} with {arguments}")
                try:
                    result = self.tools[func_name](**arguments)
                except Exception as e:
                    result = f"Error executing {func_name}: {str(e)}"
            else:
                result = f"Error: Tool {func_name} not found."

            self.messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

    def think(self, max_turns: int = 5) -> str:
        if max_turns <= 0:
            return "Error: Max turns reached."

        try:
            # Litellm handles various providers (OpenAI, Anthropic, Vertex, Bedrock, Ollama)
            # automatically based on the model name and environment variables.
            response = completion(
                model=self.model,
                messages=self.messages,
                tools=self.tool_definitions if self.tool_definitions else None,
            )

            message = response.choices[0].message

            # If the model wants to call a tool
            if message.tool_calls:
                self.messages.append(message) # Add the assistant's message with tool calls
                self._execute_tool_calls(message.tool_calls)
                # Recursively think again to process the tool output and generate a final response
                return self.think(max_turns=max_turns - 1)

            else:
                content = message.content
                if content:
                    self.messages.append({"role": "assistant", "content": content})
                    return content
                else:
                    return "Error: Empty response from model."

        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"Error during thought process: {str(e)}"

    def chat(self, message: str) -> str:
        self.add_message("user", message)
        return self.think()
