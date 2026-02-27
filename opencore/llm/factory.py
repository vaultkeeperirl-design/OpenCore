import os
from typing import List
from .base import LLMProvider
from .openai_compat import OpenAICompatibleProvider
from .anthropic import AnthropicProvider
from .gemini import GeminiProvider
from opencore.config import settings


def is_provider_available(model: str) -> bool:
    """Checks if the provider for the given model is configured."""
    if model.startswith("gpt-") or model.startswith("openai/"):
        return settings.has_openai_key
    elif model.startswith("anthropic/"):
        return settings.has_anthropic_key
    elif model.startswith("gemini/") or model.startswith("google/"):
        return settings.has_gemini_key
    elif model.startswith("groq/"):
        return settings.has_groq_key
    elif model.startswith("xai/"):
        return settings.has_xai_key
    elif model.startswith("dashscope/") or model.startswith("qwen/"):
        return settings.has_dashscope_key
    elif model.startswith("mistral/"):
        return settings.has_mistral_key
    elif model.startswith("ollama/"):
        # Only considered available if explicitly configured
        return bool(settings.ollama_api_base)

    # Fallback assumes OpenAI compatible
    return settings.has_openai_key


def get_available_model_list() -> List[str]:
    """Returns a list of example models for configured providers."""
    models = []
    if settings.has_openai_key:
        models.extend(["openai/gpt-4o", "openai/gpt-3.5-turbo"])
    if settings.has_anthropic_key:
        models.extend(["anthropic/claude-3-opus", "anthropic/claude-3-sonnet"])
    if settings.has_gemini_key:
        models.extend(["gemini/gemini-1.5-pro", "gemini/gemini-1.5-flash"])
    if settings.has_groq_key:
        models.extend(["groq/llama3-8b-8192", "groq/mixtral-8x7b-32768"])
    if settings.has_xai_key:
        models.extend(["xai/grok-2-vision-1212"])
    if settings.has_dashscope_key:
        models.extend(["dashscope/qwen-turbo", "dashscope/qwen-plus"])
    if settings.has_mistral_key:
        models.extend(["mistral/mistral-large-latest"])
    if settings.ollama_api_base:
        models.append("ollama/llama3")
    return models


def get_llm_provider(model: str, is_custom_model: bool = False) -> LLMProvider:
    """
    Factory function to get the appropriate LLM provider.
    """

    # Handle prefixes
    if model.startswith("gpt-") or model.startswith("openai/"):
        api_key = settings.openai_api_key
        model_name = model.replace("openai/", "")
        return OpenAICompatibleProvider(model_name=model_name, api_key=api_key)

    elif model.startswith("anthropic/"):
        api_key = settings.anthropic_api_key
        model_name = model.replace("anthropic/", "")
        return AnthropicProvider(model_name=model_name, api_key=api_key)

    elif model.startswith("gemini/") or model.startswith("google/"):
        api_key = settings.gemini_api_key
        return GeminiProvider(model_name=model, api_key=api_key)

    elif model.startswith("groq/"):
        api_key = settings.groq_api_key
        model_name = model.replace("groq/", "")
        return OpenAICompatibleProvider(
            model_name=model_name,
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )

    elif model.startswith("xai/"):
        api_key = settings.xai_api_key
        model_name = model.replace("xai/", "")
        return OpenAICompatibleProvider(
            model_name=model_name,
            api_key=api_key,
            base_url="https://api.x.ai/v1"
        )

    elif model.startswith("dashscope/") or model.startswith("qwen/"):
        # Check for OAuth token first (legacy Qwen logic support)
        oauth_token = settings.qwen_access_token
        key = oauth_token if oauth_token else settings.dashscope_api_key

        if model.startswith("dashscope/"):
            model_name = model.replace("dashscope/", "")
        else:
            model_name = model.replace("qwen/", "")

        # Use Portal API for OAuth, or DashScope compatible mode for Key
        base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        if oauth_token:
            base_url = "https://portal.qwen.ai/v1"

        return OpenAICompatibleProvider(
            model_name=model_name,
            api_key=key,
            base_url=base_url
        )

    elif model.startswith("mistral/"):
        api_key = settings.mistral_api_key
        model_name = model.replace("mistral/", "")
        return OpenAICompatibleProvider(
            model_name=model_name,
            api_key=api_key,
            base_url="https://api.mistral.ai/v1"
        )

    elif model.startswith("ollama/"):
        api_base = settings.ollama_api_base
        if api_base:
            # Auto-append /v1 if missing
            # First remove any trailing slash to avoid double slashes or logic errors
            clean_base = api_base.rstrip("/")
            if not clean_base.endswith("/v1"):
                api_base = f"{clean_base}/v1"
            else:
                api_base = clean_base
        else:
            api_base = "http://localhost:11434/v1"

        model_name = model.replace("ollama/", "")
        return OpenAICompatibleProvider(
            model_name=model_name,
            api_key="ollama",  # Dummy key required by some clients
            base_url=api_base
        )

    # Fallback to OpenAI if no prefix and looks like GPT
    # Or default to OpenAI compatible if unknown?
    # Let's assume OpenAI compatible for generic usage.
    api_key = settings.openai_api_key
    return OpenAICompatibleProvider(model_name=model, api_key=api_key)
