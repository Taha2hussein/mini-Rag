import sys
from pathlib import Path


# =========================================
# Add src/ to Python import path
# =========================================

BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"

sys.path.insert(0, str(SRC_DIR))


from Embeddings import get_embedding_service
from VectorStore import (
    get_vector_point_builder,
    get_vector_store,
)
from Controllers.Chunker.ChunkerFactory import get_chunker


TEST_FILE = BASE_DIR / "test.txt"


def main() -> None:

    print("========================================")
    print("VECTOR POINT BUILDER TEST")
    print("========================================")

    # -----------------------------------------
    # 1. Read test file
    # -----------------------------------------

    text = TEST_FILE.read_text(
        encoding="utf-8"
    )

    print(f"File: {TEST_FILE}")
    print(f"Characters: {len(text)}")

    # -----------------------------------------
    # 2. Chunk text
    # -----------------------------------------

    chunker = get_chunker()

    chunks = chunker.chunk(
        text=text,
        metadata={
            "source": "test.txt",
            "session_id": "test-session-001",
            "document_id": "test-document-001",
            "user_id": 3,
        },
    )

    print(f"\nChunks: {len(chunks)}")

    # -----------------------------------------
    # 3. Generate embeddings
    # -----------------------------------------

    embedding_service = get_embedding_service()

    chunk_texts = [
        chunk.page_content
        for chunk in chunks
    ]

    print("\nGenerating BGE-M3 embeddings...")

    result = embedding_service.encode(
        chunk_texts
    )

    dense_vectors = result["dense_vecs"]
    sparse_vectors = result["lexical_weights"]

    print(
        f"Dense vectors: {len(dense_vectors)}"
    )

    print(
        f"Sparse vectors: {len(sparse_vectors)}"
    )

    # -----------------------------------------
    # 4. Build Qdrant points
    # -----------------------------------------

    point_builder = get_vector_point_builder()

    points = point_builder.build_points(
        chunks=chunks,
        dense_vectors=dense_vectors,
        sparse_vectors=sparse_vectors,
    )

    print(
        f"\nGenerated points: {len(points)}"
    )

    # -----------------------------------------
    # 5. Validate points
    # -----------------------------------------

    if len(points) != len(chunks):
        raise RuntimeError(
            "Points count does not match chunks count."
        )

    first_point = points[0]

    print("\nFirst point:")

    print(
        "ID:",
        first_point["id"],
    )

    print(
        "Dense dimensions:",
        len(first_point["dense"]),
    )

    print(
        "Sparse tokens:",
        len(first_point["sparse"]["indices"]),
    )

    print(
        "Payload:",
        first_point["payload"],
    )

    # -----------------------------------------
    # 6. Store in Qdrant
    # -----------------------------------------

    vector_store = get_vector_store()

    print("\nStoring points in Qdrant...")

    vector_store.upsert(points)

    print("Points stored successfully.")

    # -----------------------------------------
    # 7. Verify
    # -----------------------------------------

    stored_points = vector_store.client.retrieve(
        collection_name=vector_store.COLLECTION_NAME,
        ids=[
            point["id"]
            for point in points
        ],
        with_payload=True,
        with_vectors=False,
    )

    print(
        "\nRetrieved points:",
        len(stored_points),
    )

    if len(stored_points) != len(points):
        raise RuntimeError(
            "Stored points count does not match."
        )

    print("\n========================================")
    print("VECTOR POINT BUILDER TEST PASSED")
    print("========================================")


if __name__ == "__main__":
    main()