from fastapi import FastAPI
from app.config.settings import settings
from app.config.logging import setup_logging
from app.server.routers import chat, ingest

# Setup logging
setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    description="An Open Source Agentic AI for Banking Customer Support",
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# Include Routers
app.include_router(chat.router)
app.include_router(ingest.router)

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
