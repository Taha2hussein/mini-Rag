import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.Embeddings import get_embedding_service


BASE_DIR = Path(__file__).resolve().parent.parent
TEST_FILE = BASE_DIR / "test.txt"


def main() -> None:

    text = TEST_FILE.read_text(
        encoding="utf-8"
    )

    embedding_service = get_embedding_service()

    result = embedding_service.encode(
        [text]
    )

    dense = result["dense_vecs"]
    sparse = result["lexical_weights"]

    print("\n========================================")
    print("EMBEDDING TEST")
    print("========================================")

    print("Dense dimensions:", dense.shape[1])
    print("Sparse tokens:", len(sparse[0]))

    print("\nDense first 10 values:")

    for value in dense[0][:10]:
        print(f"{value:.8f}")

    print("\nFirst 10 sparse values:")

    for token_id, weight in list(
        sparse[0].items()
    )[:10]:

        print(
            f"token_id={token_id}, "
            f"weight={weight:.6f}"
        )


if __name__ == "__main__":
    main()