from Configuration import get_settings
from .StorageProviderFactory import get_storage_provider


class BaseController:
    def __init__(self):
        self.settings = get_settings()
        self.storage = get_storage_provider(self.settings)
        