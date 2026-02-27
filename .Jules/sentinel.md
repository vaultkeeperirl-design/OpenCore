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

## 2026-02-27 - Unlimited Client-Side File Processing

**Observation:** The `ChatInterface` component allows users to drag and drop files of any size. The browser attempts to read the entire file into memory as a Base64 string via `FileReader`. Large files (e.g., >50MB) can cause the browser tab to freeze or crash due to memory exhaustion. Additionally, sending massive payloads to the backend without size validation can lead to server-side memory pressure or denial of service.
**Action:** Recommended implementation of client-side file size check (e.g., 10MB limit) in the `onDrop` handler and `handleSubmit` function to prevent browser crashes and backend DOS.

## 2026-03-05 - Configurable Agent Memory Limits

**Observation:** The `MAX_HISTORY` constant was hardcoded to 100 in `opencore/core/agent.py`. This rigid limit prevented users from leveraging larger context windows (e.g., Gemini 1.5 Pro) or constraining memory for resource-constrained environments.
**Action:** Replaced the hardcoded constant with a configurable `MAX_HISTORY` setting (defaulting to 100). This allows dynamic adjustment of agent memory capacity via environment variables, improving flexibility and scalability.

## 2026-03-08 - Strict API Payload Validation

**Observation:** The `chat` endpoint accepted attachments as loose dictionaries without validating required fields (`name`, `type`). A malformed payload could cause a `KeyError` deep in the agent logic, resulting in a 500 Internal Server Error.
**Action:** Implemented a strict Pydantic `Attachment` model in `ChatRequest` to enforce schema validation at the API boundary.
**Future Benefit:** Prevents server crashes due to malformed client requests, providing clear 422 validation errors instead of opaque 500 system errors.

## 2026-03-10 - Unlimited File Read Risk

**Observation:** The `read_file` tool in `opencore/tools/base.py` read the entire file content into memory without any size limit. A malicious or accidental request to read a massive file (e.g., database dump or large log) could cause memory exhaustion and crash the worker process.
**Action:** Implemented a strict 10MB limit (`MAX_READ_SIZE`) in `read_file`. Files exceeding this limit are now truncated, and a warning message `[...File truncated...]` is appended to the output to inform the agent.
**Future Benefit:** Protects the system from Out-Of-Memory (OOM) crashes and denial-of-service scenarios caused by file system operations.
