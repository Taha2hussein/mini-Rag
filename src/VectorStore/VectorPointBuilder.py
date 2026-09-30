import uuid
from typing import Any

from langchain_core.documents import Document


class VectorPointBuilder:

    @staticmethod
    def build_points(
        chunks: list[Document],
        dense_vectors: Any,
        sparse_vectors: list[dict[int, float]],
    ) -> list[dict[str, Any]]:

        if len(chunks) != len(dense_vectors):
            raise ValueError(
                "Chunks count must match dense vectors count."
            )

        if len(chunks) != len(sparse_vectors):
            raise ValueError(
                "Chunks count must match sparse vectors count."
            )

        points: list[dict[str, Any]] = []

        for index, chunk in enumerate(chunks):

            sparse_weights = sparse_vectors[index]

            point = {
                "id": str(uuid.uuid4()),

                "dense": dense_vectors[index].tolist(),

                "sparse": {
                    "indices": list(
                        sparse_weights.keys()
                    ),
                    "values": list(
                        sparse_weights.values()
                    ),
                },

                "payload": {
                    "user_id": chunk.metadata["user_id"],
                    "session_id": chunk.metadata["session_id"],
                    "document_id": chunk.metadata["document_id"],
                    "text": chunk.page_content,
                    "source": chunk.metadata["source"],
                    "chunk_index": index,
                },
            }

            points.append(point)

        return points


def get_vector_point_builder() -> VectorPointBuilder:
    return VectorPointBuilder()