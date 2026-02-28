# Architect's Journal

## 2025-02-18 - Centralized Configuration

**Learning:** Configuration was scattered across `os.getenv` calls in multiple files (`agent.py`, `swarm.py`, `middleware.py`), leading to hidden defaults and potential inconsistencies. `load_dotenv` was called in library code (`agent.py`), causing side effects on import.
**Action:** Created `opencore/config.py` with a `Settings` class to centralize environment variable loading and defaults. Refactored `agent.py`, `swarm.py`, `middleware.py`, and `main.py` to use this single source of truth. Updated tests to mock the configuration object.

## 2026-02-22 - Structured Logging

**Learning:** Application logs were formatted inconsistently across different modules, with direct `traceback.print_exc()` bypassing the logging system and relying on `logging.basicConfig` without a formatter. This makes log aggregation and parsing in production difficult.
**Action:** Created `opencore/core/logging.py` to provide a centralized `configure_logging()` function with a custom `JSONFormatter` for production environments. Standardized middleware to use `logger.exception` and ensured all logs are captured structured.

## 2026-02-23 - Robust Environment Management

**Learning:** Manual parsing and writing of `.env` files in `opencore/interface/api.py` was brittle and destructive (removing comments). Configuration updates were tightly coupled to the API layer, violating separation of concerns.
**Action:** Centralized environment management in `opencore/config.py` using `python-dotenv`'s `set_key` for safe, non-destructive updates. Removed direct `os.getenv` calls from API endpoints, enforcing usage of the `Settings` singleton as the single source of truth.

## 2026-02-24 - Missing Request Context Observability

**Learning:** The system lacks a mechanism to trace requests across the application stack. While logging is configured, there is no unique identifier (Request ID) propagated through the execution context. This makes debugging concurrent requests or correlating logs from different components (API, Scheduler, Swarm) impossible in production.

**Action:** Introduce a `ContextVar`-based Request ID propagation system.
1. Create a `context` module to hold thread-safe/task-safe global state.
2. Implement an ASGI middleware to generate and inject Request IDs.
3. Attach a logging filter to automatically tag all log records with the current Request ID.

## 2026-02-25 - Fragile String-Based Control Flow

**Learning:** The `Swarm` class methods (`remove_agent`, `toggle_agent`) return error strings (e.g., "Error: ...") instead of raising exceptions. The API layer (`api.py`) relies on parsing these strings (`if "Error" in result`) to determine success or failure. This "String Typing" anti-pattern is brittle, prevents proper HTTP status codes (everything returns 200 OK or generic errors), and tightly couples the business logic to the LLM's text-based interface.

**Action:** Decouple the core logic from the tool interface.
1.  Introduce standard exceptions (`AgentNotFoundError`, `AgentOperationError`).
2.  Refactor `Swarm` methods to raise exceptions for logic errors.
3.  Update API endpoints to catch these exceptions and return appropriate HTTP 404/403 responses.
4.  Wrap `Swarm` methods in the tool registration layer to catch exceptions and return the descriptive strings the LLM expects.

## 2026-02-28 - Typed Request Validation

**Learning:** The `/config` API endpoint accepted untyped dictionaries (`Dict[str, Any]`), bypassing FastAPI's Pydantic validation. This allowed invalid data types (e.g., strings instead of integers for `HEARTBEAT_INTERVAL`) to be written to the persistent `.env` file, causing catastrophic system crashes upon reloading the configuration singleton.
**Action:** Introduced a `ConfigRequest` Pydantic model to enforce strict type boundaries at the API layer. This request validation middleware guarantees that environment variables are type-safe before persistence, eliminating a critical architectural blind spot.
