from workers.providers.base_provider import BaseProvider
from workers.providers.vllm_provider import VLLMProvider
from workers.providers.gemini_provider import GeminiProvider
from workers.providers.llama_cpp_provider import LlamaCPPProvider

def get_provider(provider_type: str) -> BaseProvider:
    """
    Instantiates and returns the correct LLM provider based on the type.
    """
    if provider_type == "vllm":
        return VLLMProvider()
    elif provider_type == "gemini":
        return GeminiProvider()
    elif provider_type == "llama_cpp":
        return LlamaCPPProvider()
    else:
        raise ValueError(f"Unsupported provider type: '{provider_type}'")