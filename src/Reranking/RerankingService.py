from typing import Any

from .RerankerInterface import RerankerInterface


class RerankingService:

    def __init__(self, reranker: RerankerInterface):
        self.reranker = reranker

    def rerank_results(
        self,
        query: str,
        results: list[Any],
        top_k: int = 5,
    ) -> list[Any]:

        if not query.strip():
            raise ValueError("query must not be empty.")

        if not results:
            return []

        documents = []

        for result in results:
            payload = getattr(result, "payload", None) or {}
            text = payload.get("text", "").strip()

            documents.append(text)

        reranked = self.reranker.rerank(
            query=query,
            documents=documents,
        )

        reranked = reranked[:top_k]

        final_results = []

        for item in reranked:
            original_index = item["index"]

            result = results[original_index]

            final_results.append(
                {
                    "result": result,
                    "reranker_score": item["score"],
                }
            )

        return final_results