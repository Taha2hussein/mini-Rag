from fastapi import APIRouter, Depends, Form, UploadFile
from Controllers import DataController, get_data_controller
from Database.database import get_db
from pydantic import BaseModel
from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/api/v1",
    tags=["API_v1"],
)


class ProcessFileRequest(BaseModel):
    document_id: str


@router.get("/")
async def read_root(
    data_controller: DataController = Depends(get_data_controller),  # noqa: B008
):
    return await data_controller.read_root()


@router.post("/upload")
async def upload_file(
    session_id: str = Form(...),
    file: UploadFile = None,
    db: Session = Depends(get_db), # noqa: B008
    data_controller: DataController = Depends(get_data_controller),  # noqa: B008
):
    return await data_controller.upload_file(
        session_id,
        file,
        db,
    )


@router.post("/process")
async def process_file(
    request: ProcessFileRequest,
    db: Session = Depends(get_db),  # noqa: B008
    data_controller: DataController = Depends(get_data_controller),  # noqa: B008
):
    return await data_controller.process_file(
        request.document_id,
        db,
    )