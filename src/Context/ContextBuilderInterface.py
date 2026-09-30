from abc import ABC, abstractmethod
from typing import Any


class ContextBuilderInterface(ABC):

    @abstractmethod
    def build(
        self,
        results: list[Any],
    ) -> str:
        """
        Convert retrieved vector-store results into
        structured context for the LLM.
        """
        raise NotImplementedError