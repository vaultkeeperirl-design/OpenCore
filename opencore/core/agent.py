import json
import logging
from typing import List, Dict, Any, Callable, Optional, Union
from opencore.llm import get_llm_provider
from opencore.llm.base import LLMResponse
from opencore.config import settings

logger = logging.getLogger(__name__)


class Agent:
    def __init__(
        self,
        name: str,
        role: str,
        system_prompt: str,
        model: str = "gpt-4o",
        client: Any = None,
        is_custom_model: bool = False,
        created_by: Optional[str] = None
    ):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.model = model
        self.is_custom_model = is_custom_model
        self.created_by = created_by
        self.status = "active"
        self.last_thought: str = "Idle"
        sys_msg = f"You are {name}, a {role}. {system_prompt}"
        self.messages: List[Dict[str, Any]] = [
            {"role": "system", "content": sys_msg}
        ]
        self.tools: Dict[str, Callable] = {}
        self.tool_definitions: List[Dict[str, Any]] = []

        # Client is unused now but kept for sig compatibility
        self.client = client

    def register_tool(self, func: Callable, schema: Dict[str, Any]):
        """
        Registers a tool (function) to be used by the agent.
        The schema must follow the OpenAI tool definition format.
        """
        tool_name = schema["function"]["name"]
        self.tools[tool_name] = func

        # Check if tool definition already exists and update it
        for i, definition in enumerate(self.tool_definitions):
            if definition["function"]["name"] == tool_name:
                self.tool_definitions[i] = schema
                return

        # If not found, append new definition
        self.tool_definitions.append(schema)

    def add_message(
        self, role: str, content: Union[str, List[Dict[str, Any]]]
    ):
        self.messages.append({"role": role, "content": content})

    def _execute_tool_calls(self, tool_calls: List[Any]):
        """Executes a list of tool calls and appends results."""
        for tool_call in tool_calls:
            result = ""
            tool_id = "unknown"
            func_name = "unknown"

            try:
                # Support both object (dot notation) and dict access
                if isinstance(tool_call, dict):
                    tool_id = tool_call.get("id")
                    func_name = tool_call["function"]["name"]
                    arguments = json.loads(tool_call["function"]["arguments"])
                else:
                    tool_id = tool_call.id
                    func_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)

                if func_name in self.tools:
                    logger.info(
                        f"[{self.name}] Executing {func_name} with {arguments}"
                    )
                    try:
                        result = self.tools[func_name](**arguments)
                    except Exception as e:
                        logger.exception(f"Error {func_name}: {str(e)}")
                        result = f"Error executing {func_name}: {str(e)}"
                else:
                    result = f"Error: Tool {func_name} not found."

            except json.JSONDecodeError as e:
                result = (
                    f"Error: Invalid JSON for {func_name}: {str(e)}"
                )
            except Exception as e:
                logger.exception(f"Error call {func_name}: {str(e)}")
                result = f"Error processing tool call {func_name}: {str(e)}"

            self.messages.append({
                "role": "tool",
                "tool_call_id": tool_id,
                "content": str(result)
            })

    def _prune_messages(self):
        """Prunes message history to prevent context window exhaustion."""
        MAX_HISTORY = settings.max_history
        # If history exceeds limit (plus system prompt)
        if len(self.messages) > (MAX_HISTORY + 1):
            # Preserve system prompt at index 0
            system_prompt = self.messages[0]
            # Keep the last MAX_HISTORY messages
            recent_messages = self.messages[-MAX_HISTORY:]
            self.messages = [system_prompt] + recent_messages

            # Ensure the first message after system prompt is not a 'tool' message (orphaned result)
            while len(self.messages) > 1 and self.messages[1].get("role") == "tool":
                self.messages.pop(1)

            logger.warning(
                f"[{self.name}] Pruned history to {len(self.messages)} items."
            )

    def think(self, max_turns: Optional[int] = None) -> str:
        if self.status == "inactive":
            return f"Error: Agent '{self.name}' is currently inactive."

        if max_turns is None:
            max_turns = settings.max_turns

        if max_turns <= 0:
            return "Error: Max turns reached."

        self._prune_messages()

        try:
            # 1. Get Provider
            provider = get_llm_provider(
                self.model,
                is_custom_model=self.is_custom_model
            )

            # 2. Chat
            response: LLMResponse = provider.chat(
                messages=self.messages,
                tools=self.tool_definitions if self.tool_definitions else None
            )

            # 3. Handle Response
            # Convert response to dict for storage
            assistant_msg = {"role": "assistant", "content": response.content}
            if response.tool_calls:
                assistant_msg["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in response.tool_calls
                ]

            self.messages.append(assistant_msg)

            # If tool calls present
            if response.tool_calls:
                self.last_thought = "Executing tools..."
                self._execute_tool_calls(response.tool_calls)
                # Recursively think again to process the tool output
                return self.think(max_turns=max_turns - 1)
            else:
                if response.content:
                    self.last_thought = response.content
                    return response.content
                else:
                    self.last_thought = "Error: Empty response."
                    return "Error: Empty response from model."

        except Exception as e:
            error_msg = str(e)
            error_msg_lower = error_msg.lower()

            logger.exception(f"Error during thought process: {error_msg}")

            # User-friendly error for missing credentials
            if "api_key" in error_msg_lower or \
               "api key" in error_msg_lower or \
               "credentials" in error_msg_lower:
                return (
                    f"SYSTEM ALERT: LLM configuration invalid or missing ({error_msg}). "
                    "Please configure your provider in Settings."
                )

            return f"Error during thought process: {error_msg}"

    def chat(
        self,
        message: str,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        if attachments:
            content = []
            text_parts = [message] + [
                f"\n\n[Attachment: {att['name']}]\n{att['content']}\n[End]"
                for att in attachments if not att["type"].startswith("image/")
            ]
            text_content = "".join(text_parts)
            content.append({"type": "text", "text": text_content})

            # 2. Process Image Attachments
            for att in attachments:
                if att["type"].startswith("image/"):
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": att["content"]}
                    })

            self.add_message("user", content)
        else:
            self.add_message("user", message)

        return self.think()
