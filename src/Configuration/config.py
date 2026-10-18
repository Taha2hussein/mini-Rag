
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    APP_NAME: str
    APP_VERSION: str

    # OpenAI
    OPENAI_API_KEY: str

    # File Upload
    FILE_ALLOWED_TYPES: list[str]
    FILE_ALLOWED_SIZE_MB: int

    # Storage
    STORAGE_PROVIDER: str = "s3"
    FILE_DIR: str = "assets/files"

    # S3-compatible storage (Filebase)
    AWS_BUCKET_NAME: str
    AWS_ACCESS_KEY: str
    AWS_SECRET_KEY: str
    AWS_REGION: str
    S3_ENDPOINT_URL: str

    # PostgreSQL
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # Authentication
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"

    # RAG Retrieval
    RAG_RETRIEVAL_LIMIT: int = 20
    RAG_CONTEXT_LIMIT: int = 5
    RERANKER_RELEVANCE_THRESHOLD: float = 0.5

    # Context Filtering
    CONTEXT_MIN_RERANKER_SCORE: float = 0.5
    CONTEXT_MAX_RESULTS: int = 5

    # Configuration file
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / ".env",
        extra="ignore",
        env_file_encoding="utf-8",
    )


def get_settings() -> Settings:
    return Settings()
