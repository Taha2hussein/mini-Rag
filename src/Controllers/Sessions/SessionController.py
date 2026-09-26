from sqlalchemy.orm import Session

from Database.models import Session as SessionModel


class SessionController:

    def create_session(self, db: Session):
        session = SessionModel()

        db.add(session)
        db.commit()
        db.refresh(session)

        return {
            "session_id": session.id
        }


def get_session_controller():
    return SessionController()