from abc import ABC, abstractmethod


class FileLoaderInterface(ABC):
    @abstractmethod
    def load(self, file_bytes: bytes) -> str:
        raise NotImplementedError