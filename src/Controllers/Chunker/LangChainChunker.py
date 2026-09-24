from typing import List

import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from .ChunkerInterface import ChunkerInterface


class LangChainChunker(ChunkerInterface):
    """
    تقسيم النص باستخدام RecursiveCharacterTextSplitter من LangChain،
    مع عدّ الـ tokens بدقة عن طريق tiktoken، وربط كل chunk بمصدره.
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 80,
                 encoding_name: str = "cl100k_base"):
        self.encoding = tiktoken.get_encoding(encoding_name)

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=self._token_length,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def _token_length(self, text: str) -> int:
        return len(self.encoding.encode(text))

    def chunk(self, text: str, metadata: dict) -> List[Document]:
        return self.splitter.create_documents(
            texts=[text],
            metadatas=[metadata],
        )