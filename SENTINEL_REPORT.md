# Sentinel Report: Command Injection in execute_command

**Observation:** The `execute_command` tool in `opencore/tools/base.py` utilized `subprocess.run` with `shell=True`. This allowed the execution of arbitrary shell commands, including chaining commands (e.g., `&&`, `;`) and redirects (`>`), directly from the agent's input.

**Impact:** **Critical**. An attacker (or a compromised/hallucinating agent) could execute arbitrary code on the host system. This included potential for data exfiltration, file system destruction (`rm -rf /`), or installing backdoors.

**Suggested Action:** Modified `execute_command` to use `shlex.split(command)` and `shell=False`. This treats the command string as a single executable with arguments, preventing shell operator injection. Updated the tool description to explicitly state that shell features are not supported.

**Future Benefit:** Significantly reduced attack surface for the agent system. Prevents a large class of RCE vulnerabilities, ensuring that the agent can only execute intended binaries and not arbitrary shell scripts.
