from fastapi import HTTPException
from sqlalchemy.orm import Session

from Database.models import (
    Message,
    Session as SessionModel,
)


class SessionController:

    # =====================================================
    # Create Session
    # =====================================================

    def create_session(
        self,
        db: Session,
        user_id: int,
    ):

        session = SessionModel(
            user_id=user_id,
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        return session

    # =====================================================
    # Get User Sessions
    # =====================================================

    def get_user_sessions(
        self,
        db: Session,
        user_id: int,
    ):

        sessions = (
            db.query(SessionModel)
            .filter(
                SessionModel.user_id == user_id,
            )
            .order_by(
                SessionModel.created_at.desc(),
            )
            .all()
        )

        return sessions

    # =====================================================
    # Get One Session
    #
    # Also verifies that the session belongs
    # to the authenticated user.
    # =====================================================

    def get_session(
        self,
        db: Session,
        session_id: str,
        user_id: int,
    ):

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

        return session

    # =====================================================
    # Get Chat History
    # =====================================================

    def get_messages(
        self,
        db: Session,
        session_id: str,
        user_id: int,
    ):

        # First verify session ownership.
        self.get_session(
            db=db,
            session_id=session_id,
            user_id=user_id,
        )

        messages = (
            db.query(Message)
            .filter(
                Message.session_id == session_id,
            )
            .order_by(
                Message.created_at.asc(),
            )
            .all()
        )

        return messages

    # =====================================================
    # Add Message
    # =====================================================

    def add_message(
        self,
        db: Session,
        session_id: str,
        user_id: int,
        role: str,
        content: str,
    ):

        # Verify that the session belongs to the user.
        self.get_session(
            db=db,
            session_id=session_id,
            user_id=user_id,
        )

        message = Message(
            session_id=session_id,
            role=role,
            content=content,
        )

        db.add(message)
        db.commit()
        db.refresh(message)

        return message

    # =====================================================
    # Delete Session
    # =====================================================

    def delete_session(
        self,
        db: Session,
        session_id: str,
        user_id: int,
    ):

        session = self.get_session(
            db=db,
            session_id=session_id,
            user_id=user_id,
        )

        db.delete(session)
        db.commit()

        return {
            "message": "Session deleted successfully.",
            "session_id": session_id,
        }


def get_session_controller() -> SessionController:
    return SessionController()