from .BaseController import BaseController
from .TextExtraction.FileLoaderFactory import get_file_loader

from Models import FileType

from Database.models import Session as SessionModel, Document

from starlette.concurrency import run_in_threadpool
from sqlalchemy.orm import Session


class DataController(BaseController):

    def __init__(self):
        super().__init__()

    async def read_root(self):
        return {
            "App Name": self.settings.APP_NAME,
            "App Version": self.settings.APP_VERSION,
        }

    async def validate_file(self, file):

        if file.content_type.split("/")[1] not in self.settings.FILE_ALLOWED_TYPES:
            return (
                False,
                f"{FileType.FILE_TYPE_NOT_ALLOWED.value}: "
                f"{self.settings.FILE_ALLOWED_TYPES}",
            )

        if file.size > self.settings.FILE_ALLOWED_SIZE_MB * 1024 * 1024:
            return (
                False,
                f"{FileType.FILE_SIZE_NOT_ALLOWED.value}. "
                f"Allowed size: {self.settings.FILE_ALLOWED_SIZE_MB} MB",
            )

        return True, FileType.FILE_UPLOADED_SUCCESSFULLY.value

    async def upload_file(
        self,
        session_id: str,
        file,
        db: Session,
    ):

        session = db.get(SessionModel, session_id)

        if session is None:
            return {
                "error": "Session not found."
            }

        is_valid, message = await self.validate_file(file)

        if not is_valid:
            return {
                "error": message
            }

        file_id = f"{session_id}/{file.filename}"

        await run_in_threadpool(
            self.storage.save_file,
            file,
            file_id,
        )

        document = Document(
            session_id=session_id,
            filename=file.filename,
            file_id=file_id,
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        return {
            "document_id": document.id,
            "session_id": document.session_id,
            "filename": document.filename,
            "status": "uploaded",
        }

    async def process_file(
        self,
        document_id: str,
        db: Session,
    ):

        # 1. Get document from PostgreSQL
        document = db.get(Document, document_id)

        if document is None:
            return {
                "error": "Document not found."
            }

        # 2. Get the real storage file_id
        file_id = document.file_id

        # 3. Get file from storage
        file_bytes = await run_in_threadpool(
            self.storage.get_file,
            file_id,
        )

        # 4. Get loader using the real filename
        loader = get_file_loader(document.filename)

        # 5. Extract text
        extracted_text = await run_in_threadpool(
            loader.load,
            file_bytes,
        )

        # 6. Split text into chunks
        chunks = await run_in_threadpool(
            self.chunker.chunk,
            extracted_text,
            {
                "source": file_id,
                "session_id": document.session_id,
                "document_id": document.id,
            },
        )

        # 7. Return processing result
        return {
            "document_id": document.id,
            "filename": document.filename,
            "chunks_count": len(chunks),
            "first_chunk_preview": (
                chunks[0].page_content[:200]
                if chunks
                else None
            ),
            "first_chunk_metadata": (
                chunks[0].metadata
                if chunks
                else None
            ),
        }


def get_data_controller() -> DataController:
    return DataController()