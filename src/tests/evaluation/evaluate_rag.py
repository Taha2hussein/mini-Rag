import json
import time
from pathlib import Path

import requests


BASE_URL = "http://localhost:5004"
ENDPOINT = f"{BASE_URL}/generation/generate"

QUESTIONS_FILE = Path(__file__).parent / "rag_questions.json"

JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyLCJleHAiOjE3OTA3NTM0MDV9.mZkMiXCzzVO9YZj2mtPoV74xma708wIubokpiKRbAFI"

SESSION_ID = "7a3ea9dc-c560-4e92-ac2f-d26ec646529d"


NO_ANSWER_MARKERS = [
    "couldn't find",
    "could not find",
    "not found",
    "not available",
    "not provided",
    "information was not found",
    "don't have enough information",
]


def load_questions():
    with open(
        QUESTIONS_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def check_keywords(
    text: str,
    expected_keywords: list[str],
) -> bool:

    if not expected_keywords:
        return True

    normalized_text = text.lower()

    return all(
        keyword.lower() in normalized_text
        for keyword in expected_keywords
    )


def check_no_answer(text: str) -> bool:

    normalized_text = text.lower()

    return any(
        marker in normalized_text
        for marker in NO_ANSWER_MARKERS
    )


def evaluate_question(question_data: dict):

    question = question_data["question"]

    expected_keywords = question_data[
        "expected_keywords"
    ]

    should_have_answer = question_data[
        "should_have_answer"
    ]

    payload = {
        "session_id": SESSION_ID,
        "question": question,
    }

    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Content-Type": "application/json",
    }

    start_time = time.perf_counter()

    response = requests.post(
        ENDPOINT,
        json=payload,
        headers=headers,
        timeout=300,
    )

    latency = time.perf_counter() - start_time

    response.raise_for_status()

    data = response.json()

    answer = data["answer"]

    sources = data.get(
        "sources",
        [],
    )

    retrieval_hit = len(sources) > 0

    if should_have_answer:

        generation_match = check_keywords(
            answer,
            expected_keywords,
        )

        evaluation_passed = generation_match

    else:

        generation_match = check_no_answer(
            answer
        )

        evaluation_passed = (
            not retrieval_hit
            and generation_match
        )

    return {
        "question": question,
        "retrieval_hit": retrieval_hit,
        "generation_match": generation_match,
        "evaluation_passed": evaluation_passed,
        "latency": latency,
        "answer": answer,
    }


def main():

    questions = load_questions()

    results = []

    print()
    print("=" * 60)
    print("RAG Evaluation")
    print("=" * 60)

    for index, question_data in enumerate(
        questions,
        start=1,
    ):

        print()

        print(
            f"[{index}/{len(questions)}] "
            f"{question_data['question']}"
        )

        try:

            result = evaluate_question(
                question_data
            )

            results.append(result)

            retrieval_status = (
                "PASS"
                if result["retrieval_hit"]
                else "FAIL"
            )

            generation_status = (
                "PASS"
                if result["generation_match"]
                else "FAIL"
            )

            evaluation_status = (
                "PASS"
                if result["evaluation_passed"]
                else "FAIL"
            )

            print(
                f"Retrieval:  {retrieval_status}"
            )

            print(
                f"Generation: {generation_status}"
            )

            print(
                f"Evaluation: {evaluation_status}"
            )

            print(
                f"Latency:    "
                f"{result['latency']:.2f}s"
            )

        except Exception as error:

            print(
                f"ERROR: {error}"
            )

    if not results:

        print()
        print("No evaluation results.")

        return

    total = len(results)

    retrieval_hits = sum(
        result["retrieval_hit"]
        for result in results
    )

    generation_matches = sum(
        result["generation_match"]
        for result in results
    )

    evaluation_passes = sum(
        result["evaluation_passed"]
        for result in results
    )

    average_latency = (
        sum(
            result["latency"]
            for result in results
        )
        / total
    )

    retrieval_rate = (
        retrieval_hits / total
    ) * 100

    generation_rate = (
        generation_matches / total
    ) * 100

    evaluation_rate = (
        evaluation_passes / total
    ) * 100

    print()

    print("=" * 60)
    print("RAG Evaluation Summary")
    print("=" * 60)

    print(
        f"Questions:          {total}"
    )

    print(
        f"Retrieval Hit Rate: "
        f"{retrieval_rate:.1f}%"
    )

    print(
        f"Generation Match:   "
        f"{generation_rate:.1f}%"
    )

    print(
        f"Evaluation Pass:    "
        f"{evaluation_rate:.1f}%"
    )

    print(
        f"Average Latency:    "
        f"{average_latency:.2f}s"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()