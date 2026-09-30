import sys
from pathlib import Path


# =========================================
# Add src/ to Python import path
# =========================================

BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"

sys.path.insert(0, str(SRC_DIR))


from Embeddings import get_embedding_service
from VectorStore import get_vector_store


# =========================================
# Test configuration
# =========================================

USER_ID = 2
QUERY_TEXT = "How do I create a new Git branch?"
LIMIT = 5


def main() -> None:

    print("========================================")
    print("HYBRID SEARCH TEST")
    print("========================================")

    print(f"User ID: {USER_ID}")
    print(f"Query: {QUERY_TEXT}")
    print(f"Limit: {LIMIT}")

    # -----------------------------------------
    # 1. Generate query embeddings
    # -----------------------------------------

    print("\nGenerating query embeddings...")

    embedding_service = get_embedding_service()

    result = embedding_service.encode(
        [QUERY_TEXT]
    )

    dense_vector = result["dense_vecs"][0]
    sparse_weights = result["lexical_weights"][0]

    print(
        "Dense dimensions:",
        len(dense_vector),
    )

    print(
        "Sparse tokens:",
        len(sparse_weights),
    )

    # -----------------------------------------
    # 2. Convert sparse representation
    # -----------------------------------------

    sparse_vector = {
        "indices": list(
            sparse_weights.keys()
        ),
        "values": list(
            sparse_weights.values()
        ),
    }

    # -----------------------------------------
    # 3. Build query
    # -----------------------------------------

    query = {
        "dense": dense_vector.tolist(),

        "sparse": sparse_vector,
    }

    # -----------------------------------------
    # 4. Search Qdrant
    # -----------------------------------------

    vector_store = get_vector_store()

    print("\nSearching Qdrant...")

    results = vector_store.search(
        query=query,
        user_id=USER_ID,
        limit=LIMIT,
    )

    # -----------------------------------------
    # 5. Print results
    # -----------------------------------------

    print(
        f"\nResults returned: {len(results)}"
    )

    for index, result in enumerate(
        results,
        start=1,
    ):

        print("\n----------------------------------------")
        print(f"RESULT #{index}")
        print("----------------------------------------")

        print("Point ID:")
        print(result.id)

        print("\nScore:")
        print(result.score)

        payload = result.payload or {}

        print("\nUser ID:")
        print(payload.get("user_id"))

        print("\nSession ID:")
        print(payload.get("session_id"))

        print("\nDocument ID:")
        print(payload.get("document_id"))

        print("\nSource:")
        print(payload.get("source"))

        print("\nChunk Index:")
        print(payload.get("chunk_index"))

        text = payload.get("text", "")

        print("\nText:")
        print(text[:500])

    # -----------------------------------------
    # 6. Validate results
    # -----------------------------------------

    if not results:
        raise RuntimeError(
            "Hybrid search returned no results."
        )

    for result in results:

        payload = result.payload or {}

        if payload.get("user_id") != USER_ID:
            raise RuntimeError(
                "USER ISOLATION FAILED: "
                "result belongs to another user."
            )

    print("\n========================================")
    print("HYBRID SEARCH TEST PASSED")
    print("========================================")


if __name__ == "__main__":
    main()