from workers.providers.base_provider import BaseProvider
from workers.providers.vllm_provider import VLLMProvider
from workers.providers.gemini_provider import GeminiProvider

def get_provider(provider_type: str) -> BaseProvider:
    """
    Instantiates and returns the correct LLM provider based on the type.
    """
    if provider_type == "vllm":
        return VLLMProvider()
    elif provider_type == "gemini":
        return GeminiProvider()
    else:
        raise ValueError(f"Unsupported provider type: '{provider_type}'")