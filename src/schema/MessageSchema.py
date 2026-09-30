from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class MessageInput(BaseModel):
    role: Literal["user", "assistant"]

    content: str = Field(
        min_length=1,
        max_length=20000,
    )


class MessageOutput(BaseModel):
    id: str
    session_id: str
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime


class MessageListResponse(BaseModel):
    session_id: str
    messages: list[MessageOutput]