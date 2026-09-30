from Context import get_context_builder


class FakeResult:

    def __init__(self, payload: dict):
        self.payload = payload


def main():

    results = [
        FakeResult(
            {
                "text": (
                    "A Git branch is an independent line of development "
                    "that allows developers to work on changes separately."
                ),
                "source": "github.pdf",
                "document_id": "document-123",
                "chunk_index": 0,
            }
        ),
        FakeResult(
            {
                "text": (
                    "Developers can create branches to work on features "
                    "without affecting the main branch."
                ),
                "source": "github.pdf",
                "document_id": "document-123",
                "chunk_index": 1,
            }
        ),
    ]

    context_builder = get_context_builder()

    context = context_builder.build(results)

    print("\n========================================")
    print("CONTEXT BUILDER TEST")
    print("========================================")
    print(context)
    print("========================================")


if __name__ == "__main__":
    main()