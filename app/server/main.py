from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os
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

# Add CORS Middleware to support local file testing and avoid CORS issues
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(chat.router)
app.include_router(ingest.router)

@app.get("/html", response_class=HTMLResponse)
def read_root():
    """Serves the chat interface HTML page."""
    html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../chat.html"))
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h3>chat.html not found</h3>"

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
