from datetime import datetime

from pydantic import BaseModel


class SessionOutput(BaseModel):
    session_id: str
    user_id: int
    created_at: datetime


class SessionListResponse(BaseModel):
    sessions: list[SessionOutput]