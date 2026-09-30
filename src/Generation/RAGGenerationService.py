from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from Configuration.config import get_settings
from Database.models import Session as SessionModel, Message

from Context import get_context_builder
from ContextFiltering import get_context_quality_filter
from Embeddings import get_embedding_service
from VectorStore import get_vector_store
from LLM import get_llm_service
from Reranking import get_reranking_pipeline

from .GenerationInterface import GenerationInterface


class RAGGenerationService(GenerationInterface):

    def __init__(self, db: Session):
        self.db = db

        # Application settings
        self.settings = get_settings()

        # RAG services
        self.embedding_service = get_embedding_service()
        self.vector_store = get_vector_store()
        self.reranking_pipeline = get_reranking_pipeline()
        self.context_quality_filter = get_context_quality_filter()
        self.context_builder = get_context_builder()

        # LLM
        self.llm = get_llm_service()

    async def generate(
        self,
        question: str,
        session_id: str,
        user_id: int,
    ) -> dict:

        # =========================================================
        # 1. Validate session ownership
        # =========================================================

        session = (
            self.db.query(SessionModel)
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

        # =========================================================
        # 2. Load conversation history
        # =========================================================

        history = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in session.messages
        ]

        # =========================================================
        # 3. Generate query embedding
        #
        # BGE-M3 produces:
        # - Dense vector
        # - Sparse lexical weights
        # =========================================================

        embedding_result = await run_in_threadpool(
            self.embedding_service.encode,
            [question],
        )

        dense_vector = embedding_result["dense_vecs"][0]
        sparse_weights = embedding_result["lexical_weights"][0]

        query = {
            "dense": dense_vector.tolist(),
            "sparse": {
                "indices": list(sparse_weights.keys()),
                "values": list(sparse_weights.values()),
            },
        }

        # =========================================================
        # 4. First-stage retrieval
        #
        # Qdrant retrieves more candidates for better recall.
        #
        # Example:
        # Top 20 candidates
        # =========================================================

        candidates = await run_in_threadpool(
            self.vector_store.search,
            query,
            user_id,
            self.settings.RAG_RETRIEVAL_LIMIT,
        )

        # =========================================================
        # 5. Reranking
        #
        # BGE Reranker evaluates:
        #
        #     query <-> document
        #
        # and sorts candidates by relevance.
        # =========================================================

        reranked_results = await run_in_threadpool(
            self.reranking_pipeline.rerank_results,
            question,
            candidates,
            self.settings.RAG_RETRIEVAL_LIMIT,
        )

        # =========================================================
        # 6. Relevance Gate
        #
        # We only continue if the best reranker result
        # passes the configured relevance threshold.
        # =========================================================

        if not reranked_results:
            answer = (
                "I couldn't find this information "
                "in your documents."
            )

            self._save_messages(
                session_id=session_id,
                question=question,
                answer=answer,
            )

            return {
                "session_id": session_id,
                "question": question,
                "answer": answer,
                "sources": [],
            }

        best_score = float(
            reranked_results[0]["reranker_score"]
        )

        threshold = (
            self.settings.RERANKER_RELEVANCE_THRESHOLD
        )

        if best_score < threshold:
            answer = (
                "I couldn't find this information "
                "in your documents."
            )

            self._save_messages(
                session_id=session_id,
                question=question,
                answer=answer,
            )

            return {
                "session_id": session_id,
                "question": question,
                "answer": answer,
                "sources": [],
            }

        # =========================================================
        # 7. Context Quality Filtering
        #
        # Remove:
        # - Weak results
        # - Empty chunks
        # - Obvious Table Of Contents chunks
        #
        # Then keep only the configured number of results.
        # =========================================================

        filtered_results = await run_in_threadpool(
            self.context_quality_filter.filter,
            reranked_results,
            self.settings.CONTEXT_MIN_RERANKER_SCORE,
            self.settings.CONTEXT_MAX_RESULTS,
        )

        # =========================================================
        # 8. Make sure we still have usable context
        # =========================================================

        if not filtered_results:
            answer = (
                "I couldn't find enough relevant information "
                "in your documents."
            )

            self._save_messages(
                session_id=session_id,
                question=question,
                answer=answer,
            )

            return {
                "session_id": session_id,
                "question": question,
                "answer": answer,
                "sources": [],
            }

        # =========================================================
        # 9. Extract original Qdrant results
        #
        # ContextBuilder expects Qdrant result objects,
        # while filtered_results contain:
        #
        # {
        #     "result": qdrant_result,
        #     "reranker_score": ...
        # }
        # =========================================================

        final_results = [
            item["result"]
            for item in filtered_results
        ]

        # =========================================================
        # 10. Build final context
        # =========================================================

        context = self.context_builder.build(
            final_results
        )

        # =========================================================
        # 11. Generate grounded answer
        #
        # DeepSeek receives:
        # - Conversation history
        # - Current question
        # - Clean RAG context
        # =========================================================

        answer = await self.llm.generate(
            question=question,
            context=context,
            history=history,
        )

        # =========================================================
        # 12. Save conversation
        # =========================================================

        self._save_messages(
            session_id=session_id,
            question=question,
            answer=answer,
        )

        # =========================================================
        # 13. Build sources
        # =========================================================

        sources = []

        for item in filtered_results:

            result = item["result"]

            payload = result.payload or {}

            sources.append(
                {
                    "source": payload.get(
                        "source",
                        "",
                    ),
                    "document_id": payload.get(
                        "document_id",
                        "",
                    ),
                    "chunk_index": payload.get(
                        "chunk_index",
                        0,
                    ),
                    "retrieval_score": float(
                        result.score
                    ),
                    "reranker_score": float(
                        item["reranker_score"]
                    ),
                }
            )

        # =========================================================
        # 14. Final response
        # =========================================================

        return {
            "session_id": session_id,
            "question": question,
            "answer": answer,
            "sources": sources,
        }

    # =============================================================
    # Private helper
    # =============================================================

    def _save_messages(
        self,
        session_id: str,
        question: str,
        answer: str,
    ) -> None:

        user_message = Message(
            session_id=session_id,
            role="user",
            content=question,
        )

        assistant_message = Message(
            session_id=session_id,
            role="assistant",
            content=answer,
        )

        self.db.add(user_message)
        self.db.add(assistant_message)

        self.db.commit()