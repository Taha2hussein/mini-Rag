import io
from pypdf import PdfReader

from .FileLoaderInterface import FileLoaderInterface


class PDFLoader(FileLoaderInterface):
    def load(self, file_bytes: bytes) -> str:
        reader = PdfReader(io.BytesIO(file_bytes))
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        return "\n".join(text_parts)