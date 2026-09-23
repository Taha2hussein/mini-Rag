from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    OPENAI_API_KEY: str
    APP_NAME: str
    APP_VERSION: str
    FILE_ALLOWED_TYPES: list[str]
    FILE_ALLOWED_SIZE_MB: int
    
    STORAGE_PROVIDER: str = "s3"   # "local" أو "s3"
    FILE_DIR: str = "assets/files"

    AWS_BUCKET_NAME: str = "rag-taha-files-taha"
    AWS_ACCESS_KEY: str = "1B45420CF65D6E723EDC"
    AWS_SECRET_KEY: str = "noFcvVfipxR0PksJzzWd2XKkM7hXyPvuS1rSiwXM"
    AWS_REGION: str = "us-east-1"
    S3_ENDPOINT_URL: str = "https://s3.filebase.io"

    
    class Config:
        env_file = Path(__file__).parent / ".env"


def get_settings():
    return Settings()