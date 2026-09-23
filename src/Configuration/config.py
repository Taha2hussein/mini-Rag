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

    AWS_BUCKET_NAME: str = ""
    AWS_ACCESS_KEY: str = ""
    AWS_SECRET_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_ENDPOINT_URL: str = "https://s3.filebase.io"
    
    class Config:
        env_file = Path(__file__).parent / ".env"


def get_settings():
    return Settings()