from .RerankerFactory import get_reranker_service
from .RerankingService import RerankingService


_reranking_service: RerankingService | None = None


def get_reranking_pipeline() -> RerankingService:

    global _reranking_service

    if _reranking_service is None:
        _reranking_service = RerankingService(
            reranker=get_reranker_service(),
        )

    return _reranking_service