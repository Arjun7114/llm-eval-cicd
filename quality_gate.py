# quality_gate.py
# Reads the metrics from evaluate.py and decides PASS or FAIL against
# thresholds. Exits with code 0 (pass) or 1 (fail). The exit code is what
# GitHub Actions reads to allow or block a change.

import json
import sys

# --- The thresholds. These are the quality bar every change must clear. ---
THRESHOLDS = {
    "min_accuracy": 90.0,          # accuracy must be at least this
    "max_hallucination_rate": 5.0, # hallucination must be at most this
    "max_avg_latency_ms": 2000.0,  # avg latency must be under this
}

def check_gate():
    with open("results.json", "r", encoding="utf-8") as f:
        m = json.load(f)

    print("QUALITY GATE\n")
    failures = []

    # Each check: compare a metric to its threshold.
    if m["accuracy"] < THRESHOLDS["min_accuracy"]:
        failures.append(f"Accuracy {m['accuracy']}% is below minimum {THRESHOLDS['min_accuracy']}%")
    print(f"  Accuracy           : {m['accuracy']}%  (min {THRESHOLDS['min_accuracy']}%)")

    if m["hallucination_rate"] > THRESHOLDS["max_hallucination_rate"]:
        failures.append(f"Hallucination rate {m['hallucination_rate']}% exceeds max {THRESHOLDS['max_hallucination_rate']}%")
    print(f"  Hallucination rate : {m['hallucination_rate']}%  (max {THRESHOLDS['max_hallucination_rate']}%)")

    if m["avg_latency_ms"] > THRESHOLDS["max_avg_latency_ms"]:
        failures.append(f"Latency {m['avg_latency_ms']}ms exceeds max {THRESHOLDS['max_avg_latency_ms']}ms")
    print(f"  Avg latency        : {m['avg_latency_ms']}ms  (max {THRESHOLDS['max_avg_latency_ms']}ms)")

    print()
    if failures:
        print("GATE FAILED:")
        for fail in failures:
            print(f"  X  {fail}")
        sys.exit(1)   # non-zero exit -> CI blocks the change
    else:
        print("GATE PASSED — all metrics within thresholds.")
        sys.exit(0)   # zero exit -> CI allows the change

if __name__ == "__main__":
    check_gate()