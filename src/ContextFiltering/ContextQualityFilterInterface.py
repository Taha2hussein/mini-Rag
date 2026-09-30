from abc import ABC, abstractmethod
from typing import Any


class ContextQualityFilterInterface(ABC):

    @abstractmethod
    def filter(
        self,
        results: list[Any],
        min_score: float,
        max_results: int,
    ) -> list[Any]:
        raise NotImplementedError