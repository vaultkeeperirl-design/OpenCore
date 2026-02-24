from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ToolCallFunction:
    name: str
    arguments: str  # JSON string

@dataclass
class ToolCall:
    id: str
    function: ToolCallFunction
    type: str = "function"

@dataclass
class LLMResponse:
    content: Optional[str]
    tool_calls: Optional[List[ToolCall]] = None

class LLMProvider(ABC):
    @abstractmethod
    def chat(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> LLMResponse:
        """
        Sends a chat request to the LLM provider.

        Args:
            messages: List of message dicts (role, content).
            tools: List of OpenAI-format tool definitions.

        Returns:
            LLMResponse object containing content and/or tool_calls.
        """
        pass
