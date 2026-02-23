# PatchRunner Journal

## 2025-02-17 - Inconsistent Exception Logging
**Learning:** Multiple core components (`agent.py`, `middleware.py`) were using `traceback.print_exc()` instead of `logger.exception`, bypassing log configuration and reducing observability in production.
**Action:** Enforce use of `logger.exception` in catch blocks during code reviews. Check for `traceback` imports in future hotfixes.

## 2026-02-23 - Swallowed Tool Exceptions
**Learning:** The `Agent` class in `opencore/core/agent.py` was swallowing exceptions during tool execution without logging them, making it impossible to diagnose tool failures.
**Action:** Always use `logger.exception` in `except` blocks that handle external code execution (like tools) to capture full tracebacks.
