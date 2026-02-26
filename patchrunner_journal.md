# PatchRunner Journal

## 2026-02-26 - Tool Execution Fragility
**Learning:** The `Agent._execute_tool_calls` logic was fragile because it attempted to parse tool arguments (JSON) inside `_normalize_tool_call` before extracting the `tool_call_id`. If parsing failed (e.g., malformed JSON from the LLM), the `tool_call_id` defaulted to "unknown".
**Action:** When executing tool calls, ALWAYS extract the `tool_call_id` and `function_name` *before* attempting to parse the arguments. This ensures that even if execution fails due to invalid input, the error message can be correctly associated with the specific tool call ID, preventing `400 Bad Request` errors from the LLM provider on subsequent turns.
