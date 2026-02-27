from langchain_ollama import ChatOllama
from app.config.settings import settings

def get_llm():
    """
    Returns an instance of the configured LLM.
    """
    return ChatOllama(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=0,  # Deterministic for routing/reasoning
    )
