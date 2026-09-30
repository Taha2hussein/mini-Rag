from typing import Any

import httpx

from .LLMInterface import LLMInterface


class DeepSeekLLMService(LLMInterface):

    MODEL_NAME = "deepseek-r1:7b"
    OLLAMA_URL = "http://localhost:11434/api/chat"

    SYSTEM_PROMPT = """
You are a document-grounded AI assistant.

Your job is to answer the user's question using the provided
RAG context as the ONLY source of factual information.

STRICT RULES:

1. Use ONLY information explicitly supported by the RAG context.

2. Do NOT use your general knowledge to add facts, commands,
   steps, examples, or explanations that are not supported
   by the RAG context.

3. NEVER invent or modify a command.

4. NEVER change the meaning of a command.

5. NEVER combine separate commands into a workflow unless
   the RAG context explicitly presents them as one workflow.

6. If the RAG context presents multiple alternatives,
   preserve them as alternatives.

7. Do NOT turn an alternative into a sequential step.

8. Answer only what the user asked.

9. Do NOT add unrelated steps such as cloning, committing,
   pushing, merging, or pull requests unless the user
   explicitly asks about them or the RAG context clearly
   requires them to answer the question.

10. When presenting a command, copy the command exactly
    from the RAG context whenever possible.

11. If the context says that command A creates a branch
    and switches to it, do not claim that another command
    performs the same action.

12. Conversation history is provided only to understand
    conversational context. It is NOT a factual source.

13. The RAG context is the factual source.

14. If the answer cannot be determined from the RAG context,
    say clearly that the information was not found in the
    provided documents.

15. Do not guess.

16. Do not add a "helpful" step that is not supported by
    the documents.

Before answering, internally verify every factual statement
and every command against the RAG context.
"""

    async def generate(
        self,
        question: str,
        context: str,
        history: list[dict[str, str]] | None = None,
    ) -> str:

        if not question.strip():
            raise ValueError(
                "question must not be empty."
            )

        if not context.strip():
            raise ValueError(
                "context must not be empty."
            )

        messages: list[dict[str, str]] = [
            {
                "role": "system",
                "content": self.SYSTEM_PROMPT,
            }
        ]

        # ---------------------------------------------------------
        # Conversation history
        #
        # History helps the model understand the conversation,
        # but the system prompt explicitly prevents it from
        # being treated as factual evidence.
        # ---------------------------------------------------------

        if history:

            for message in history:

                role = message.get("role")
                content = message.get("content")

                if role not in {"user", "assistant"}:
                    continue

                if not content:
                    continue

                messages.append(
                    {
                        "role": role,
                        "content": content,
                    }
                )

        # ---------------------------------------------------------
        # Current question + RAG evidence
        # ---------------------------------------------------------

        user_prompt = f"""
RAG CONTEXT
===========
{context}

END RAG CONTEXT


CURRENT USER QUESTION
=====================
{question}


ANSWERING REQUIREMENTS
======================

Answer the current question using the RAG context only.

For every command or factual statement:

- Verify that it is supported by the RAG context.
- Do not invent missing commands.
- Do not change the meaning of commands.
- Do not combine alternatives into a sequence.
- Do not add unrelated workflow steps.

If the context provides multiple ways to accomplish something,
present them as separate alternatives.

If the context does not contain enough information to answer
the question, explicitly say that the information was not
found in the provided documents.
"""

        messages.append(
            {
                "role": "user",
                "content": user_prompt,
            }
        )

        payload: dict[str, Any] = {
            "model": self.MODEL_NAME,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.0,
            },
        }

        async with httpx.AsyncClient(
            timeout=300.0
        ) as client:

            response = await client.post(
                self.OLLAMA_URL,
                json=payload,
            )

        response.raise_for_status()

        data = response.json()

        answer = (
            data
            .get("message", {})
            .get("content")
        )

        if not answer:
            raise RuntimeError(
                "Ollama returned an empty response."
            )

        return answer.strip()