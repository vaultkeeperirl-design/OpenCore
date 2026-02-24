from typing import List, Dict, Any, Optional
import anthropic
import json
from .base import LLMProvider, LLMResponse, ToolCall, ToolCallFunction
from .schema import convert_to_anthropic_tool

class AnthropicProvider(LLMProvider):
    def __init__(self, model_name: str, api_key: Optional[str] = None):
        self.model_name = model_name
        self.client = anthropic.Anthropic(api_key=api_key)

    def chat(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> LLMResponse:
        # Anthropic separates system prompt from messages
        system_prompt = None
        filtered_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            else:
                filtered_messages.append(msg)

        kwargs = {
            "model": self.model_name,
            "max_tokens": 4096,
            "messages": filtered_messages
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        if tools:
            kwargs["tools"] = [convert_to_anthropic_tool(t) for t in tools]

        response = self.client.messages.create(**kwargs)

        content_blocks = []
        tool_calls_list = []

        for block in response.content:
            if block.type == "text":
                content_blocks.append(block.text)
            elif block.type == "tool_use":
                tool_calls_list.append(ToolCall(
                    id=block.id,
                    function=ToolCallFunction(
                        name=block.name,
                        arguments=json.dumps(block.input)
                    )
                ))

        content_str = "".join(content_blocks) if content_blocks else None

        return LLMResponse(
            content=content_str,
            tool_calls=tool_calls_list if tool_calls_list else None
        )
