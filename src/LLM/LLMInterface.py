from abc import ABC, abstractmethod


class LLMInterface(ABC):

    @abstractmethod
    async def generate(
        self,
        question: str,
        context: str,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        """
        Generate an answer using:

        - Current user question
        - Retrieved RAG context
        - Conversation history
        """
        raise NotImplementedError