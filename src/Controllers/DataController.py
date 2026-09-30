from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from .BaseController import BaseController
from .TextExtraction.FileLoaderFactory import get_file_loader

from Models import FileType

from Database.models import (
    Session as SessionModel,
    Document,
)

from Embeddings import get_embedding_service

from VectorStore import (
    get_vector_store,
    get_vector_point_builder,
)


class DataController(BaseController):

    def __init__(self):
        super().__init__()

    async def read_root(self):
        return {
            "App Name": self.settings.APP_NAME,
            "App Version": self.settings.APP_VERSION,
        }

    async def validate_file(self, file):

        if file.content_type.split("/")[1] not in (
            self.settings.FILE_ALLOWED_TYPES
        ):
            return (
                False,
                f"{FileType.FILE_TYPE_NOT_ALLOWED.value}: "
                f"{self.settings.FILE_ALLOWED_TYPES}",
            )

        if file.size > self.settings.FILE_ALLOWED_SIZE_MB * 1024 * 1024:
            return (
                False,
                f"{FileType.FILE_SIZE_NOT_ALLOWED.value}. "
                f"Allowed size: "
                f"{self.settings.FILE_ALLOWED_SIZE_MB} MB",
            )

        return (
            True,
            FileType.FILE_UPLOADED_SUCCESSFULLY.value,
        )

    async def upload_file(
        self,
        session_id: str,
        file,
        db: Session,
        user_id: int,
    ):

        # ---------------------------------------------
        # 1. Validate session ownership
        # ---------------------------------------------

        session = (
            db.query(SessionModel)
            .filter(
                SessionModel.id == session_id,
                SessionModel.user_id == user_id,
            )
            .first()
        )

        if session is None:
            raise HTTPException(
                status_code=404,
                detail="Session not found.",
            )

        # ---------------------------------------------
        # 2. Validate file
        # ---------------------------------------------

        is_valid, message = await self.validate_file(file)

        if not is_valid:
            return {
                "error": message,
            }

        # ---------------------------------------------
        # 3. Save file
        # ---------------------------------------------

        file_id = f"{session_id}/{file.filename}"

        await run_in_threadpool(
            self.storage.save_file,
            file,
            file_id,
        )

        # ---------------------------------------------
        # 4. Save document metadata
        # ---------------------------------------------

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
        user_id: int,
    ):

        # ---------------------------------------------
        # 1. Get document with user isolation
        # ---------------------------------------------

        document = (
            db.query(Document)
            .join(SessionModel)
            .filter(
                Document.id == document_id,
                SessionModel.user_id == user_id,
            )
            .first()
        )

        if document is None:
            raise HTTPException(
                status_code=404,
                detail="Document not found.",
            )

        # ---------------------------------------------
        # 2. Get file from storage
        # ---------------------------------------------

        file_id = document.file_id

        file_bytes = await run_in_threadpool(
            self.storage.get_file,
            file_id,
        )

        # ---------------------------------------------
        # 3. Extract text
        # ---------------------------------------------

        loader = get_file_loader(
            document.filename
        )

        extracted_text = await run_in_threadpool(
            loader.load,
            file_bytes,
        )

        # ---------------------------------------------
        # 4. Chunk document
        # ---------------------------------------------

        chunks = await run_in_threadpool(
            self.chunker.chunk,
            extracted_text,
            {
                "source": file_id,
                "session_id": document.session_id,
                "document_id": document.id,
                "user_id": user_id,
            },
        )

        if not chunks:
            return {
                "document_id": document.id,
                "filename": document.filename,
                "chunks_count": 0,
                "vectors_stored": 0,
                "status": "processed",
            }

        # ---------------------------------------------
        # 5. Generate Dense + Sparse embeddings
        # ---------------------------------------------

        embedding_service = get_embedding_service()

        chunk_texts = [
            chunk.page_content
            for chunk in chunks
        ]

        embedding_result = await run_in_threadpool(
            embedding_service.encode,
            chunk_texts,
        )

        dense_vectors = embedding_result["dense_vecs"]
        sparse_vectors = embedding_result["lexical_weights"]

        # ---------------------------------------------
        # 6. Build Qdrant points
        # ---------------------------------------------

        point_builder = get_vector_point_builder()

        points = point_builder.build_points(
            chunks=chunks,
            dense_vectors=dense_vectors,
            sparse_vectors=sparse_vectors,
        )

        # ---------------------------------------------
        # 7. Store points in Qdrant
        # ---------------------------------------------

        vector_store = get_vector_store()

        await run_in_threadpool(
            vector_store.upsert,
            points,
        )

        # ---------------------------------------------
        # 8. Return processing result
        # ---------------------------------------------

        return {
            "document_id": document.id,
            "filename": document.filename,
            "chunks_count": len(chunks),
            "vectors_stored": len(points),
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
            "status": "processed",
        }


def get_data_controller() -> DataController:
    return DataController()