## 2026-02-21 - Blocking I/O in Async Endpoint

**Observation:** The `chat` endpoint in `opencore/interface/api.py` is defined as `async def` but calls the synchronous `swarm.chat` method (which uses the blocking `OpenAI` client). This blocks the main event loop during API calls, freezing the server for other requests.
**Action:** Changed `async def chat` to `def chat`. This instructs FastAPI to run the endpoint in a threadpool, preventing the blocking call from freezing the main loop.

## 2026-02-21 - Path Traversal in File Tools

**Vulnerability:** The default file manipulation tools (`read_file`, `write_file`, `list_files`) allowed path traversal via `../` or absolute paths, enabling agents to access files outside the project directory (e.g., `/etc/passwd`).
**Learning:** Providing file system access to agents requires strict sandboxing. Relying on "good intentions" of the LLM is not security. `os.path.commonpath` combined with `os.path.realpath` is a robust way to enforce directory confinement in Python.
**Prevention:** Implemented `_is_safe_path` check in `opencore/tools/base.py` that resolves symlinks and verifies the target path is within the current working directory.
