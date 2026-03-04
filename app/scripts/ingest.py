import requests
import logging
from bs4 import BeautifulSoup
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config.settings import settings
from app.core.database import get_vector_store

logger = logging.getLogger(__name__)

def ingest_faqs() -> dict:
    """
    Fetches JSON data from the Drupal FAQ endpoint (handling pagination), 
    strips HTML, chunks the text, and safely upserts them to PostgreSQL.
    """
    try:
        logger.info(f"Starting FAQ ingestion from {settings.DRUPAL_FAQ_URL}")
        
        documents = []
        next_url = settings.DRUPAL_FAQ_URL
        
        # 1. Handle Drupal Pagination (Fetch ALL pages)
        while next_url:
            response = requests.get(next_url, timeout=settings.API_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            nodes = data.get("data", [])
            for node in nodes:
                attributes = node.get("attributes", {})
                title = attributes.get("title", "")
                
                body_obj = attributes.get("body", {})
                body_html = body_obj.get("value", "") if isinstance(body_obj, dict) else str(body_obj)
                
                if not body_html:
                    continue
                    
                # Strip HTML
                soup = BeautifulSoup(body_html, "html.parser")
                clean_text = soup.get_text(separator=" ", strip=True)
                
                full_text = f"Title: {title}\n\nContent: {clean_text}"
                
                metadata = {
                    "id": node.get("id", ""),
                    "title": title,
                    "type": node.get("type", "faq")
                }
                documents.append(Document(page_content=full_text, metadata=metadata))
            
            # Check for the next page link in Drupal's JSON:API response
            links = data.get("links", {})
            next_link_obj = links.get("next", {})
            next_url = next_link_obj.get("href") if isinstance(next_link_obj, dict) else None

        if not documents:
            logger.warning("No FAQ data found.")
            return {"status": "success", "chunks_processed": 0, "message": "No data found."}

        # 2. Fix the LangChain parameter typo
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200  # Fixed from 'overlap'
        )
        split_docs = text_splitter.split_documents(documents)
        
        # 3. Handle Database Updates cleanly
        vector_store = get_vector_store()
        
        # Optional but highly recommended: Drop the existing collection data 
        # before inserting the fresh sync to prevent duplicate bloat.
        # This assumes you are using PGVector.
        vector_store.create_tables_if_not_exists()
        try:
            # vector_store.drop_tables()
            vector_store.create_tables_if_not_exists()
        except Exception as db_e:
            logger.warning(f"Could not drop tables, appending instead. Error: {db_e}")

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