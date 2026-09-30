from abc import ABC, abstractmethod


class GenerationInterface(ABC):

    @abstractmethod
    async def generate(
        self,
        question: str,
        session_id: str,
        user_id: int,
    ) -> dict:
        """
        Generate a RAG-based answer for a user's question.
        """
        raise NotImplementedError