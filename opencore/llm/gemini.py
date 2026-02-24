from typing import List, Dict, Any, Optional
import google.generativeai as genai
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
        if not api_key:
            raise ValueError("Gemini API Key is required.")

        genai.configure(api_key=api_key)
        # Strip 'gemini/' prefix if present
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

        # Map tool_call_id -> function_name from history
        tool_id_map = {}

        for msg in messages:
            role = msg["role"]
            content = msg.get("content")

            if role == "system":
                system_instruction = content
                continue

            if role == "user":
                contents.append({"role": "user", "parts": [content or ""]})

            elif role == "assistant":
                parts = []
                if content:
                    parts.append({"text": content})

                tool_calls = msg.get("tool_calls")
                if tool_calls:
                    for tc in tool_calls:
                        # Store mapping for later
                        tool_id_map[tc.id] = tc.function.name

                        # Add function call to parts
                        # Args must be dict
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
                    # Parse result (content) into a dict structure if possible,
                    # otherwise wrap in result key.
                    # Gemini expects `response` to be a dict (struct).
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
                    # If we can't find the function name, treat as user text
                    contents.append(
                        {"role": "user", "parts": [f"Tool result: {content}"]}
                    )

        # Configure tools
        gemini_tools = None
        if tools:
            # Convert list of OpenAI tools to Gemini FunctionDeclarations
            declarations = []
            for t in tools:
                declarations.append(convert_to_gemini_tool(t))
            gemini_tools = declarations

        # Initialize model
        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_instruction,
            tools=gemini_tools
        )

        try:
            response = model.generate_content(contents)

            # Extract content and function calls
            if not response.candidates:
                return LLMResponse(content="Error: No candidates returned.")

            candidate = response.candidates[0]
            content_parts = []
            tool_calls_list = []

            for part in candidate.content.parts:
                if part.text:
                    content_parts.append(part.text)

                # Check for function_call attribute
                if hasattr(part, 'function_call') and part.function_call:
                    fc = part.function_call
                    # Convert args (proto map) to dict then json string
                    args_dict = {}
                    for k, v in fc.args.items():
                        args_dict[k] = v

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
            return LLMResponse(content=f"Error from Gemini: {str(e)}")
