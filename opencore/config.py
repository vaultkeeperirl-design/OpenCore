import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    def __init__(self):
        self.reload()

    def reload(self):
        load_dotenv(override=True)
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
