from Configuration import get_settings
from .FileStorage.StorageProviderFactory import get_storage_provider
from .Chunker.ChunkerFactory import get_chunker

class BaseController:
    def __init__(self):
        self.settings = get_settings()
        self.storage = get_storage_provider(self.settings)
        self.chunker = get_chunker()