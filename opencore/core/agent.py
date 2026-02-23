import json
import logging
from typing import List, Dict, Any, Callable
from dotenv import load_dotenv
from litellm import completion

load_dotenv()

logger = logging.getLogger(__name__)


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
            result = ""
            tool_id = "unknown"
            func_name = "unknown"

            try:
                tool_id = tool_call.id
                func_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                if func_name in self.tools:
                    logger.info(f"[{self.name}] Executing {func_name} with {arguments}")
                    try:
                        result = self.tools[func_name](**arguments)
                    except Exception as e:
                        logger.exception(f"Error executing {func_name}: {str(e)}")
                        result = f"Error executing {func_name}: {str(e)}"
                else:
                    result = f"Error: Tool {func_name} not found."

            except json.JSONDecodeError as e:
                result = f"Error: Invalid JSON arguments for tool {func_name}: {str(e)}"
            except Exception as e:
                logger.exception(f"Error processing tool call {func_name}: {str(e)}")
                result = f"Error processing tool call {func_name}: {str(e)}"

            self.messages.append({
                "role": "tool",
                "tool_call_id": tool_id,
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
                timeout=60,  # Prevent indefinite hanging
            )

            message = response.choices[0].message

            # If the model wants to call a tool
            if message.tool_calls:
                # Add the assistant's message with tool calls
                self.messages.append(message)
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
            error_msg = str(e)
            logger.exception(f"Error during thought process: {error_msg}")

            # User-friendly error for missing credentials
            if "credentials were not found" in error_msg or "api_key" in error_msg.lower():
                 return "SYSTEM ALERT: LLM configuration invalid or missing. Please configure your provider in Settings."

            return f"Error during thought process: {error_msg}"

    def chat(self, message: str) -> str:
        self.add_message("user", message)
        return self.think()
