import os
from enum import Enum
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class LLMProvider(str, Enum):
    OLLAMA = "ollama"
    VLLM = "vllm"

class PersistenceType(str, Enum):
    MEMORY = "memory"
    POSTGRES = "postgres"

class Environment(str, Enum):
    DEVELOPMENT = "development"
    SIT = "sit"
    UAT = "uat"
    PRODUCTION = "production"

class Settings(BaseSettings):
    # Application Environment
    APP_ENV: Environment = Environment.DEVELOPMENT

    # LLM Configuration
    LLM_PROVIDER: LLMProvider = LLMProvider.OLLAMA

    # ── Ollama ──────────────────────────────────────────────
    OLLAMA_MODEL: str = "llama3.1"
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    # Embedding model served by Ollama (used for FAQ vector search).
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"

    # Optional lighter model for the supervisor's routing decision (Ollama).
    # Routing is a lightweight 4-way classification, so a smaller/faster model
    # here cuts per-request latency. When None, falls back to OLLAMA_MODEL.
    OLLAMA_SUPERVISOR_MODEL: Optional[str] = None

    # How long Ollama keeps a model resident in GPU memory after a call.
    # -1 = keep loaded indefinitely (avoids reload thrash when alternating
    # between the supervisor and agent models). 0 = unload immediately.
    OLLAMA_KEEP_ALIVE: int = -1

    # ── vLLM ────────────────────────────────────────────────
    VLLM_MODEL: Optional[str] = None
    VLLM_BASE_URL: Optional[str] = None
    VLLM_API_KEY: str = "EMPTY"
    # Embedding model served by the (OpenAI-compatible) vLLM endpoint.
    # Must be an embedding model your vLLM server actually serves.
    VLLM_EMBED_MODEL: str = "text-embedding-3-small"

    # Optional lighter model for the supervisor's routing decision (vLLM).
    # Must be a model your vLLM server actually serves. When None, falls
    # back to VLLM_MODEL.
    VLLM_SUPERVISOR_MODEL: Optional[str] = None

    # API Configuration
    BANK_API_BASE_URL: str
    API_TIMEOUT: int = 10

    # Database Configuration
    DATABASE_URL: str

    # Knowledge Base Retrieval
    # Number of FAQ chunks to retrieve, and the minimum normalized
    # relevance score (0-1) a chunk must clear to be considered a match.
    # Chunks below the threshold are discarded so off-topic or vague
    # queries return "no relevant knowledge" instead of arbitrary FAQs.
    KB_SEARCH_TOP_K: int = 3
    KB_RELEVANCE_THRESHOLD: float = 0.4

    # ── Inference funnel ────────────────────────────────────
    # Order of matcher tiers. Change/reorder freely (JSON list in env).
    # 'spell' is a pre-processor (rewrites the query); 'fallback' is terminal
    # and is appended automatically if omitted. Valid names are the keys in
    # app/modules/knowledge/pipeline.REGISTRY.
    INFERENCE_ORDER: List[str] = [
        "spell", "small_talk", "ontology", "faq", "open_text", "fallback"
    ]

    # Small talk (semantic match, verbatim answer). Higher = stricter.
    SMALLTALK_THRESHOLD: float = 0.62

    # FAQ (semantic match over question + variants, verbatim answer).
    FAQ_TOP_K: int = 3
    FAQ_THRESHOLD: float = 0.5
    # Which Answers[] channel to render for Template FAQs ("default", "w", ...).
    FAQ_ANSWER_CHANNEL: str = "default"

    # Open text (RAG / LLM-generated).
    OPENTEXT_TOP_K: int = 4
    OPENTEXT_THRESHOLD: float = 0.4

    # Ontology "did you mean" — trigram similarity floor for a bare utterance.
    ONTOLOGY_TRGM_THRESHOLD: float = 0.6

    # Persistence Configuration
    PERSISTENCE_TYPE: PersistenceType = PersistenceType.MEMORY

    # Security & Compliance
    ENABLE_PII_MASKING: bool = False

    # Application Configuration
    APP_NAME: str = "Banking Agent AI"
    APP_VERSION: str = "1.2.0"
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=f".env.{os.getenv('APP_ENV', 'development')}",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Reload settings to ensure the correct .env file is used
settings = Settings()
