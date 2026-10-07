from functools import lru_cache

from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings

from app.config.settings import settings, LLMProvider


@lru_cache(maxsize=1)
def _client():
    if settings.LLM_PROVIDER == LLMProvider.OLLAMA:
        return OllamaEmbeddings(
            model=settings.OLLAMA_EMBED_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
        )
    return OpenAIEmbeddings(
        model=settings.VLLM_EMBED_MODEL,
        openai_api_base=settings.VLLM_BASE_URL,
        openai_api_key=settings.VLLM_API_KEY,
    )


def embed_query(text: str) -> list[float]:
    return _client().embed_query(text)
