from .FileLoaderInterface import FileLoaderInterface


class TextLoader(FileLoaderInterface):
    def load(self, file_bytes: bytes) -> str:
        return file_bytes.decode("utf-8")