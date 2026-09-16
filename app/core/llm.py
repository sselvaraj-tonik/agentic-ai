from typing import Optional
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from app.config.settings import settings, LLMProvider

def get_llm(model: Optional[str] = None):
    """
    Returns an instance of the configured LLM based on the LLM_PROVIDER setting.

    Args:
        model: Optional model name override. When None, the provider's default
               (OLLAMA_MODEL / VLLM_MODEL) is used. Lets callers such as the
               supervisor run a lighter, faster model for routing.
    """
    if settings.LLM_PROVIDER == LLMProvider.OLLAMA:
        return ChatOllama(
            model=model or settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=0,
            keep_alive=settings.OLLAMA_KEEP_ALIVE,
        )
    elif settings.LLM_PROVIDER == LLMProvider.VLLM:
        return ChatOpenAI(
            model=model or settings.VLLM_MODEL,
            openai_api_base=settings.VLLM_BASE_URL,
            openai_api_key=settings.VLLM_API_KEY,
            temperature=0,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")


def get_supervisor_llm():
    """
    Returns the LLM used for supervisor routing, resolving the correct
    lightweight model for whichever provider is active.

    This keeps provider switching seamless: each provider defines its own
    optional supervisor model (OLLAMA_SUPERVISOR_MODEL / VLLM_SUPERVISOR_MODEL),
    and each falls back to that provider's main model when unset. Callers don't
    need to know which provider is configured.
    """
    if settings.LLM_PROVIDER == LLMProvider.OLLAMA:
        supervisor_model = settings.OLLAMA_SUPERVISOR_MODEL
    elif settings.LLM_PROVIDER == LLMProvider.VLLM:
        supervisor_model = settings.VLLM_SUPERVISOR_MODEL
    else:
        raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")

    # get_llm() applies the per-provider main-model fallback when this is None.
    return get_llm(model=supervisor_model)
