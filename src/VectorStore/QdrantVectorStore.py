from typing import Any

from qdrant_client import QdrantClient, models
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    SparseVector,
    SparseVectorParams,
    VectorParams,
)

from .VectorStoreInterface import VectorStoreInterface


class QdrantVectorStore(VectorStoreInterface):

    COLLECTION_NAME = "mini_rag_chunks"

    DENSE_VECTOR_NAME = "dense"
    SPARSE_VECTOR_NAME = "sparse"

    DENSE_VECTOR_SIZE = 1024

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
    ) -> None:

        self.client = QdrantClient(
            host=host,
            port=port,
        )

        self._ensure_collection()

    def _ensure_collection(self) -> None:

        collections = self.client.get_collections()

        collection_names = {
            collection.name
            for collection in collections.collections
        }

        if self.COLLECTION_NAME in collection_names:
            return

        self.client.create_collection(
            collection_name=self.COLLECTION_NAME,
            vectors_config={
                self.DENSE_VECTOR_NAME: VectorParams(
                    size=self.DENSE_VECTOR_SIZE,
                    distance=Distance.COSINE,
                ),
            },
            sparse_vectors_config={
                self.SPARSE_VECTOR_NAME: SparseVectorParams(),
            },
        )

    def upsert(
        self,
        points: list[dict[str, Any]],
    ) -> None:

        if not points:
            raise ValueError(
                "points must contain at least one point."
            )

        qdrant_points: list[PointStruct] = []

        for point in points:

            dense_vector = point["dense"]
            sparse_vector = point["sparse"]

            qdrant_points.append(
                PointStruct(
                    id=point["id"],
                    vector={
                        self.DENSE_VECTOR_NAME: dense_vector,
                        self.SPARSE_VECTOR_NAME: SparseVector(
                            indices=sparse_vector["indices"],
                            values=sparse_vector["values"],
                        ),
                    },
                    payload=point["payload"],
                )
            )

        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=qdrant_points,
            wait=True,
        )

    def search(
        self,
        query: dict[str, Any],
        user_id: int,
        limit: int = 5,
    ) -> list[Any]:

        if not query:
            raise ValueError(
                "query must not be empty."
            )

        if limit <= 0:
            raise ValueError(
                "limit must be greater than zero."
            )

        dense_vector = query["dense"]
        sparse_vector = query["sparse"]

        # --------------------------------------------------
        # Retrieval Scope
        #
        # Search is scoped by user_id ONLY.
        #
        # session_id is intentionally NOT used here.
        #
        # A user's documents can be retrieved regardless
        # of which session originally uploaded them.
        # --------------------------------------------------

        search_filter = Filter(
            must=[
                FieldCondition(
                    key="user_id",
                    match=MatchValue(
                        value=user_id,
                    ),
                ),
            ],
        )

        # --------------------------------------------------
        # Dense Retrieval
        # --------------------------------------------------

        dense_query = models.Prefetch(
            query=dense_vector,
            using=self.DENSE_VECTOR_NAME,
            filter=search_filter,
            limit=limit,
        )

        # --------------------------------------------------
        # Sparse Retrieval
        # --------------------------------------------------

        sparse_query = models.Prefetch(
            query=SparseVector(
                indices=sparse_vector["indices"],
                values=sparse_vector["values"],
            ),
            using=self.SPARSE_VECTOR_NAME,
            filter=search_filter,
            limit=limit,
        )

        # --------------------------------------------------
        # Hybrid Retrieval + RRF Fusion
        # --------------------------------------------------

        response = self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            prefetch=[
                dense_query,
                sparse_query,
            ],
            query=models.FusionQuery(
                fusion=models.Fusion.RRF,
            ),
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )

        return response.points