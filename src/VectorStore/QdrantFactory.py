from .QdrantVectorStore import QdrantVectorStore
from .VectorStoreInterface import VectorStoreInterface


_vector_store: VectorStoreInterface | None = None


def get_vector_store() -> VectorStoreInterface:

    global _vector_store

    if _vector_store is None:
        _vector_store = QdrantVectorStore()

    return _vector_store