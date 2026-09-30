import uuid
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.Embeddings import get_embedding_service
from src.VectorStore import get_vector_store
TEST_FILE = BASE_DIR / "test.txt"


def main() -> None:

    print("========================================")
    print("QDRANT VECTOR STORE TEST")
    print("========================================")

    # --------------------------------------------------
    # 1. Read test document
    # --------------------------------------------------

    text = TEST_FILE.read_text(
        encoding="utf-8"
    )

    print(f"Test file: {TEST_FILE}")
    print(f"Characters: {len(text)}")

    # --------------------------------------------------
    # 2. Generate embeddings
    # --------------------------------------------------

    print("\nGenerating BGE-M3 embeddings...")

    embedding_service = get_embedding_service()

    result = embedding_service.encode(
        [text]
    )

    dense = result["dense_vecs"][0]
    sparse_weights = result["lexical_weights"][0]

    print(
        f"Dense dimensions: {len(dense)}"
    )

    print(
        f"Sparse tokens: {len(sparse_weights)}"
    )

    # --------------------------------------------------
    # 3. Convert sparse dictionary
    #    into Qdrant SparseVector format
    # --------------------------------------------------

    sparse_indices = list(
        sparse_weights.keys()
    )

    sparse_values = list(
        sparse_weights.values()
    )

    # --------------------------------------------------
    # 4. Build Qdrant point
    # --------------------------------------------------

    point_id = str(uuid.uuid4())

    payload = {
        "user_id": 3,
        "session_id": "test-session-001",
        "document_id": "test-document-001",
        "text": text,
        "source": "test.txt",
    }

    point = {
        "id": point_id,

        "dense": dense.tolist(),

        "sparse": {
            "indices": sparse_indices,
            "values": sparse_values,
        },

        "payload": payload,
    }

    # --------------------------------------------------
    # 5. Get Vector Store
    # --------------------------------------------------

    vector_store = get_vector_store()

    # --------------------------------------------------
    # 6. Store point
    # --------------------------------------------------

    print("\nStoring vector in Qdrant...")

    vector_store.upsert(
        [point]
    )

    print("Vector stored successfully.")

    # --------------------------------------------------
    # 7. Verify point exists
    # --------------------------------------------------

    print("\nVerifying stored point...")

    stored_points = vector_store.client.retrieve(
        collection_name=vector_store.COLLECTION_NAME,
        ids=[point_id],
        with_payload=True,
        with_vectors=False,
    )

    if not stored_points:
        raise RuntimeError(
            "Point was not found in Qdrant."
        )

    stored_point = stored_points[0]

    print(
        f"Point ID: {stored_point.id}"
    )

    print(
        f"Payload user_id: "
        f"{stored_point.payload['user_id']}"
    )

    print(
        f"Payload session_id: "
        f"{stored_point.payload['session_id']}"
    )

    print(
        f"Payload document_id: "
        f"{stored_point.payload['document_id']}"
    )

    print(
        f"Payload source: "
        f"{stored_point.payload['source']}"
    )

    print("\n========================================")
    print("QDRANT INTEGRATION TEST PASSED")
    print("========================================")


if __name__ == "__main__":
    main()