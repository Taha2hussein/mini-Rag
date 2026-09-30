from abc import ABC, abstractmethod
from typing import Any


class EmbeddingInterface(ABC):

    @abstractmethod
    def encode(
        self,
        texts: list[str],
    ) -> dict[str, Any]:
        """
        Generate dense and sparse embeddings.

        Returns:
            {
                "dense_vecs": ...,
                "lexical_weights": ...
            }
        """
        raise NotImplementedError