from langchain_core.tools import tool
import logging
from app.core.database import get_vector_store
from app.modules.common.schemas import SearchCompanyKnowledgeInput

logger = logging.getLogger(__name__)

vector_store = None

@tool("search_company_knowledge", args_schema=SearchCompanyKnowledgeInput)
def search_company_knowledge(query: str) -> str:
    """
    Searches the company knowledge base (FAQs, policies) for the given query.
    Returns the top 3 most relevant results formatted as a readable string.
    """
    global vector_store
    if vector_store is None:
        try:
            vector_store = get_vector_store()
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            return "Error: Company knowledge base is currently unavailable."

    try:
        # Perform similarity search, returning top 3 results
        results = vector_store.similarity_search(query, k=3)

        if not results:
            return "No relevant company knowledge found for your query."

        # Format the results into a readable string
        formatted_results = []
        for i, doc in enumerate(results, start=1):
            title = doc.metadata.get('title', f"Result {i}")
            formatted_results.append(f"### {title}\n{doc.page_content}")

        return "\n\n".join(formatted_results)

    except Exception as e:
        logger.error(f"Error during company knowledge search for query '{query}': {e}")
        return f"An error occurred while searching the knowledge base: {str(e)}"
