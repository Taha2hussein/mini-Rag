from sqlalchemy.orm import Session

from .GenerationInterface import GenerationInterface
from .RAGGenerationService import RAGGenerationService


def get_generation_service(
    db: Session,
) -> GenerationInterface:

    return RAGGenerationService(db=db)