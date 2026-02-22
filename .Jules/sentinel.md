## 2026-02-21 - Blocking I/O in Async Endpoint

**Observation:** The `chat` endpoint in `opencore/interface/api.py` is defined as `async def` but calls the synchronous `swarm.chat` method (which uses the blocking `OpenAI` client). This blocks the main event loop during API calls, freezing the server for other requests.
**Action:** Changed `async def chat` to `def chat`. This instructs FastAPI to run the endpoint in a threadpool, preventing the blocking call from freezing the main loop.

## 2026-02-22 - Inconsistent Logging & Missing Timeouts in Core Agent

**Observation:** The `Agent` class in `opencore/core/agent.py` uses `print` and `traceback.print_exc()` instead of the standard `logging` module, violating project guidelines. Additionally, the `completion` call lacks a `timeout` parameter, posing a risk of hanging processes.
**Action:** Recommend refactoring `agent.py` to use `logging.getLogger(__name__)` and add a `timeout=60` parameter to `completion`.
