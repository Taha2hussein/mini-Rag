# routers/router.py
from fastapi import APIRouter, UploadFile, Depends
from Controllers import DataController, get_data_controller
from pydantic import BaseModel
router = APIRouter(
    prefix="/api/v1",
    tags=["API_v1"],
)

class ProcessFileRequest(BaseModel):
    file_id: str


@router.get("/")
async def read_root(
    data_controller: DataController = Depends(get_data_controller),  # noqa: B008
):
    return await data_controller.read_root()

@router.post("/upload/{project_id}")
async def upload_file(project_id: str, file: UploadFile, data_controller: DataController = Depends(get_data_controller),  # noqa: B008
):
    return await data_controller.upload_file(project_id, file)

@router.post("/process")
async def process_file(
    request: ProcessFileRequest,
    data_controller: DataController = Depends(get_data_controller),   # noqa: B008
):
    return await data_controller.process_file(request.file_id)
