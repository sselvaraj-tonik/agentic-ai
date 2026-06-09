from langchain_postgres.vectorstores import PGVector
from langchain_ollama import OllamaEmbeddings
from app.config.settings import settings

def get_vector_store() -> PGVector:
    """
    Initializes and returns a LangChain PGVector store connected
    to the PostgreSQL database.

    Returns:
        PGVector: A vector store instance using Ollama embeddings
        and connected to the DATABASE_URL.
    """
    # Initialize the Ollama Embeddings model as required
    embeddings = OllamaEmbeddings(
        model="nomic-embed-text",
        base_url=settings.OLLAMA_BASE_URL
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
