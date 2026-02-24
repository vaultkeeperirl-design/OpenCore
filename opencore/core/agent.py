import json
import logging
import os
from typing import List, Dict, Any, Callable, Optional, Union
from litellm import completion


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

    def add_message(self, role: str, content: Union[str, List[Dict[str, Any]]]):
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

    def _prune_messages(self):
        """Prunes message history to prevent context window exhaustion."""
        MAX_HISTORY = 100
        # If history exceeds limit (plus system prompt)
        if len(self.messages) > (MAX_HISTORY + 1):
            # Preserve system prompt at index 0
            system_prompt = self.messages[0]
            # Keep the last MAX_HISTORY messages
            recent_messages = self.messages[-MAX_HISTORY:]
            self.messages = [system_prompt] + recent_messages
            logger.warning(f"[{self.name}] Pruned message history to {len(self.messages)} items.")

    def think(self, max_turns: int = 5) -> str:
        if max_turns <= 0:
            return "Error: Max turns reached."

        self._prune_messages()

        try:
            # Litellm handles various providers (OpenAI, Anthropic, Vertex, Bedrock, Ollama)
            # automatically based on the model name and environment variables.

            call_model = self.model
            call_api_base = None
            call_api_key = None

            # Qwen OAuth Logic: If we have an OAuth token, redirect to Portal API as OpenAI-compatible
            if ("qwen" in self.model.lower() or "dashscope" in self.model.lower()) and os.environ.get("QWEN_ACCESS_TOKEN"):
                qwen_token = os.environ.get("QWEN_ACCESS_TOKEN")
                # Extract pure model name
                model_name = self.model.split("/", 1)[1] if "/" in self.model else self.model

                # Use openai provider for compatibility with Portal API
                call_model = f"openai/{model_name}"
                call_api_base = "https://portal.qwen.ai/v1"
                call_api_key = qwen_token
                logger.info(f"Using Qwen OAuth for model {model_name}")

            response = completion(
                model=call_model,
                messages=self.messages,
                tools=self.tool_definitions if self.tool_definitions else None,
                timeout=60,  # Prevent indefinite hanging
                api_base=call_api_base,
                api_key=call_api_key
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
            error_msg_lower = error_msg.lower()

            # User-friendly error for missing credentials
            error_msg_lower = error_msg.lower()
            if "credentials were not found" in error_msg_lower or "api_key" in error_msg_lower or "api key" in error_msg_lower:
                 return "SYSTEM ALERT: LLM configuration invalid or missing. Please configure your provider in Settings."

            logger.exception(f"Error during thought process: {error_msg}")
            return f"Error during thought process: {error_msg}"

    def chat(self, message: str, attachments: Optional[List[Dict[str, Any]]] = None) -> str:
        if attachments:
            content = []
            text_content = message

            # 1. Process Text/Code Attachments (append to text)
            for att in attachments:
                if not att["type"].startswith("image/"):
                    text_content += f"\n\n[Attachment: {att['name']}]\n{att['content']}\n[End Attachment]"

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
