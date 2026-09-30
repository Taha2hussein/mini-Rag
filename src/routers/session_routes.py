from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from Controllers.Sessions import (
    SessionController,
    get_session_controller,
)
from Database.database import get_db
from Security.dependencies import get_current_user
from schema import (
    MessageInput,
    MessageListResponse,
    MessageOutput,
    SessionListResponse,
    SessionOutput,
)


router = APIRouter(
    prefix="/api/v1",
    tags=["Sessions"],
)


# =========================================================
# Create a new chat session
# =========================================================

@router.post(
    "/sessions",
    response_model=SessionOutput,
    status_code=status.HTTP_201_CREATED,
)
async def create_session(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),   # noqa: B008
    session_controller: SessionController = Depends(get_session_controller,) ,  # noqa: B008
):
    session = session_controller.create_session(
        db=db,
        user_id=user_id,
    )

    return {
        "session_id": session.id,
        "user_id": session.user_id,
        "created_at": session.created_at,
    }


# =========================================================
# Get all sessions for authenticated user
# =========================================================

@router.get(
    "/sessions",
    response_model=SessionListResponse,
)
async def get_sessions(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),   # noqa: B008
    session_controller: SessionController = Depends(get_session_controller,),  # noqa: B008
):
    sessions = session_controller.get_user_sessions(
        db=db,
        user_id=user_id,
    )

    return {
        "sessions": [
            {
                "session_id": session.id,
                "user_id": session.user_id,
                "created_at": session.created_at,
            }
            for session in sessions
        ],
    }


# =========================================================
# Get chat history
# =========================================================

@router.get(
    "/sessions/{session_id}/messages",
    response_model=MessageListResponse,
)
async def get_messages(
    session_id: str,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),   # noqa: B008
    session_controller: SessionController = Depends(get_session_controller,),   # noqa: B008
):
    messages = session_controller.get_messages(
        db=db,
        session_id=session_id,
        user_id=user_id,
    )

    return {
        "session_id": session_id,
        "messages": [
            {
                "id": message.id,
                "session_id": message.session_id,
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at,
            }
            for message in messages
        ],
    }


# =========================================================
# Add message to chat
# =========================================================

@router.post(
    "/sessions/{session_id}/messages",
    response_model=MessageOutput,
    status_code=status.HTTP_201_CREATED,
)
async def add_message(
    session_id: str,
    request: MessageInput,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),  # noqa: B008
    session_controller: SessionController = Depends(get_session_controller,),   # noqa: B008
):
    message = session_controller.add_message(
        db=db,
        session_id=session_id,
        user_id=user_id,
        role=request.role,
        content=request.content,
    )

    return {
        "id": message.id,
        "session_id": message.session_id,
        "role": message.role,
        "content": message.content,
        "created_at": message.created_at,
    }


# =========================================================
# Delete chat session
# =========================================================

@router.delete(
    "/sessions/{session_id}",
)
async def delete_session(
    session_id: str,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),   # noqa: B008
    session_controller: SessionController = Depends(get_session_controller,),   # noqa: B008
):
    return session_controller.delete_session(
        db=db,
        session_id=session_id,
        user_id=user_id,
    )