from typing import Any

from FlagEmbedding import FlagReranker
from huggingface_hub import snapshot_download

from .RerankerInterface import RerankerInterface


class BGE_M3_RerankerService(RerankerInterface):

    MODEL_NAME = "BAAI/bge-reranker-v2-m3"

    def __init__(self) -> None:

        model_path = snapshot_download(
            repo_id=self.MODEL_NAME,
            local_files_only=False,
        )

        self.model = FlagReranker(
            model_path,
            use_fp16=False,
        )

    def rerank(
        self,
        query: str,
        documents: list[str],
    ) -> list[dict[str, Any]]:

        if not query.strip():
            raise ValueError("query must not be empty.")

        if not documents:
            return []

        pairs = [
            [query, document]
            for document in documents
        ]

        scores = self.model.compute_score(
            pairs,
            normalize=True,
        )

        if isinstance(scores, float):
            scores = [scores]

        results = [
            {
                "index": index,
                "score": float(score),
                "text": documents[index],
            }
            for index, score in enumerate(scores)
        ]

        results.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return results