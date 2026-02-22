# PatchRunner's Journal

## 2025-02-20 - Fragile Tool Parsing
**Learning:** `json.loads` on LLM output is a critical failure point. A single malformed JSON argument crashes the entire agent loop, losing context.
**Action:** Always wrap `json.loads` and tool execution in `try...except` blocks to catch `json.JSONDecodeError` and return an error message to the model for self-correction.
