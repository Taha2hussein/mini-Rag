from pydantic import BaseModel, Field


class GenerationInput(BaseModel):
    session_id: str = Field(
        min_length=1,
        max_length=36,
    )

    question: str = Field(
        min_length=1,
        max_length=5000,
    )


class GenerationSource(BaseModel):
    source: str
    document_id: str
    chunk_index: int
    retrieval_score: float
    reranker_score: float


class GenerationResponse(BaseModel):
    session_id: str
    question: str
    answer: str
    sources: list[GenerationSource]