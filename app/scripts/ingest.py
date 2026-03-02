import requests
import logging
from bs4 import BeautifulSoup
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.config.settings import settings
from app.core.database import get_vector_store

logger = logging.getLogger(__name__)

def ingest_faqs() -> dict:
    """
    Fetches JSON data from the Drupal FAQ endpoint, strips HTML,
    chunks the text, generates embeddings, and saves them to PostgreSQL.

    Returns:
        dict: A dictionary indicating the status and number of chunks processed.
    """
    try:
        logger.info(f"Fetching FAQs from {settings.DRUPAL_FAQ_URL}")
        # Fetch data from mock Drupal JSON:API endpoint
        response = requests.get(settings.DRUPAL_FAQ_URL, timeout=settings.API_TIMEOUT)
        response.raise_for_status()
        data = response.json()

        # Ensure 'data' exists in the response
        nodes = data.get("data", [])
        if not nodes:
            logger.warning("No FAQ data found in the response.")
            return {"status": "success", "chunks_processed": 0, "message": "No data found."}

        documents = []
        # Process each node
        for node in nodes:
            # Depending on JSON:API structure, attributes hold the actual data
            attributes = node.get("attributes", {})
            title = attributes.get("title", "")

            # The body is typically an object with a 'value' field containing HTML
            body_obj = attributes.get("body", {})
            body_html = body_obj.get("value", "") if isinstance(body_obj, dict) else str(body_obj)

            if not body_html:
                continue

            # Strip HTML using BeautifulSoup
            soup = BeautifulSoup(body_html, "html.parser")
            clean_text = soup.get_text(separator=" ", strip=True)

            # Combine title and body for better context
            full_text = f"Title: {title}\n\nContent: {clean_text}"

            # Add metadata if available (like id or url)
            metadata = {
                "id": node.get("id", ""),
                "title": title,
                "type": node.get("type", "faq")
            }

            documents.append(Document(page_content=full_text, metadata=metadata))

        if not documents:
            logger.warning("No content extracted from the fetched nodes.")
            return {"status": "success", "chunks_processed": 0, "message": "No valid content found."}

        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            overlap=200
        )
        split_docs = text_splitter.split_documents(documents)

        # Initialize the vector store and add documents
        vector_store = get_vector_store()

        # NOTE: If we want to replace the entire store each time, we could potentially drop the collection.
        # However, for this task, we will simply add the documents. In a real-world scenario, you might
        # want to check for updates or clear old vectors.
        vector_store.add_documents(split_docs)

        chunks_count = len(split_docs)
        logger.info(f"Successfully processed and embedded {chunks_count} chunks.")

        return {
            "status": "success",
            "chunks_processed": chunks_count,
            "message": "FAQs ingested successfully."
        }

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching FAQ data from Drupal: {e}")
        return {"status": "error", "message": f"Network error fetching FAQs: {str(e)}"}
    except Exception as e:
        logger.error(f"Error during FAQ ingestion process: {e}")
        return {"status": "error", "message": f"Ingestion error: {str(e)}"}
