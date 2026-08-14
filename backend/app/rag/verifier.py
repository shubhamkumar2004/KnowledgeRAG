import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:3b"


def verify_answer(
    question: str,
    context: str,
    answer: str
) -> bool:
    """
    Verify whether the generated answer is supported by
    the retrieved context.

    Returns:
        True  -> Answer is supported.
        False -> Answer is unsupported.
    """

    prompt = f"""
You are verifying an answer against the provided context.

Your job is NOT to judge writing quality.

Only determine whether the answer contradicts the context.

Rules:

1. If the answer is generally supported by the context,
   reply YES.

2. Minor rewording, summarization and paraphrasing are acceptable.

3. Reply NO only if the answer introduces important facts
   that are missing from or contradict the context.

4. If the answer is only a concise summary of the context,
   reply YES.

Reply using ONLY one of these formats:

YES

or

NO

QUESTION:
{question}

CONTEXT:
{context}

ANSWER:
{answer}

VERDICT:
""".strip()

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0
            }
        },
        timeout=60
    )

    response.raise_for_status()

    verdict = response.json()["response"].strip()

    # Debug output
    print("\n========== VERIFIER ==========")
    print(verdict)
    print("==============================\n")

    return verdict.upper().startswith("YES")