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
