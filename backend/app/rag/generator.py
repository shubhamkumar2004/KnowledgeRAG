import time
import requests

from app.rag.retriever import retrieve


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:3b"


def build_context(results: list[dict]) -> str:
    """
    Convert retrieved chunks into one context block
    that can be given to the LLM.
    """

    context_parts = []

    for index, result in enumerate(results, start=1):

        context_parts.append(
            f"[Source {index}: {result['source']}]\n"
            f"{result['document']}"
        )

    return "\n\n".join(context_parts)


def build_prompt(question: str, context: str) -> str:
    """
    Create a grounded prompt for Qwen.
    """

    return f"""
You are a question-answering assistant for the Ekta Navnirman Trust website.

Your job is to answer the user's question using ONLY the information
provided in the CONTEXT.

STRICT RULES:

1. Use ONLY information explicitly present in the CONTEXT.

2. Do NOT use your own knowledge.

3. Do NOT invent information.

4. Preserve names, dates, phone numbers, email addresses,
amounts, percentages, eligibility, and scheme names exactly.

5. Do NOT rename schemes.

6. Government schemes mentioned on the website are NOT
necessarily run by Ekta Trust.

7. If the retrieved context does not contain enough information,
reply exactly:

I could not find this information in the available Ekta Trust data.

8. Keep answers concise.

CONTEXT:
{context}

USER QUESTION:
{question}

ANSWER:
""".strip()


def generate_answer(
    question: str,
    top_k: int = 5
) -> dict:
    """
    Complete RAG pipeline.

    Returns:
    {
        "answer": "...",
        "sources": [...],
        "response_time": 2.31
    }
    """

    total_start = time.time()

    # ---------------------------
    # Retrieve
    # ---------------------------

    retrieval_start = time.time()

    results = retrieve(
        question=question,
        top_k=top_k
    )

    retrieval_time = time.time() - retrieval_start

    print(
        f"\nRetrieval time: "
        f"{retrieval_time:.2f} seconds"
    )

    # ---------------------------
    # Build Context
    # ---------------------------

    context = build_context(results)

    prompt = build_prompt(
        question=question,
        context=context
    )

    # ---------------------------
    # Generate
    # ---------------------------

    generation_start = time.time()

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1
            }
        },
        timeout=120
    )

    generation_time = time.time() - generation_start

    print(
        f"LLM generation time: "
        f"{generation_time:.2f} seconds"
    )

    response.raise_for_status()

    answer = response.json()["response"].strip()

    total_time = time.time() - total_start

    # Remove duplicate sources while preserving order
    seen = set()
    sources = []

    for result in results:
        source = result["source"]

        if source not in seen:
            seen.add(source)
            sources.append(source)

    return {
        "answer": answer,
        "sources": sources,
        "response_time": round(total_time, 2)
    }


if __name__ == "__main__":

    question = "What are the details of the Education Loan Scheme?"

    print("\nQUESTION:")
    print(question)

    print("\nANSWER:")

    result = generate_answer(question)

    print("\n" + result["answer"])

    print("\nSources:")

    for source in result["sources"]:
        print("-", source)

    print(
        f"\nTotal RAG time: "
        f"{result['response_time']:.2f} seconds"
    )