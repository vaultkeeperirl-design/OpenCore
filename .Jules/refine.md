## 2025-02-19 - Centralized Configuration Logic

**Learning:** Configuration logic, especially string normalization or correction, tends to get duplicated across read (loading env) and write (updating env) operations.
**Action:** Extract such logic into constant dictionaries or helper methods within the `Settings` class to ensure consistency and single source of truth.

## 2025-06-25 - Polymorphic Tool Call Handling

**Learning:** `Agent` tool execution logic was handling both dictionary and object representations of tool calls inline, causing complexity and repetition.
**Action:** Extract normalization logic into helper methods (e.g., `_normalize_tool_call`) to improve readability and allow isolated testing of data parsing.
