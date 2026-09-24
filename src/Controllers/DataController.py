from .BaseController import BaseController
from .TextExtraction.FileLoaderFactory import get_file_loader
from Models import FileType
from starlette.concurrency import run_in_threadpool


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
            return False, f"{FileType.FILE_TYPE_NOT_ALLOWED.value}: {self.settings.FILE_ALLOWED_TYPES}"

        if file.size > self.settings.FILE_ALLOWED_SIZE_MB * 1024 * 1024:
            return False, f"{FileType.FILE_SIZE_NOT_ALLOWED.value}. Allowed size: {self.settings.FILE_ALLOWED_SIZE_MB} MB"

        return True, f"{FileType.FILE_UPLOADED_SUCCESSFULLY.value}"

    async def upload_file(self, project_id: str, file):
        is_valid, message = await self.validate_file(file)
        if not is_valid:
            return {"error": message}

        file_id = f"{project_id}/{file.filename}"
        await run_in_threadpool(self.storage.save_file, file, file_id)
        return {
                 "message": f"{message} for project '{project_id}'.",
                 "file_id": file_id
        }


    async def process_file(self, file_id: str):
         file_bytes = await run_in_threadpool(self.storage.get_file, file_id)
         filename = file_id.split("/")[-1]
         project_id = file_id.split("/")[0]
         loader = get_file_loader(filename)
         extracted_text = await run_in_threadpool(loader.load, file_bytes)
         chunks = await run_in_threadpool(
               self.chunker.chunk,
               extracted_text,
               {"source": file_id, "project_id": project_id},
           )
         return {
               "chunks_count": len(chunks),
               "first_chunk_preview": chunks[0].page_content[:200] if chunks else None,
               "first_chunk_metadata": chunks[0].metadata if chunks else None,
           }

def get_data_controller() -> DataController:
    return DataController()