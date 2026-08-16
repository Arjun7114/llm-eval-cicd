# evaluate.py
# The core evaluation. Runs the golden dataset through the system-under-test,
# grades each answer, computes metrics, prints a report, and saves results.

import json
import time
from tabulate import tabulate
from system_under_test import answer_question

REFUSAL_PHRASES = [
    "don't have enough", "do not have enough", "don't know", "do not know",
    "not mention", "no information", "cannot answer", "can't answer",
    "not provide", "not contain", "unable to",
]

def is_refusal(answer: str) -> bool:
    a = answer.lower()
    return any(p in a for p in REFUSAL_PHRASES)

def grade(item: dict, answer: str) -> bool:
    """Grade one answer against the golden dataset entry."""
    if item["answerable"]:
        # Correct = did NOT refuse AND contains an expected keyword.
        if is_refusal(answer):
            return False
        return any(kw.lower() in answer.lower() for kw in item["expected_keywords"])
    else:
        # Correct = DID refuse (didn't hallucinate).
        return is_refusal(answer)

def run_evaluation():
    with open("data/golden_dataset.json", "r", encoding="utf-8") as f:
        dataset = json.load(f)

    rows = []
    correct = 0
    total_latency = 0.0
    hallucinations = 0
    unanswerable_count = 0

    for item in dataset:
        start = time.time()
        answer = answer_question(item)
        latency = time.time() - start
        total_latency += latency

        is_correct = grade(item, answer)
        if is_correct:
            correct += 1

        # A hallucination = an unanswerable question that got a non-refusal answer.
        if not item["answerable"]:
            unanswerable_count += 1
            if not is_refusal(answer):
                hallucinations += 1

        rows.append([
            item["id"],
            "yes" if item["answerable"] else "no",
            "PASS" if is_correct else "FAIL",
            f"{latency*1000:.0f}ms",
            answer[:45] + ("..." if len(answer) > 45 else ""),
        ])

    total = len(dataset)
    accuracy = correct / total * 100
    hallucination_rate = (hallucinations / unanswerable_count * 100) if unanswerable_count else 0
    avg_latency_ms = (total_latency / total) * 1000

    # --- Print the report ---
    print("\n" + tabulate(rows,
          headers=["ID", "Answerable", "Result", "Latency", "Answer"],
          tablefmt="github"))

    metrics = {
        "accuracy": round(accuracy, 1),
        "hallucination_rate": round(hallucination_rate, 1),
        "avg_latency_ms": round(avg_latency_ms, 1),
        "total_questions": total,
        "passed": correct,
    }

    print("\nMETRICS")
    print(f"  Accuracy            : {metrics['accuracy']}%  ({correct}/{total})")
    print(f"  Hallucination rate  : {metrics['hallucination_rate']}%")
    print(f"  Avg latency         : {metrics['avg_latency_ms']} ms")

    # Save for the CI gate and history.
    with open("results.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print("\nSaved metrics to results.json")

    return metrics

if __name__ == "__main__":
    run_evaluation()