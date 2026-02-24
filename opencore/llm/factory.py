import os
from .base import LLMProvider
from .openai_compat import OpenAICompatibleProvider
from .anthropic import AnthropicProvider
from .gemini import GeminiProvider


def get_llm_provider(model: str, is_custom_model: bool = False) -> LLMProvider:
    """
    Factory function to get the appropriate LLM provider.
    """

    # Handle prefixes
    if model.startswith("gpt-") or model.startswith("openai/"):
        api_key = os.getenv("OPENAI_API_KEY")
        model_name = model.replace("openai/", "")
        return OpenAICompatibleProvider(model_name=model_name, api_key=api_key)

    elif model.startswith("anthropic/"):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        model_name = model.replace("anthropic/", "")
        return AnthropicProvider(model_name=model_name, api_key=api_key)

    elif model.startswith("gemini/") or model.startswith("google/"):
        api_key = os.getenv("GEMINI_API_KEY")
        return GeminiProvider(model_name=model, api_key=api_key)

    elif model.startswith("groq/"):
        api_key = os.getenv("GROQ_API_KEY")
        model_name = model.replace("groq/", "")
        return OpenAICompatibleProvider(
            model_name=model_name,
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )

    elif model.startswith("xai/"):
        api_key = os.getenv("XAI_API_KEY")
        model_name = model.replace("xai/", "")
        return OpenAICompatibleProvider(
            model_name=model_name,
            api_key=api_key,
            base_url="https://api.x.ai/v1"
        )

    elif model.startswith("dashscope/") or model.startswith("qwen/"):
        # Check for OAuth token first (legacy Qwen logic support)
        oauth_token = os.getenv("QWEN_ACCESS_TOKEN")
        key = oauth_token if oauth_token else os.getenv("DASHSCOPE_API_KEY")

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
        api_key = os.getenv("MISTRAL_API_KEY")
        model_name = model.replace("mistral/", "")
        return OpenAICompatibleProvider(
            model_name=model_name,
            api_key=api_key,
            base_url="https://api.mistral.ai/v1"
        )

    elif model.startswith("ollama/"):
        api_base = os.getenv("OLLAMA_API_BASE", "http://localhost:11434/v1")
        model_name = model.replace("ollama/", "")
        return OpenAICompatibleProvider(
            model_name=model_name,
            api_key="ollama",  # Dummy key required by some clients
            base_url=api_base
        )

    # Fallback to OpenAI if no prefix and looks like GPT
    # Or default to OpenAI compatible if unknown?
    # Let's assume OpenAI compatible for generic usage.
    api_key = os.getenv("OPENAI_API_KEY")
    return OpenAICompatibleProvider(model_name=model, api_key=api_key)
