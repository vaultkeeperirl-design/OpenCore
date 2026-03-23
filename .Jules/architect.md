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

## 2026-04-12 - Health Check Observability

**Learning:** The application lacked a basic, fast `Liveness`/`Readiness` probe. While `/heartbeat` existed, it performed more complex checks and status accumulation. Load balancers, Kubernetes, and simple uptime monitors need a lightweight, unauthenticated endpoint that strictly verifies the HTTP server is accepting connections without any overhead.
**Action:** Introduced a minimal `GET /health` endpoint returning `{"status": "ok"}` with a typed `HealthCheckResponse` model. This adheres to standard infrastructure patterns and provides a clear separation between a simple API liveness check and the more detailed system heartbeat.

## 2026-04-10 - Request-Scoped State Isolation

**Learning:** Request-scoped state (`current_turn_activity`) was stored as a mutable instance variable on the global `Swarm` singleton. In a concurrent environment (like FastAPI with thread pools), multiple requests executing `/chat` simultaneously would interleave their activity logs, resulting in corrupted API responses and potential cross-session data leakage. This is a critical structural weakness of storing request lifecycle data on shared global singletons.
**Action:** Extracted `current_turn_activity` into a thread-safe `ContextVar` (`activity_log_ctx`) managed by the API layer. This ensures strict request-level boundary isolation, eliminating race conditions without introducing locking bottlenecks during I/O operations.

## 2026-04-15 - Service Layer Extraction for Configuration

**Learning:** The API routing layer (`opencore/interface/api.py`) was directly orchestrating configuration file updates, filtering allowed keys, and manually notifying the `Swarm` singleton. This tight coupling violated the Single Responsibility Principle, mixing HTTP transport logic with system configuration business logic, making it difficult to test or reuse configuration management independently.
**Action:** Extracted configuration logic into a dedicated `ConfigService` (`opencore/core/config_service.py`). The API layer now simply delegates to this service, ensuring clear boundaries between transport, validation (via Pydantic), and business operations.

## 2026-04-20 - Service Layer Extraction for Google Auth

**Learning:** The Google OAuth routes (`google_login` and `google_callback`) in `opencore/interface/auth_routes.py` directly instantiated the OAuth `Flow`, managed local testing transport environment variables, updated the config environment variables, and defined API scopes. This tightly coupled HTTP transport routing with authorization domain logic and configuration management, violating separation of concerns and making the authorization business logic difficult to isolate or test.
**Action:** Created `GoogleAuthService` inside `opencore/auth/google.py` that encapsulates all the OAuth domain logic. Refactored `auth_routes.py` to simply instantiate this service and call `get_login_url()` and `handle_callback()`. Deferred loading `from opencore.config import settings` within the service's methods to prevent circular dependency problems between the authentication domain and application configuration logic.

## 2026-04-25 - Decoupling Request Validation from Routing Logic in Authentication

**Learning:** The authentication routes (`opencore/interface/auth_routes.py`) were manually reading JSON request bodies and performing inline validation (e.g., checking if `api_key` exists), as well as returning raw, untyped Python dictionaries. Furthermore, exceptions were manually caught and returned as JSON dictionaries, bypassing the centralized error handling mechanisms. This approach violates the principle of keeping routing logic thin and the API schema typed and standardized. It causes inconsistent error responses (bypassing `ErrorResponse` schemas), avoids auto-generated documentation, and obscures the API's actual data contracts.
**Action:** Replaced manual validation and dictionary returns with typed Pydantic models (`QwenCallbackRequest`, `AuthCallbackResponse`) on the `/qwen/callback` endpoint, and refactored the `google_login` and `google_callback` endpoints to raise standard `HTTPException` instances rather than returning dictionaries. This architectural shift guarantees that all requests pass through centralized FastAPI validation and any resulting errors are routed through the `global_exception_handler`, ensuring a unified and typed API boundary constraint.

## 2026-05-15 - Secure Environment File Permissions

**Learning:** The `.env` file, which stores sensitive API keys and configuration, was being created and updated by `opencore/config.py` and `opencore/cli/onboard.py` without explicitly restricting file permissions. Depending on the system's default `umask`, this could expose sensitive credentials to other users on the system (e.g., `0o644` read permissions for everyone). This is a hidden risk and violates the "Secure by default" principle.
**Action:** Enforced restrictive file permissions (`0o600`, owner read/write only) on the `.env` file immediately upon creation or update. Added `os.chmod(env_path, 0o600)` to `Settings.update_env` and `run_onboarding` to guarantee that secrets are locked down at the OS level. Introduced `tests/test_env_permissions.py` as a regression test.

## 2026-05-20 - Environment Schema Validation

**Learning:** Environment variables loaded via `os.getenv` in `opencore/config.py` were directly cast to integers using `int()`. If a user manually edited the `.env` file and entered a non-integer value (e.g., `HEARTBEAT_INTERVAL="abc"`), the application would completely crash on startup or reload due to an unhandled `ValueError`. This violates "Environment schema validation" and makes the application brittle to manual configuration errors.
**Action:** Introduced a safe integer parser helper `_get_int_env` in `Settings` that catches `ValueError`, logs a warning message, and gracefully falls back to a sensible default. This prevents catastrophic application failure from simple configuration typos and hardens the application's configuration boundaries.

## 2026-05-25 - Error Isolation in Agent Delegation

**Learning:** The `delegate_task_wrapper` tool used for inter-agent communication did not catch unexpected exceptions raised by a target agent's `chat` method (such as an LLM provider timeout or a bug in a sub-agent's tool logic). Because this exception bubbled up, a failure in a single sub-agent would crash the delegating agent's thought process, making the entire swarm fragile to single-node failures.
**Action:** Wrapped the `target_agent.chat()` invocation inside the `delegate_task_wrapper` within a `try/except Exception` block. When an error occurs during delegation, it is now caught and converted into a formatted string (e.g., `"Error: Delegation to ... failed"`). This isolates execution failures, allowing the delegating agent to handle the error gracefully without terminating its own execution cycle.

## 2026-06-05 - Standardize API Error Responses in Configuration Route

**Learning:** The configuration update route (`POST /config`) caught all exceptions generically and returned a 200 OK with `{"status": "error", "message": "..."}`. This bypasses the application's centralized error handler (`global_exception_handler`), violates REST semantics, and produces inconsistent API contracts, as other endpoints return standardized `ErrorResponse` objects with appropriate HTTP status codes (400, 500) upon failure.
**Action:** Refactored `update_config` in `opencore/interface/api.py` to raise standard `HTTPException` instances when it catches a `ValueError` (400) or an unexpected generic `Exception` (500). The `global_exception_handler` now captures these exceptions to enforce uniform schema compliance, improving observability and API boundary clarity.
