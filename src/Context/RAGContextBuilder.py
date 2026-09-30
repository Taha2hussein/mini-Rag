from typing import Any

from .ContextBuilderInterface import ContextBuilderInterface


class RAGContextBuilder(ContextBuilderInterface):

    def build(
        self,
        results: list[Any],
    ) -> str:

        if not results:
            return "No relevant context was found."

        context_parts: list[str] = []

        for index, result in enumerate(results, start=1):
            payload = getattr(result, "payload", None) or {}

            text = payload.get("text", "").strip()
            source = payload.get("source", "")
            document_id = payload.get("document_id", "")
            chunk_index = payload.get("chunk_index", 0)

            if not text:
                continue

            context_parts.append(
                f"""[Context {index}]
Source: {source}
Document ID: {document_id}
Chunk: {chunk_index}

{text}
"""
            )

        if not context_parts:
            return "No relevant context was found."

        return "\n".join(context_parts)