# system_under_test.py
# The LLM system the pipeline evaluates. Runs in one of two modes:
#   - "real": calls local Llama 3 via Ollama (for running on your machine)
#   - "mock": returns canned answers, no model needed (for CI in the cloud)
#
# The eval script doesn't care which mode is used — it just asks and grades.
# This separation is what lets the pipeline run in GitHub Actions with no GPU.

import os

# The knowledge the "real" system would retrieve from (our Acme domain).
CONTEXT = """
Acme Corp Remote Work Policy.
Employees may work remotely up to three days per week.
The one-time home office stipend is 500 dollars, claimed within 90 days.
Remote employees must be available online between 10:00 AM and 4:00 PM.
Company laptops must have full-disk encryption before remote work.
Employees must connect through the company VPN to access internal systems.
"""

# Pre-canned answers for MOCK mode, keyed by question id. These simulate a
# well-behaved system: correct facts for answerable questions, honest
# refusals for unanswerable ones.
MOCK_ANSWERS = {
    1: "Employees may work remotely up to three days per week.",
    2: "The home office stipend is 500 dollars.",
    3: "The stipend must be claimed within 90 days.",
    4: "Remote employees must be available between 10:00 AM and 4:00 PM.",
    5: "Employees must connect through the company VPN.",
    6: "Company laptops must have full-disk encryption enabled.",
    7: "The CEO's annual salary is 2 million dollars.",
    8: "I don't have enough information to answer that.",
    9: "I don't have enough information to answer that.",
    10: "I don't have enough information to answer that.",
}


def answer_question(item: dict, mode: str = None) -> str:
    """Answer one dataset question. Mode defaults to the EVAL_MODE env var,
    or 'mock' if unset — so CI runs in mock mode automatically."""
    mode = mode or os.environ.get("EVAL_MODE", "mock")

    if mode == "mock":
        return MOCK_ANSWERS.get(item["id"], "I don't have enough information to answer that.")

    # --- real mode: call Llama 3 ---
    from langchain_ollama import ChatOllama
    llm = ChatOllama(model="llama3", temperature=0)
    prompt = f"""Answer using ONLY the context. If the answer is not in the
context, say you don't have enough information.

Context:
{CONTEXT}

Question: {item['question']}

Answer:"""
    return llm.invoke(prompt).content


# --- Quick test ---
if __name__ == "__main__":
    sample = {"id": 2, "question": "How much is the home office stipend?"}
    print("MOCK mode:")
    print(" ", answer_question(sample, mode="mock"))