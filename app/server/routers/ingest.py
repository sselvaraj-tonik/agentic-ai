from fastapi import APIRouter, HTTPException, status
from app.scripts.ingest import ingest_faqs

router = APIRouter(
    prefix="/ingest",
    tags=["Ingestion"],
    responses={404: {"description": "Not found"}},
)

@router.post("/faqs", status_code=status.HTTP_200_OK)
def trigger_faq_ingestion() -> dict:
    """
    Triggers the standalone ingestion script to fetch FAQs from the mock
    Drupal CMS endpoint, chunk the text, embed it via Ollama, and store
    it in the PostgreSQL pgvector database.

    Returns:
        dict: The result of the ingestion process, including status
              and number of chunks processed.
    """
    result = ingest_faqs()

    # Check if there was an error during ingestion and return appropriate status
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message"))

    return result
