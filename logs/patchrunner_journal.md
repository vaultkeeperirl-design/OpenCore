# PatchRunner Journal

## 2025-02-17 - Inconsistent Exception Logging
**Learning:** Multiple core components (`agent.py`, `middleware.py`) were using `traceback.print_exc()` instead of `logger.exception`, bypassing log configuration and reducing observability in production.
**Action:** Enforce use of `logger.exception` in catch blocks during code reviews. Check for `traceback` imports in future hotfixes.

## 2026-02-23 - Missing Import in Critical Security Tool
**Learning:** The `execute_command` tool in `opencore/tools/base.py` relied on `shlex` but failed to import it, causing a `NameError` and breaking the tool.
**Action:** Always verify imports when using standard library modules like `shlex`. Add regression tests for tool imports.

## 2026-02-23 - Unbounded Message History Growth
**Learning:** The `Agent` class allowed infinite message accumulation, leading to potential context window exhaustion and memory leaks.
**Action:** Implemented a rolling window pruning mechanism in `Agent.think` to limit history while preserving the system prompt. Future agents should support configurable history limits.

## 2026-02-24 - Frontend Validation Gaps
**Learning:** The `ChatInterface` component lacked client-side size validation for file uploads, relying solely on backend (or crashing before reaching backend).
**Action:** Enforce size limits on all file inputs/drops in frontend components.

## 2026-02-24 - Orphaned Tool Messages in History Pruning
**Learning:** The `Agent._prune_messages` method naively sliced the message history, which could split a `tool_calls` / `tool` message pair, leaving an orphaned `tool` message at the start of the conversation history. This causes schema validation errors in strict LLM APIs (like OpenAI).
**Action:** Updated `_prune_messages` to recursively remove `tool` messages if they appear at the start of the pruned history (after the system prompt).

## 2026-02-25 - Stale Frontend Artifacts
**Learning:** The frontend source code contained a critical fix for file upload size limits, but the committed static assets in `opencore/interface/static` were outdated, leaving the bug active in production.
**Action:** Always verify that `opencore/interface/static` matches the frontend source when diagnosing frontend bugs. Consider adding a CI check to ensure static assets are up-to-date with source.
