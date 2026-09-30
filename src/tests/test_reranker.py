from Reranking import get_reranker_service


def main():

    query = "What is the capital of Japan?"

    documents = [
        """
        Git branches allow developers to work on different
        lines of development without affecting the main branch.
        """,

        """
        Git clone downloads a repository from a remote URL
        to the local machine.
        """,

        """
        Japan is an island country in East Asia.
        Tokyo is the capital of Japan.
        """,

        """
        Large language model evaluation includes offline
        evaluation pipelines and regression detection.
        """,
    ]

    reranker = get_reranker_service()

    results = reranker.rerank(
        query=query,
        documents=documents,
    )

    print("\n========================================")
    print("RERANKER TEST")
    print("========================================")

    print(f"Query: {query}\n")

    for result in results:

        print(f"Score: {result['score']:.6f}")
        print(f"Original Index: {result['index']}")
        print(f"Text: {result['text'].strip()}")
        print("----------------------------------------")

    print("========================================")


if __name__ == "__main__":
    main()