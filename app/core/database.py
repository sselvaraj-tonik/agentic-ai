from langchain_postgres.vectorstores import PGVector
from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings
from app.config.settings import settings, LLMProvider

def get_vector_store() -> PGVector:
    """
    Initializes and returns a LangChain PGVector store connected
    to the PostgreSQL database.
    """
    if settings.LLM_PROVIDER == LLMProvider.OLLAMA:
        embeddings = OllamaEmbeddings(
            model="nomic-embed-text",
            base_url=settings.OLLAMA_BASE_URL
        )
    else:
        # Default to OpenAI-compatible embeddings for vLLM or other providers
        # Note: vLLM usually serves chat models, embedding models might need a different base URL
        # or a different service altogether. Assuming OpenAI compatibility for now.
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small", # Or whatever model is served
            openai_api_base=settings.VLLM_BASE_URL,
            openai_api_key=settings.VLLM_API_KEY,
        )

    # Initialize the PGVector store
    vector_store = PGVector(
        embeddings=embeddings,
        collection_name="company_faqs",
        connection=settings.DATABASE_URL,
        use_jsonb=True,
    )

    vector_store.create_tables_if_not_exists()

    return vector_store
