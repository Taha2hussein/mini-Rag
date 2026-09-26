from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from Controllers.Sessions import (
    SessionController,
    get_session_controller,
)

from Database.database import get_db


router = APIRouter(
    prefix="/api/v1",
    tags=["Sessions"],
)


@router.post("/sessions")
async def create_session(
    db: Session = Depends(get_db),  # noqa: B008
    session_controller: SessionController = Depends(get_session_controller),  # noqa: B008
):
    return session_controller.create_session(db)