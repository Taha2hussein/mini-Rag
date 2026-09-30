from .EmbeddingInterface import EmbeddingInterface
from .BGE_M3_EmbeddingService import BGE_M3_EmbeddingService


_embedding_service: EmbeddingInterface | None = None


def get_embedding_service() -> EmbeddingInterface:

    global _embedding_service

    if _embedding_service is None:
        _embedding_service = BGE_M3_EmbeddingService()

    return _embedding_service