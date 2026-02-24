## 2026-02-21 - Blocking I/O in Async Endpoint

**Observation:** The `chat` endpoint in `opencore/interface/api.py` is defined as `async def` but calls the synchronous `swarm.chat` method (which uses the blocking `OpenAI` client). This blocks the main event loop during API calls, freezing the server for other requests.
**Action:** Changed `async def chat` to `def chat`. This instructs FastAPI to run the endpoint in a threadpool, preventing the blocking call from freezing the main loop.

## 2026-02-21 - Path Traversal in File Tools

**Vulnerability:** The default file manipulation tools (`read_file`, `write_file`, `list_files`) allowed path traversal via `../` or absolute paths, enabling agents to access files outside the project directory (e.g., `/etc/passwd`).
**Learning:** Providing file system access to agents requires strict sandboxing. Relying on "good intentions" of the LLM is not security. `os.path.commonpath` combined with `os.path.realpath` is a robust way to enforce directory confinement in Python.
**Prevention:** Implemented `_is_safe_path` check in `opencore/tools/base.py` that resolves symlinks and verifies the target path is within the current working directory.

## 2026-02-21 - Command Injection in Agent Tools

**Vulnerability:** The `execute_command` tool in `opencore/tools/base.py` used `shell=True`, allowing command injection (e.g., `echo test > injected.txt`).
**Learning:** `shell=True` is fundamentally insecure for agent tools that accept arbitrary strings from an LLM. Agents often output unexpected characters or can be prompt-injected to run malicious commands.
**Prevention:** Replaced `shell=True` with `shell=False` and used `shlex.split(command)` to parse arguments securely. Updated tool description to explicitly disallow shell features.

## 2026-02-24 - Unrestricted Environment Configuration

**Vulnerability:** The `POST /config` endpoint allowed unauthenticated users to inject arbitrary keys into the `.env` file via `Settings.update_env`, potentially leading to RCE or system compromise.
**Learning:** Never trust input for configuration updates. Configuration endpoints are high-value targets and must be strictly validated. Whitelisting is the only safe approach for runtime configuration updates.
**Prevention:** Implemented a strict whitelist `ALLOWED_CONFIG_KEYS` in `opencore/config.py` and enforced validation in `Settings.update_env`.
