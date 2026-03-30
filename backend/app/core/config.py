"""
Application configuration — loaded from environment variables via pydantic-settings.
"""
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    pass

    # App
    APP_ENV: Literal["development", "staging", "production"] = "development"
    APP_SECRET_KEY: str = "change-me"
    LOG_LEVEL: str = "INFO"

    # API
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173"]

    # LLM
    LLM_PROVIDER: str = "ollama"           # ollama | openai | azure_openai
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_DEPLOYMENT: str = "gpt-4o"
    AZURE_OPENAI_API_VERSION: str = "2024-02-01"
    OPENAI_API_KEY: str = ""
    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"

    # LangGraph checkpointer
    LANGGRAPH_CHECKPOINTER: str = "memory"
    CHECKPOINT_DB_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/pmo_checkpoints"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./pmo_agent.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Vector store
    VECTOR_STORE: str = "chroma"
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001

    # Embedding
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_PROVIDER: str = "openai"

    # Auth
    AUTH_PROVIDER: str = "azure_ad"
    AZURE_AD_TENANT_ID: str = ""
    AZURE_AD_CLIENT_ID: str = ""
    AZURE_AD_CLIENT_SECRET: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings: Settings = get_settings()
