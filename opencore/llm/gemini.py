from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
import os
import json
import uuid
from .base import LLMProvider, LLMResponse, ToolCall, ToolCallFunction
from .schema import convert_to_gemini_tool


class GeminiProvider(LLMProvider):
    def __init__(self, model_name: str, api_key: Optional[str] = None):
        if not api_key:
            # Try env var
            api_key = os.getenv("GEMINI_API_KEY")

        vertex_project = os.getenv("VERTEX_PROJECT")
        vertex_location = os.getenv("VERTEX_LOCATION")

        if api_key:
            self.client = genai.Client(api_key=api_key)
        elif vertex_project and vertex_location:
            self.client = genai.Client(vertexai=True, project=vertex_project, location=vertex_location)
        else:
            raise ValueError("Gemini API Key or Vertex Project/Location is required.")

        # Handle model name mapping/stripping
        # The new SDK handles 'models/' prefix fine, but often expects just 'gemini-...'
        # We strip 'gemini/' if it's our internal prefix.
        if model_name.startswith("gemini/"):
            self.model_name = model_name[7:]
        elif model_name.startswith("models/"):
            self.model_name = model_name
        else:
            self.model_name = model_name

    def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> LLMResponse:
        system_instruction = None
        contents = []

        # Map tool_call_id -> function_name from history to reconstruct function responses
        tool_id_map = {}

        for msg in messages:
            role = msg["role"]
            content = msg.get("content")

            if role == "system":
                system_instruction = content
                continue

            if role == "user":
                contents.append({"role": "user", "parts": [{"text": content or ""}]})

            elif role == "assistant":
                parts = []
                if content:
                    parts.append({"text": content})

                tool_calls = msg.get("tool_calls")
                if tool_calls:
                    for tc in tool_calls:
                        # Store mapping for later (using ID to find name)
                        tool_id_map[tc.id] = tc.function.name

                        # Add function call to parts
                        try:
                            args = json.loads(tc.function.arguments)
                        except Exception:
                            args = {}

                        parts.append({
                            "function_call": {
                                "name": tc.function.name,
                                "args": args
                            }
                        })

                contents.append({"role": "model", "parts": parts})

            elif role == "tool":
                # Convert to function_response
                tool_id = msg.get("tool_call_id")
                func_name = tool_id_map.get(tool_id)

                if func_name:
                    try:
                        result_data = json.loads(content)
                        if not isinstance(result_data, dict):
                            result_data = {"result": result_data}
                    except Exception:
                        result_data = {"result": content}

                    contents.append({
                        "role": "function",
                        "parts": [{
                            "function_response": {
                                "name": func_name,
                                "response": result_data
                            }
                        }]
                    })
                else:
                    # Fallback if we can't find the function name
                    contents.append(
                        {"role": "user", "parts": [{"text": f"Tool result: {content}"}]}
                    )

        # Configure tools
        config = types.GenerateContentConfig()

        if system_instruction:
            config.system_instruction = system_instruction

        if tools:
            declarations = []
            for t in tools:
                # convert_to_gemini_tool returns a dict with keys: name, description, parameters
                # parameters is a dict representing the schema.
                decl_dict = convert_to_gemini_tool(t)

                # We need to construct types.FunctionDeclaration or allow dict if SDK supports it.
                # It's safer to use dicts inside the list if we aren't sure about strict typing,
                # but passing dicts to types.Tool(function_declarations=[...]) usually works.
                declarations.append(decl_dict)

            # Create a single Tool object containing all declarations
            # Note: The SDK expects a list of Tool objects in config.tools
            tool_obj = types.Tool(function_declarations=declarations)

            config.tools = [tool_obj]

            # Set tool config to AUTO
            config.tool_config = types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(
                    mode="AUTO"
                )
            )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )

            if not response.candidates:
                return LLMResponse(content="Error: No candidates returned.")

            candidate = response.candidates[0]
            content_parts = []
            tool_calls_list = []

            for part in candidate.content.parts:
                if part.text:
                    content_parts.append(part.text)

                if part.function_call:
                    fc = part.function_call
                    # fc.args is likely a dict or object that behaves like one
                    # We need to serialize it to JSON string for LLMResponse
                    try:
                        # If fc.args is a dict
                        args_dict = dict(fc.args)
                    except Exception:
                        # If it's something else, try verify
                        args_dict = {}

                    # Generate ID
                    call_id = f"call_{uuid.uuid4().hex[:8]}"

                    tool_calls_list.append(ToolCall(
                        id=call_id,
                        function=ToolCallFunction(
                            name=fc.name,
                            arguments=json.dumps(args_dict)
                        )
                    ))

            content_str = "".join(content_parts) if content_parts else None

            return LLMResponse(
                content=content_str,
                tool_calls=tool_calls_list if tool_calls_list else None
            )

        except Exception as e:
            # Handle API errors (e.g. 404, 429)
            return LLMResponse(content=f"Error from Gemini: {str(e)}")
