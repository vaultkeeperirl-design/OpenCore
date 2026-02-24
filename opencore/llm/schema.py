from typing import Dict, Any, List

def convert_to_anthropic_tool(openai_tool: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converts an OpenAI tool definition to Anthropic format.
    OpenAI: {"type": "function", "function": {"name": "...", "description": "...", "parameters": {...}}}
    Anthropic: {"name": "...", "description": "...", "input_schema": {...}}
    """
    func = openai_tool.get("function", {})
    return {
        "name": func.get("name"),
        "description": func.get("description"),
        "input_schema": func.get("parameters", {"type": "object", "properties": {}})
    }

def convert_to_gemini_tool(openai_tool: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converts an OpenAI tool definition to Google Gemini format.
    Gemini expects a list of function declarations. Here we return a single FunctionDeclaration dict.
    """
    func = openai_tool.get("function", {})
    return {
        "name": func.get("name"),
        "description": func.get("description"),
        "parameters": func.get("parameters", {"type": "object", "properties": {}})
    }
