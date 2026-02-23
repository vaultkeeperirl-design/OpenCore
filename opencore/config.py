import os
from dotenv import load_dotenv
from opencore.auth import get_auth_status
from opencore.auth.qwen import get_qwen_credentials

# Load environment variables from .env file
load_dotenv()

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
        self.llm_model = os.getenv("LLM_MODEL")

        # Auto-correct known broken model strings from older configs
        if self.llm_model == "gemini/gemini-1.5-flash":
            self.llm_model = "gemini/gemini-1.5-flash-latest"
        elif self.llm_model == "openai/grok-2-1212":
            self.llm_model = "xai/grok-2-vision-1212"

        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", 8000))
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.heartbeat_interval = int(os.getenv("HEARTBEAT_INTERVAL", 3600))

    @property
    def is_dev(self) -> bool:
        return self.app_env == "development"

settings = Settings()
