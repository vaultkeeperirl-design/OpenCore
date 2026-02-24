import os
from typing import Dict, Any
from dotenv import load_dotenv, set_key
from opencore.auth import get_auth_status
from opencore.auth.qwen import get_qwen_credentials

# Load environment variables from .env file
load_dotenv()

MODEL_CORRECTIONS = {
    "gemini/gemini-1.5-flash": "gemini/gemini-2.0-flash",
    "gemini/gemini-1.5-flash-latest": "gemini/gemini-2.0-flash",
    "gemini/gemini-1.5-flash-001": "gemini/gemini-2.0-flash",
    "openai/grok-2-1212": "xai/grok-2-vision-1212",
}

# Whitelist of allowed configuration keys to prevent arbitrary env injection
ALLOWED_CONFIG_KEYS = {
    "LLM_MODEL",
    "HEARTBEAT_INTERVAL",
    "VERTEX_PROJECT",
    "VERTEX_LOCATION",
    "OLLAMA_API_BASE",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "MISTRAL_API_KEY",
    "XAI_API_KEY",
    "DASHSCOPE_API_KEY",
    "GEMINI_API_KEY",
    "GROQ_API_KEY",
    "LOG_LEVEL",
    "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET",
    "GOOGLE_REFRESH_TOKEN",
    "ALLOW_UNSAFE_SYSTEM_ACCESS",
}

class Settings:
    def __init__(self):
        self.reload()

    def reload(self):
        load_dotenv(override=True)

        # --- OAuth Credential Injection ---
        # Qwen/DashScope
        qwen_token = get_qwen_credentials()
        if qwen_token:
            # We set a special internal env var for the token
            # We don't overwrite DASHSCOPE_API_KEY directly if it's already set in .env
            # unless we want OAuth to take precedence.
            # Given "User First", if they have OAuth, we should probably use it.
            # However, litellm expects DASHSCOPE_API_KEY.
            # We will set a separate var QWEN_ACCESS_TOKEN to be used in agent logic
            os.environ["QWEN_ACCESS_TOKEN"] = qwen_token

        # Google ADC is automatic via library, but we can log it
        auth_status = get_auth_status()
        if auth_status["google"]:
            # Ensure no conflicting keys if we want to force ADC?
            # Usually keys take precedence, but ADC is a fallback.
            pass

        self.app_env = os.getenv("APP_ENV", "production")

        # Auto-correct known broken model strings
        raw_model = os.getenv("LLM_MODEL")
        self.llm_model = MODEL_CORRECTIONS.get(raw_model, raw_model)

        self.host = os.getenv("HOST", "127.0.0.1")
        self.port = int(os.getenv("PORT", 8000))
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.heartbeat_interval = int(os.getenv("HEARTBEAT_INTERVAL", 3600))

    def update_env(self, updates: Dict[str, Any]):
        """Updates the .env file and reloads configuration."""
        env_path = ".env"
        # Create .env if it doesn't exist
        if not os.path.exists(env_path):
            with open(env_path, "w") as f:
                pass

        # Validate keys against whitelist
        for k in updates.keys():
            if k not in ALLOWED_CONFIG_KEYS:
                raise ValueError(f"Configuration key '{k}' is not allowed.")

        # Update with new values using set_key which preserves comments
        for k, v in updates.items():
            if v is not None:
                val = str(v)
                # Auto-correct known broken model strings before saving
                if k == "LLM_MODEL":
                    val = MODEL_CORRECTIONS.get(val, val)

                # Use python-dotenv's set_key to preserve comments and structure
                try:
                    set_key(env_path, k, val)
                except Exception as e:
                    print(f"Error setting key {k}: {e}")
                    raise e

        # Reload runtime settings
        self.reload()

    @property
    def is_dev(self) -> bool:
        return self.app_env == "development"

    @property
    def vertex_project(self) -> str:
        return os.getenv("VERTEX_PROJECT", "")

    @property
    def vertex_location(self) -> str:
        return os.getenv("VERTEX_LOCATION", "")

    @property
    def ollama_api_base(self) -> str:
        return os.getenv("OLLAMA_API_BASE", "")

    @property
    def has_openai_key(self) -> bool:
        return bool(os.getenv("OPENAI_API_KEY"))

    @property
    def has_anthropic_key(self) -> bool:
        return bool(os.getenv("ANTHROPIC_API_KEY"))

    @property
    def has_mistral_key(self) -> bool:
        return bool(os.getenv("MISTRAL_API_KEY"))

    @property
    def has_xai_key(self) -> bool:
        return bool(os.getenv("XAI_API_KEY"))

    @property
    def has_dashscope_key(self) -> bool:
        return bool(os.getenv("DASHSCOPE_API_KEY"))

    @property
    def has_gemini_key(self) -> bool:
        return bool(os.getenv("GEMINI_API_KEY"))

    @property
    def has_groq_key(self) -> bool:
        return bool(os.getenv("GROQ_API_KEY"))

    @property
    def allow_unsafe_system_access(self) -> bool:
        """
        Returns True if the system is configured to allow unrestricted file access
        and potentially dangerous shell commands.
        """
        val = os.getenv("ALLOW_UNSAFE_SYSTEM_ACCESS", "false").lower()
        return val in ("true", "1", "yes")

settings = Settings()
