# Architect's Journal

## 2025-02-18 - Centralized Configuration

**Learning:** Configuration was scattered across `os.getenv` calls in multiple files (`agent.py`, `swarm.py`, `middleware.py`), leading to hidden defaults and potential inconsistencies. `load_dotenv` was called in library code (`agent.py`), causing side effects on import.
**Action:** Created `opencore/config.py` with a `Settings` class to centralize environment variable loading and defaults. Refactored `agent.py`, `swarm.py`, `middleware.py`, and `main.py` to use this single source of truth. Updated tests to mock the configuration object.
