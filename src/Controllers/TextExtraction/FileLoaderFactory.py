import os

from .FileLoaderInterface import FileLoaderInterface
from .TextLoader import TextLoader
from .PDFLoader import PDFLoader


def get_file_loader(filename: str) -> FileLoaderInterface:
    extension = os.path.splitext(filename)[1].lower()

    if extension == ".txt":
        return TextLoader()

    if extension == ".pdf":
        return PDFLoader()

    raise ValueError(f"Unsupported file type: {extension}")