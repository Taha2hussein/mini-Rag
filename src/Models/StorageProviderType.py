from enum import Enum


class StorageProviderType(str, Enum):
    LOCAL = "local"
    S3 = "s3"