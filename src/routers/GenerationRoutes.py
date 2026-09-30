from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from Database import get_db
from Security.dependencies import get_current_user
from Generation import get_generation_service
from schema.GenerationSchema import (
    GenerationInput,
    GenerationResponse,
)


router = APIRouter(
    prefix="/generation",
    tags=["Generation"],
)


@router.post(
    "/generate",
    response_model=GenerationResponse,
)
async def generate(
    request: GenerationInput,
    user_id: int = Depends(get_current_user), # noqa: B008
    db: Session = Depends(get_db), # noqa: B008
):
    generation_service = get_generation_service(db)

    return await generation_service.generate(
        question=request.question,
        session_id=request.session_id,
        user_id=user_id,
    )