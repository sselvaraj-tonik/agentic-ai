from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from app.config.settings import settings, LLMProvider

def get_llm():
    """
    Returns an instance of the configured LLM based on the LLM_PROVIDER setting.
    """
    if settings.LLM_PROVIDER == LLMProvider.OLLAMA:
        return ChatOllama(
            model=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=0,
        )
    elif settings.LLM_PROVIDER == LLMProvider.VLLM:
        return ChatOpenAI(
            model=settings.VLLM_MODEL,
            openai_api_base=settings.VLLM_BASE_URL,
            openai_api_key=settings.VLLM_API_KEY,
            temperature=0,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")
