# PatchRunner Journal

## 2025-02-17 - Inconsistent Exception Logging
**Learning:** Multiple core components (`agent.py`, `middleware.py`) were using `traceback.print_exc()` instead of `logger.exception`, bypassing log configuration and reducing observability in production.
**Action:** Enforce use of `logger.exception` in catch blocks during code reviews. Check for `traceback` imports in future hotfixes.

## 2026-02-23 - Missing Import in Critical Security Tool
**Learning:** The `execute_command` tool in `opencore/tools/base.py` relied on `shlex` but failed to import it, causing a `NameError` and breaking the tool.
**Action:** Always verify imports when using standard library modules like `shlex`. Add regression tests for tool imports.
