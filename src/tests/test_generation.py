import asyncio

from LLM import get_llm_service


async def main():
    llm = get_llm_service()

    answer = await llm.generate(
        question="What is a Git branch?",
        context=(
            "A Git branch is an independent line of development "
            "that allows developers to work on changes separately."
        ),
    )

    print("\n========================================")
    print("GENERATION TEST")
    print("========================================")
    print(f"Answer:\n{answer}")
    print("========================================")


if __name__ == "__main__":
    asyncio.run(main())