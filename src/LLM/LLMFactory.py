from .DeepSeekLLMService import DeepSeekLLMService
from .LLMInterface import LLMInterface


_llm_service: LLMInterface | None = None


def get_llm_service() -> LLMInterface:
    global _llm_service

    if _llm_service is None:
        _llm_service = DeepSeekLLMService()

    return _llm_service