import os
import re
import shlex
import subprocess
from opencore.core.agent import Agent
from opencore.config import settings


def _is_safe_path(path: str) -> bool:
    """
    Checks if the path is within the current working directory.
    Prevents path traversal attacks by resolving symlinks and absolute paths.
    """
    if settings.allow_unsafe_system_access:
        return True

    try:
        base_dir = os.path.realpath(os.getcwd())
        # Resolve the target path, including symlinks
        target_path = os.path.realpath(path)
        # Check if the target path starts with the base directory
        return os.path.commonpath([base_dir, target_path]) == base_dir
    except Exception:
        # If any error occurs (e.g. ValueError on Windows different drives),
        # assume unsafe
        return False


def execute_command(command: str) -> str:
    """Executes a shell command and returns the output."""
    # Global Safety Guard: Block catastrophic deletion commands
    # This applies regardless of ALLOW_UNSAFE_SYSTEM_ACCESS

    # Regex patterns for dangerous commands
    # We use (\s+|$) to ensure we are matching the exact path and not a prefix (e.g., /tmp)
    dangerous_patterns = [
        # rm -rf / or rm -rf /*
        r"rm\s+(-[rRfF]{2,}|-[rR]\s+-[fF]|-[fF]\s+-[rR])\s+(/|/\*)(\s+|$)",
        # rd /s /q c:\ or rd /s /q /
        r"rd\s+(/s\s+/q|/q\s+/s)\s+(c:\\|/)(\s+|$)",
    ]

    cmd_lower = command.lower().strip()
    for pattern in dangerous_patterns:
        if re.search(pattern, cmd_lower):
             return f"Error: Command blocked by safety guard. usage of dangerous pattern '{pattern}' is not allowed."

    try:
        if settings.allow_unsafe_system_access:
            # Unrestricted access: shell=True allows pipes, redirects, &&, etc.
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=30
            )
        else:
            # Security: Use shlex.split and shell=False to prevent injection
            # This prevents chaining commands with &&, |, ;, etc.
            args = shlex.split(command)

            # Sentinel Security Patch: Validate arguments for path traversal
            # Iterate over ALL arguments (including the command itself) to ensure no files outside CWD are accessed
            # This prevents executing binaries by absolute path (e.g. /bin/ls) and path traversal in args
            for arg in args:
                # Check if argument resolves to an unsafe path
                # Note: This might block some legitimate non-path arguments if they happen to look like paths
                # but resolve to something outside CWD (e.g. absolute paths that exist).
                # This is a necessary trade-off for security in restricted mode.
                if not _is_safe_path(arg):
                     return f"Error: Access denied - Path traversal detected in argument '{arg}'."

            result = subprocess.run(
                args, shell=False, capture_output=True, text=True, timeout=30
            )

        output = result.stdout
        if result.stderr:
            output += f"\nError: {result.stderr}"
        return output
    except Exception as e:
        return f"Error executing command: {str(e)}"


def read_file(filepath: str) -> str:
    """Reads the content of a file."""
    if not _is_safe_path(filepath):
        return "Error: Access denied - Path traversal detected."

    try:
        with open(filepath, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


def write_file(filepath: str, content: str) -> str:
    """Writes content to a file."""
    if not _is_safe_path(filepath):
        return "Error: Access denied - Path traversal detected."

    try:
        with open(filepath, "w") as f:
            f.write(content)
        return f"File '{filepath}' written successfully."
    except Exception as e:
        return f"Error writing file: {str(e)}"


def list_files(directory: str = ".") -> str:
    """Lists files in a directory."""
    if not _is_safe_path(directory):
        return "Error: Access denied - Path traversal detected."

    try:
        files = os.listdir(directory)
        return "\n".join(files)
    except Exception as e:
        return f"Error listing files: {str(e)}"


# Schemas
execute_command_schema = {
    "type": "function",
    "function": {
        "name": "execute_command",
        "description": (
            "Executes a single shell command. "
            "Pipes, redirects, and shell operators (&&, ;, |) NOT supported."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The command to execute."
                }
            },
            "required": ["command"]
        }
    }
}

read_file_schema = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Reads a file from the filesystem.",
        "parameters": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "The path to the file."
                }
            },
            "required": ["filepath"]
        }
    }
}

write_file_schema = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": "Writes content to a file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "The path to the file."
                },
                "content": {
                    "type": "string",
                    "description": "The content to write."
                }
            },
            "required": ["filepath", "content"]
        }
    }
}

list_files_schema = {
    "type": "function",
    "function": {
        "name": "list_files",
        "description": "Lists files in a directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "The directory path (default: .)."
                }
            },
            "required": []
        }
    }
}


def register_base_tools(agent: Agent):
    """Registers the base tools to an agent."""
    agent.register_tool(execute_command, execute_command_schema)
    agent.register_tool(read_file, read_file_schema)
    agent.register_tool(write_file, write_file_schema)
    agent.register_tool(list_files, list_files_schema)
