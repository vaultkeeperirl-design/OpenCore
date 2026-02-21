# Refine's Journal

## 2026-02-21 - Replace Print with Logging

**Learning:** Core library components (e.g., `Agent` class) relied on `print` statements and `traceback.print_exc()` for debugging and error reporting. This reduces observability in production environments where stdout/stderr might not be captured effectively or where log levels are needed to filter noise.
**Action:** Adopt standard Python `logging` for all internal operations. Use `logger.info` for operational events and `logger.exception` for error handling to ensure stack traces are captured properly within the log record.
