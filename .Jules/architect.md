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

## 2026-02-28 - Structured API Response Format for Validation Errors

**Learning:** Pydantic validation errors (`fastapi.exceptions.RequestValidationError`) were not caught by the application's global exception handler and therefore returned the default FastAPI list-of-dictionaries format instead of the application's standardized JSON `ErrorResponse` schema. This forced clients to handle two entirely different error formats depending on whether a request failed business logic vs type validation.

**Action:**
1. Modified `opencore/interface/middleware.py`'s `global_exception_handler` to explicitly handle `RequestValidationError` exceptions.
2. Mapped the exception to an HTTP 422 status code with an `ErrorResponse` where code is `"UNPROCESSABLE_ENTITY"` and the details contain the stringified validation errors.
3. Registered the exception handler for `RequestValidationError` in `opencore/interface/api.py`.

## 2026-03-01 - Missing CORS Configuration

**Learning:** The FastAPI application processed all incoming requests without an explicit Cross-Origin Resource Sharing (CORS) policy. This structural omission prevented separated frontend clients (like web browsers on different origins) from securely accessing the API, making decoupled deployments impossible.
**Action:** Introduced `CORSMiddleware` in `opencore/interface/api.py` to establish explicit boundaries and allow flexible integration across origins. This resolves a hidden architectural limitation related to frontend-backend decoupling.

## 2026-03-03 - Centralized Domain Exception Handling

**Learning:** The API controller routes (`delete_agent`, `toggle_agent` in `opencore/interface/api.py`) were manually catching domain exceptions (`AgentNotFoundError`, `AgentOperationError`) and raising `HTTPException`. This violates the principle of separation of concerns, cluttering the routing logic with error handling that should be globally managed, and risking inconsistent error response schemas.
**Action:** Shifted to centralized domain exception handling. Added explicit handlers for `AgentNotFoundError` and `AgentOperationError` to the `global_exception_handler` in `opencore/interface/middleware.py`. Removed the redundant `try/except` blocks from the API routes, allowing domain exceptions to naturally bubble up to the centralized middleware where they are uniformly mapped to HTTP 404 and 403 responses with the standard `ErrorResponse` JSON schema.

## 2026-03-15 - Thread Safety for Global Swarm Singleton

**Learning:** The `Swarm` instance is a global singleton accessed concurrently by FastAPI threadpool threads (which execute synchronous routes and proactive heartbeat tasks). Modifying shared mutable state like `self.agents` and `self.interactions` directly without synchronization introduces race conditions, potentially leading to corrupted state or runtime exceptions under load.
**Action:** Introduced a `threading.Lock` within the `Swarm` class. Wrapped critical dictionary and list mutations (e.g., in `create_agent`, `remove_agent`, `delegate_task_wrapper`) in `with self._lock:` blocks to ensure safe concurrent access across API request threads while being careful not to hold the lock during blocking LLM inference.

## 2026-03-20 - Decoupling Request Validation from Routing Logic

**Learning:** The `/chat` endpoint manually validated the size of file attachments within its route handler (`if request.attachments: ... raise HTTPException()`). This mixes routing with business validation logic, violates separation of concerns, and bypassing the centralized `RequestValidationError` handler, leading to inconsistent error response schemas (HTTP 413 vs HTTP 422).
**Action:** Shifted request validation closer to the data contract. Extracted the file size check from `opencore/interface/api.py`'s `chat` route and implemented it as a Pydantic `@field_validator('content')` on the `Attachment` model. This enforces type/size boundaries strictly at the model level and relies on the `global_exception_handler` to consistently map the error to an HTTP 422 standard `ErrorResponse`.

## 2026-03-22 - Non-Blocking Event Loop Paradigm for Synchronous I/O

**Learning:** The FastAPI application defines several asynchronous route handlers (`async def`) that internally perform synchronous, blocking I/O operations. Specifically, `get_config` and `update_config` synchronously read and write the `.env` file via `settings.reload()` and `settings.update_env()`. Furthermore, `google_callback` in `auth_routes.py` makes a blocking network request via `flow.fetch_token()`. Executing synchronous blocking operations inside an `async def` function blocks the main ASGI event loop, causing severe latency spikes, degrading overall system throughput, and preventing concurrent requests from being processed during configuration or authentication flows.
**Action:** Refactored synchronous I/O routes to be standard `def` instead of `async def`. Modified `get_config` and `update_config` in `opencore/interface/api.py` and `google_login`, `google_callback`, and `qwen_login` in `opencore/interface/auth_routes.py`. By letting FastAPI inherently offload these synchronous `def` handlers to its own built-in thread pool, we achieve a much cleaner architectural fix without boilerplate, ensuring the ASGI event loop remains responsive.

## 2026-03-30 - Basic Rate Limiting

**Learning:** The application lacked any mechanism to limit the number of requests a single client IP could make, leaving it vulnerable to basic abuse, rapid token exhaustion, and potential denial-of-service against third-party LLM providers.
**Action:** Introduced a basic in-memory `RateLimitMiddleware` in `opencore/interface/rate_limit.py`. This middleware implements a simple fixed-window counter per client IP, rejecting requests with HTTP 429 Too Many Requests once the limit is exceeded, and returning the standard `ErrorResponse` schema for consistency.

## 2026-03-31 - Structured API Response Contracts

**Learning:** Several endpoints in the FastAPI application (e.g., `/agents`, `/heartbeat`, `/config`, `/transcribe`) returned raw Python dictionaries instead of utilizing Pydantic models for responses. This violated the architectural goal of typed contracts, resulting in inconsistent data structures and missing/incomplete OpenAPI documentation, which weakened long-term maintainability.
**Action:** Introduced typed Pydantic response models (`AgentListResponse`, `AgentActionResponse`, `HeartbeatResponse`, `AuthStatusResponse`, `ConfigResponse`, `ConfigUpdateResponse`, `TranscribeResponse`) and explicitly bound them to their respective routes via the `response_model` parameter in `opencore/interface/api.py`. This ensures runtime validation and creates strict, self-documenting API boundaries without adding unnecessary middleware.

## 2026-04-05 - O(1) Tool Definition Management

**Learning:** The `Agent` class in `opencore/core/agent.py` managed tool definitions using a list (`self.tool_definitions`). During tool registration (`register_tool`), it iterated over the entire list to check if a tool definition already existed before updating or appending it. This resulted in an $O(n)$ operation for each tool registration, which scales poorly as the number of available tools grows.
**Action:** Refactored the internal data structure to use a dictionary (`self._tool_definitions`) keyed by tool name. This allows for $O(1)$ lookups and updates during registration. Exposed a public `tool_definitions` property that dynamically generates the list of definitions required for compatibility with LLM provider APIs.
