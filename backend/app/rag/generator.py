import time
import requests
from app.rag.verifier import verify_answer
from app.rag.retriever import retrieve
from app.services.memory import (
    get_history,
    save_message
)
from app.rag.query_rewriter import rewrite_question


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:3b"

SMALL_TALK = {
    "hi": "Hello! 👋\n\nI'm the Ekta Trust AI Assistant.\nHow can I help you today?",

    "hello": "Hello! 👋\n\nI'm the Ekta Trust AI Assistant.\nHow can I help you today?",

    "hey": "Hello! 👋\n\nI'm the Ekta Trust AI Assistant.\nHow can I help you today?",

    "good morning": "Good morning! 👋\n\nHow can I help you today?",

    "good afternoon": "Good afternoon! 👋\n\nHow can I help you today?",

    "good evening": "Good evening! 👋\n\nHow can I help you today?",

    "thanks": "You're welcome! 😊\n\nIf you have any other questions about Ekta Trust, feel free to ask.",

    "thank you": "You're welcome! 😊\n\nIf you have any other questions about Ekta Trust, feel free to ask.",

    "bye": "Goodbye! 👋\n\nThank you for using the Ekta Trust AI Assistant. Have a great day!",

    "goodbye": "Goodbye! 👋\n\nThank you for using the Ekta Trust AI Assistant. Have a great day!"
}


def build_context(results: list[dict]) -> str:
    """
    Convert retrieved chunks into a single context block.

    Internal filenames are intentionally omitted so the
    chatbot never exposes implementation details.
    """

    context_parts = []

    for result in results:
        context_parts.append(result["document"])

    return "\n\n".join(context_parts)


def build_chat_history(history: list[dict]) -> str:
    """
    Convert previous conversation into plain text.
    """

    if not history:
        return "No previous conversation."

    lines = []

    for message in history:

        role = (
            "User"
            if message["role"] == "user"
            else "Assistant"
        )

        lines.append(
            f"{role}: {message['content']}"
        )

    return "\n".join(lines)


def build_prompt(
    question: str,
    context: str,
    history: str
) -> str:
    """
    Build the prompt for Qwen.
    """

    return f"""
You are a question-answering assistant for the Ekta Navnirman Trust website.

You will receive:

1. Previous conversation
2. Retrieved website context
3. Current user question

Use the previous conversation ONLY to understand follow-up questions.

Use ONLY the retrieved CONTEXT to answer.

STRICT RULES

1. Never answer using your own knowledge.

2. Never invent information.

3. Use the conversation history only to understand references like:
   "it", "that", "this", "maximum amount", etc.

4. Answer ONLY using the retrieved context.

5. Preserve names, dates, phone numbers, addresses,
amounts, percentages and scheme names exactly.

6. If the user's question is unrelated to Ekta Navnirman Trust
or cannot be answered using the retrieved context, politely
explain that you are designed to answer questions only about
Ekta Navnirman Trust and the information available on its
official website.

Do not answer unrelated general knowledge questions.


7. Do not mention document names, source files,
or internal implementation details.

8. Keep answers clear, professional and concise.

------------------------
PREVIOUS CONVERSATION
------------------------

{history}

------------------------
CONTEXT
------------------------

{context}

------------------------
CURRENT QUESTION
------------------------

{question}

ANSWER:
""".strip()


def generate_answer(
    session_id: str,
    question: str,
    top_k: int = 5
) -> dict:
    """
    Complete conversational RAG pipeline.
    """

    total_start = time.time()

    # -----------------------------------
    # Small Talk Handling
    # -----------------------------------

    cleaned_question = question.lower().strip()

    if cleaned_question in SMALL_TALK:

        return {
            "answer": SMALL_TALK[cleaned_question],
            "response_time": round(
                time.time() - total_start,
                2
            )
        }

    # -----------------------------------
    # Conversation History
    # -----------------------------------

    history = get_history(session_id)

    print("\nConversation History")
    print(history)

    # -----------------------------------
    # Query Rewriting
    # -----------------------------------

    rewritten_question = rewrite_question(
        question,
        history
    )

    print("\nOriginal Question:")
    print(question)

    print("\nRewritten Question:")
    print(rewritten_question)

    # -----------------------------------
    # Retrieval
    # -----------------------------------

    retrieval_start = time.time()

    results = retrieve(
        question=rewritten_question,
        top_k=top_k
    )

    retrieval_time = time.time() - retrieval_start

    print(
        f"\nRetrieval time: {retrieval_time:.2f} seconds"
    )

    # -----------------------------------
    # Prompt
    # -----------------------------------

    context = build_context(results)

    history_text = build_chat_history(history)

    prompt = build_prompt(
        question=rewritten_question,
        context=context,
        history=history_text
    )

    # -----------------------------------
    # LLM Generation
    # -----------------------------------

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
        f"LLM generation time: {generation_time:.2f} seconds"
    )

    response.raise_for_status()

    answer = response.json()["response"].strip()

    # -----------------------------------
    # Verify Answer (only when needed)
    # -----------------------------------

    VERIFICATION_KEYWORDS = [
    "maximum",
    "minimum",
    "amount",
    "interest",
    "interest rate",
    "collateral",
    "security",
    "eligible",
    "eligibility",
    "documents",
    "required",
    "fee",
    "deadline",
    "date",
    "phone",
    "contact",
    "email",
    "address",
    "repayment",
    "margin"
    ]

    needs_verification = any(
        keyword in rewritten_question.lower()
        for keyword in VERIFICATION_KEYWORDS
    )

    if needs_verification:

        verification_start = time.time()

        print("\n===== VERIFYING =====")
        print("Question:", rewritten_question)
        print("\nAnswer:")
        print(answer)

        is_supported = verify_answer(
            question=rewritten_question,
            context=context,
            answer=answer
        )

        verification_time = time.time() - verification_start

        print(
            f"Verification time: {verification_time:.2f} seconds"
        )

        print(
            f"Verification: {is_supported}"
        )

        if not is_supported:

            answer = """
I'm sorry, but I couldn't verify this information using the available Ekta Trust knowledge base.

Please try rephrasing your question.

If you still need assistance, you can contact the Ekta Navnirman Trust support team.

📞 +91-7877664078
📧 ektanavnirmantrust@gmail.com
""".strip()

    # -----------------------------------
    # Save Conversation
    # -----------------------------------

    save_message(
        session_id,
        "user",
        question
    )

    save_message(
        session_id,
        "assistant",
        answer
    )

    # -----------------------------------
    # Response
    # -----------------------------------

    total_time = time.time() - total_start

    return {
        "answer": answer,
        "response_time": round(total_time, 2)
    }

if __name__ == "__main__":

    from app.services.memory import create_session

    session = create_session()

    while True:

        question = input("\nYou: ")

        if question.lower() == "exit":
            break

        result = generate_answer(
            session_id=session,
            question=question
        )

        print("\nBot:", result["answer"])

        print(
            f"\nResponse Time: "
            f"{result['response_time']:.2f} sec"
        )