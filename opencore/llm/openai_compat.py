from typing import List, Dict, Any, Optional
import os
import json
from openai import OpenAI
from .base import LLMProvider, LLMResponse, ToolCall, ToolCallFunction

class OpenAICompatibleProvider(LLMProvider):
    def __init__(self, model_name: str, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.model_name = model_name
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def chat(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> LLMResponse:
        # Check if messages need any special handling (e.g. system message role)
        # OpenAI supports "system" role natively.

        kwargs = {
            "model": self.model_name,
            "messages": messages,
        }

        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = self.client.chat.completions.create(**kwargs)

        message = response.choices[0].message

        tool_calls_list = None
        if message.tool_calls:
            tool_calls_list = []
            for tc in message.tool_calls:
                tool_calls_list.append(ToolCall(
                    id=tc.id,
                    function=ToolCallFunction(
                        name=tc.function.name,
                        arguments=tc.function.arguments
                    ),
                    type=tc.type
                ))

        return LLMResponse(
            content=message.content,
            tool_calls=tool_calls_list
        )
