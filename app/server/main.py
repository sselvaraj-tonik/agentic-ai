from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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

# Mount your frontend directory (ensure the folder name matches your directory, e.g., "chat-screen")
# html=True automatically serves index.html when you hit the root of this path
app.mount("/chat-screen", StaticFiles(directory="chat-screen", html=True), name="chat-screen")

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
