from abc import ABC, abstractmethod
from typing import List
from langchain_core.documents import Document


class ChunkerInterface(ABC):
    """
    Interface عام لأي طريقة تقسيم نص لأجزاء (chunks).
    """

    @abstractmethod
    def chunk(self, text: str, metadata: dict) -> List[Document]:
        """
        بتاخد النص الكامل + metadata (زي مصدر الملف)،
        وترجّع ليستة من Document objects، كل واحد فيه
        النص (page_content) والمصدر (metadata).
        """
        raise NotImplementedError