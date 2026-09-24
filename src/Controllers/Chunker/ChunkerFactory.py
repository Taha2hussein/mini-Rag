from .ChunkerInterface import ChunkerInterface
from .LangChainChunker import LangChainChunker


def get_chunker(chunk_size: int = 500, chunk_overlap: int = 80) -> ChunkerInterface:
    return LangChainChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)