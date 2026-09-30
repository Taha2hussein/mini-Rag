from .ContextBuilderInterface import ContextBuilderInterface
from .RAGContextBuilder import RAGContextBuilder


_context_builder: ContextBuilderInterface | None = None


def get_context_builder() -> ContextBuilderInterface:
    global _context_builder

    if _context_builder is None:
        _context_builder = RAGContextBuilder()

    return _context_builder