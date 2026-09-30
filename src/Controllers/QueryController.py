from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from Database.models import Session as SessionModel
from Embeddings import get_embedding_service
from VectorStore import get_vector_store


class QueryController:

    def __init__(self):
        pass

    async def query(
        self,
        query_text: str,
        session_id: str | None,
        user_id: int,
        db: Session,
        limit: int = 5,
    ):

        # --------------------------------------------------
        # 1. Validate session ownership if session_id exists
        # --------------------------------------------------

        if session_id is not None:

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

        # --------------------------------------------------
        # 2. Generate query embeddings
        # --------------------------------------------------

        embedding_service = get_embedding_service()

        embedding_result = await run_in_threadpool(
            embedding_service.encode,
            [query_text],
        )

        dense_vector = embedding_result["dense_vecs"][0]

        sparse_weights = (
            embedding_result["lexical_weights"][0]
        )

        query = {
            "dense": dense_vector.tolist(),
            "sparse": {
                "indices": list(
                    sparse_weights.keys()
                ),
                "values": list(
                    sparse_weights.values()
                ),
            },
        }

        # --------------------------------------------------
        # 3. Hybrid search
        #
        # IMPORTANT:
        # Qdrant searches by user_id ONLY.
        #
        # session_id does NOT affect retrieval.
        # --------------------------------------------------

        vector_store = get_vector_store()

        results = await run_in_threadpool(
            vector_store.search,
            query,
            user_id,
            limit,
        )

        # --------------------------------------------------
        # 4. Format results
        # --------------------------------------------------

        formatted_results = []

        for result in results:

            payload = result.payload or {}

            formatted_results.append(
                {
                    "point_id": str(result.id),
                    "score": result.score,
                    "text": payload.get(
                        "text",
                        "",
                    ),
                    "source": payload.get(
                        "source",
                        "",
                    ),
                    "document_id": payload.get(
                        "document_id",
                        "",
                    ),
                    "session_id": payload.get(
                        "session_id",
                        "",
                    ),
                    "chunk_index": payload.get(
                        "chunk_index",
                        0,
                    ),
                }
            )

        return {
            "query": query_text,
            "results": formatted_results,
        }


def get_query_controller() -> QueryController:
    return QueryController()