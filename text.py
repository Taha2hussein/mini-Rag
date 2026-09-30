
from pathlib import Path

from huggingface_hub import snapshot_download
from FlagEmbedding import BGEM3FlagModel


# ============================================================
# Configuration
# ============================================================

MODEL_NAME = "BAAI/bge-m3"

BASE_DIR = Path(__file__).resolve().parent
TEST_FILE = BASE_DIR / "test.txt"


# ============================================================
# Find BGE-M3 in Hugging Face Cache
# ============================================================

print("========================================")
print("BGE-M3")
print("========================================")

print("Checking local Hugging Face cache...")


try:
    model_path = snapshot_download(
        repo_id=MODEL_NAME,
        local_files_only=True,
    )

except Exception as exc:
    raise RuntimeError(
        "\nBGE-M3 was not found completely in the local "
        "Hugging Face cache.\n\n"
        "Run the model once with internet access to download "
        "the missing files, then run this test again.\n\n"
        f"Original error: {exc}"
    ) from exc


print("Using local model:")
print(model_path)


# ============================================================
# Load BGE-M3
# ============================================================

print("\n========================================")
print("Loading BGE-M3")
print("========================================")

model = BGEM3FlagModel(
    model_path,
    use_fp16=False,
)

print("Model loaded successfully.")


# ============================================================
# Read test.txt
# ============================================================

if not TEST_FILE.exists():
    raise FileNotFoundError(
        f"Test file not found: {TEST_FILE}"
    )


text = TEST_FILE.read_text(
    encoding="utf-8"
)


print("\n========================================")
print("TEST FILE")
print("========================================")

print("File:", TEST_FILE)
print("Characters:", len(text))


# ============================================================
# Generate Dense + Sparse Embeddings
# ============================================================

print("\n========================================")
print("ENCODING")
print("========================================")

embeddings = model.encode(
    [text],
    return_dense=True,
    return_sparse=True,
    return_colbert_vecs=False,
)


# ============================================================
# Dense Embedding
# ============================================================

dense_embeddings = embeddings["dense_vecs"]


print("\n========================================")
print("DENSE")
print("========================================")

print("Type:", type(dense_embeddings))
print("Number of embeddings:", len(dense_embeddings))
print("Dimensions:", dense_embeddings.shape[1])

print("\nFirst 10 values:")

for value in dense_embeddings[0][:10]:
    print(f"{value:.8f}")


# ============================================================
# Sparse Embedding
# ============================================================

sparse_embeddings = embeddings["lexical_weights"]


print("\n========================================")
print("SPARSE")
print("========================================")

print("Type:", type(sparse_embeddings))
print("Number of sparse embeddings:", len(sparse_embeddings))

print("\nNumber of non-zero sparse tokens:")
print(len(sparse_embeddings[0]))


print("\nFirst 20 sparse values:")

for token_id, weight in list(
    sparse_embeddings[0].items()
)[:20]:

    print(
        f"token_id={token_id}, "
        f"weight={weight:.6f}"
    )


# ============================================================
# Summary
# ============================================================

print("\n========================================")
print("SUMMARY")
print("========================================")

print("Model:", MODEL_NAME)
print("Model source: LOCAL CACHE")
print("Dense dimensions:", dense_embeddings.shape[1])
print("Sparse tokens:", len(sparse_embeddings[0]))
print("Status: SUCCESS")
