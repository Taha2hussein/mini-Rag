from typing import Any

from FlagEmbedding import BGEM3FlagModel
from huggingface_hub import snapshot_download

from .EmbeddingInterface import EmbeddingInterface


class BGE_M3_EmbeddingService(EmbeddingInterface):

    MODEL_NAME = "BAAI/bge-m3"

    def __init__(self) -> None:

        print("========================================")
        print("Initializing BGE-M3 Embedding Service")
        print("========================================")

        # Resolve the already downloaded model
        # from the local Hugging Face cache.
        model_path = snapshot_download(
            repo_id=self.MODEL_NAME,
            local_files_only=True,
        )

        print(f"Using local model: {model_path}")

        # Load the model ONCE.
        #
        # The same instance will be reused for
        # all embedding requests handled by this service.
        self.model = BGEM3FlagModel(
            model_path,
            use_fp16=False,
        )

        print("BGE-M3 loaded successfully.")

    def encode(
        self,
        texts: list[str],
    ) -> dict[str, Any]:

        if not texts:
            raise ValueError(
                "texts must contain at least one text."
            )

        return self.model.encode(
            texts,
            return_dense=True,
            return_sparse=True,
            return_colbert_vecs=False,
        )