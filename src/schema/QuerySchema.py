from pydantic import BaseModel, Field


class QueryInput(BaseModel):

    session_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=36,
    )

    query: str = Field(
        min_length=1,
        max_length=5000,
    )


class QueryResult(BaseModel):

    point_id: str
    score: float
    text: str
    source: str
    document_id: str
    session_id: str
    chunk_index: int


class QueryResponse(BaseModel):

    query: str
    results: list[QueryResult]