from abc import ABC, abstractmethod
from typing import Any


class VectorStoreInterface(ABC):

    @abstractmethod
    def upsert(self, points: list[dict[str, Any]]) -> None:
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        query: dict[str, Any],
        user_id: int,
        limit: int = 5,
    ) -> list[Any]:
        raise NotImplementedError