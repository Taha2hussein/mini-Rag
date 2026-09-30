from .BGE_M3_RerankerService import BGE_M3_RerankerService
from .RerankerInterface import RerankerInterface


_reranker_service: RerankerInterface | None = None


def get_reranker_service() -> RerankerInterface:

    global _reranker_service

    if _reranker_service is None:
        _reranker_service = BGE_M3_RerankerService()

    return _reranker_service