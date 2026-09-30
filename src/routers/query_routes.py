from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from Controllers.QueryController import (
    QueryController,
    get_query_controller,
)
from Database.database import get_db
from Security.dependencies import get_current_user
from schema.QuerySchema import (
    QueryInput,
    QueryResponse,
)


router = APIRouter(
    prefix="/api/v1",
    tags=["Query"],
)


@router.post(
    "/query",
    response_model=QueryResponse,
)
async def query(
    request: QueryInput,
    user_id: int = Depends(get_current_user), 
    db: Session = Depends(get_db),  # noqa: B008
    query_controller: QueryController = Depends(get_query_controller), # noqa: B008
):
    return await query_controller.query(
        query_text=request.query,
        session_id=request.session_id,
        user_id=user_id,
        db=db,
    )