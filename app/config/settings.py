import os
from enum import Enum
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class LLMProvider(str, Enum):
    OLLAMA = "ollama"
    VLLM = "vllm"

class PersistenceType(str, Enum):
    MEMORY = "memory"
    POSTGRES = "postgres"

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class Settings(BaseSettings):
    # Application Environment
    APP_ENV: Environment = Environment.DEVELOPMENT

    # LLM Configuration
    LLM_PROVIDER: LLMProvider = LLMProvider.OLLAMA

    OLLAMA_MODEL: str = "llama3.1"
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"

    VLLM_MODEL: Optional[str] = None
    VLLM_BASE_URL: Optional[str] = None
    VLLM_API_KEY: str = "EMPTY"

    # API Configuration
    BANK_API_BASE_URL: str
    DRUPAL_FAQ_URL: str
    API_TIMEOUT: int = 10

    # Database Configuration
    DATABASE_URL: str

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
