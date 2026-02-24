import json
import logging
from typing import Dict, Any, List

def convert_to_anthropic_tool(openai_tool: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converts an OpenAI tool definition to Anthropic format.
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
    """
    func = openai_tool.get("function", {})

    # Extract parameters
    parameters = func.get("parameters", {})

    def _convert_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
        new_schema = {}

        # 1. Type: Convert to uppercase (e.g. "string" -> "STRING")
        if "type" in schema:
            typ = schema["type"]
            if isinstance(typ, str):
                new_schema["type"] = typ.upper()
            else:
                new_schema["type"] = typ

        # 2. Description
        if "description" in schema:
            new_schema["description"] = schema["description"]

        # 3. Enum
        if "enum" in schema:
            new_schema["enum"] = schema["enum"]

        # 4. Properties (Recursion)
        if "properties" in schema and isinstance(schema["properties"], dict):
            new_props = {}
            for k, v in schema["properties"].items():
                new_props[k] = _convert_schema(v)
            new_schema["properties"] = new_props

        # 5. Required (List of strings)
        if "required" in schema and isinstance(schema["required"], list):
            new_schema["required"] = schema["required"]

        # 6. Items (Recursion for arrays)
        if "items" in schema:
            new_schema["items"] = _convert_schema(schema["items"])

        return new_schema

    converted_params = _convert_schema(parameters)

    return {
        "name": func.get("name"),
        "description": func.get("description"),
        "parameters": converted_params
    }
