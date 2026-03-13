from typing import Dict, Any
from opencore.config import settings, ALLOWED_CONFIG_KEYS

class ConfigService:
    def __init__(self, swarm=None):
        """
        Initializes the ConfigService.
        :param swarm: An optional reference to the Swarm instance to update its settings when config changes.
        """
        self.swarm = swarm

    def get_masked_config(self) -> Dict[str, Any]:
        """
        Returns the current configuration, masked for API consumption.
        Reloads the environment state first to ensure it's up to date.
        """
        settings.reload()
        return {
            "LLM_MODEL": settings.llm_model or "gpt-4o",
            "HEARTBEAT_INTERVAL": str(settings.heartbeat_interval),
            "VERTEX_PROJECT": settings.vertex_project,
            "VERTEX_LOCATION": settings.vertex_location,
            "OLLAMA_API_BASE": settings.ollama_api_base,
            # Boolean flags for sensitive keys
            "HAS_OPENAI_KEY": settings.has_openai_key,
            "HAS_ANTHROPIC_KEY": settings.has_anthropic_key,
            "HAS_MISTRAL_KEY": settings.has_mistral_key,
            "HAS_XAI_KEY": settings.has_xai_key,
            "HAS_DASHSCOPE_KEY": settings.has_dashscope_key,
            "HAS_GEMINI_KEY": settings.has_gemini_key,
            "HAS_GROQ_KEY": settings.has_groq_key,
        }

    def update_config(self, updates: Dict[str, Any]) -> None:
        """
        Filters the updates against the allowed keys and updates the environment.
        Updates the swarm settings if a swarm instance was provided.
        """
        valid_config = {k: v for k, v in updates.items() if k in ALLOWED_CONFIG_KEYS}

        settings.update_env(valid_config)

        if self.swarm:
            self.swarm.update_settings()
