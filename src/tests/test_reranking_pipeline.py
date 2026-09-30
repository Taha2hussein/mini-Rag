import asyncio

from starlette.concurrency import run_in_threadpool

from Embeddings import get_embedding_service
from VectorStore import get_vector_store
from Reranking import get_reranking_pipeline


USER_ID = 2

QUERIES = [
    # 1. Directly available in the documents
    "How do I create a new Git branch?",

    # 2. Same concept, different wording
    "How can I make a new branch in Git?",

    # 3. Related concept but answer should be in the documents
    "How do I switch to another Git branch?",

    # 4. Completely unrelated to the documents
    "What is the capital of Japan?",

    # 5. Another unrelated question
    "How do I cook pasta?",
]


async def test_query(
    query: str,
    embedding_service,
    vector_store,
    reranking_pipeline,
):

    print("\n")
    print("=" * 70)
    print(f"QUERY: {query}")
    print("=" * 70)

    # ----------------------------------------
    # 1. Generate query embedding
    # ----------------------------------------

    embedding_result = await run_in_threadpool(
        embedding_service.encode,
        [query],
    )

    dense_vector = embedding_result["dense_vecs"][0]
    sparse_weights = embedding_result["lexical_weights"][0]

    query_vector = {
        "dense": dense_vector.tolist(),
        "sparse": {
            "indices": list(sparse_weights.keys()),
            "values": list(sparse_weights.values()),
        },
    }

    # ----------------------------------------
    # 2. Retrieve candidates from Qdrant
    # ----------------------------------------

    results = await run_in_threadpool(
        vector_store.search,
        query_vector,
        USER_ID,
        20,
    )

    print(f"\nQdrant candidates: {len(results)}")

    # ----------------------------------------
    # 3. Rerank candidates
    # ----------------------------------------

    reranked_results = await run_in_threadpool(
        reranking_pipeline.rerank_results,
        query,
        results,
        5,
    )

    # ----------------------------------------
    # 4. Print results
    # ----------------------------------------

    if not reranked_results:
        print("No reranked results.")
        return

    for rank, item in enumerate(reranked_results, start=1):

        result = item["result"]
        reranker_score = item["reranker_score"]

        payload = result.payload or {}

        print(f"\nRank: {rank}")
        print(f"Reranker score: {reranker_score:.6f}")
        print(f"Qdrant score: {result.score:.6f}")
        print(f"Source: {payload.get('source', '')}")
        print(f"Chunk: {payload.get('chunk_index', 0)}")

        text = payload.get("text", "").strip()

        print(f"Text: {text[:400]}")


async def main():

    print("\n")
    print("=" * 70)
    print("RERANKER EVALUATION TEST")
    print("=" * 70)

    embedding_service = get_embedding_service()
    vector_store = get_vector_store()
    reranking_pipeline = get_reranking_pipeline()

    for query in QUERIES:

        await test_query(
            query=query,
            embedding_service=embedding_service,
            vector_store=vector_store,
            reranking_pipeline=reranking_pipeline,
        )

    print("\n")
    print("=" * 70)
    print("TEST COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())