# Controllers/StorageProviderFactory.py

from .StorageProviderInterface import StorageProviderInterface
from .LocalStorageProvider import LocalStorageProvider
from .S3StorageProvider import S3StorageProvider


def get_storage_provider(settings) -> StorageProviderInterface:
    """
    بترجّع نسخة من الـ storage provider المناسب بناءً على STORAGE_PROVIDER
    في الإعدادات. أي كود بينادي الـ function دي مش محتاج يعرف
    هل الملفات هتتخزن محليًا ولا على S3/Filebase.
    """
    provider = settings.STORAGE_PROVIDER.lower()

    if provider == "local":
        return LocalStorageProvider(base_dir=settings.FILE_DIR)

    if provider == "s3":
        return S3StorageProvider(
            bucket_name=settings.AWS_BUCKET_NAME,
            access_key=settings.AWS_ACCESS_KEY,
            secret_key=settings.AWS_SECRET_KEY,
            region=settings.AWS_REGION,
            endpoint_url=settings.S3_ENDPOINT_URL or None,
        )

    raise ValueError(f"Unknown storage provider: {settings.STORAGE_PROVIDER}")