from abc import ABC, abstractmethod
from typing import Any


class RerankerInterface(ABC):

    @abstractmethod
    def rerank(
        self,
        query: str,
        documents: list[str],
    ) -> list[dict[str, Any]]:
        """
        Re-rank retrieved documents according to their
        relevance to the query.
        """
        raise NotImplementedError