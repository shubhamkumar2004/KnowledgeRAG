import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:3b"


# Questions that are usually follow-ups
FOLLOW_UP_PHRASES = [

    "maximum amount",
    "interest",
    "interest rate",
    "collateral",
    "margin",
    "eligibility",
    "eligible",
    "repayment",
    "documents",
    "fee",
    "dress code",
    "route",
    "distance",
    "winner",
    "theme song",
    "gallery",
    "photos",
    "contact number",
    "phone number",
    "email",
    "address",
    "how much",
    "where is it",
    "when is it"
]


# Standalone pronouns that usually refer
# to the previous conversation
PRONOUNS = {
    "it",
    "they",
    "them",
    "this",
    "that",
    "these",
    "those"
}


def should_rewrite(question: str) -> bool:
    """
    Decide whether the question is likely
    to be a follow-up question.
    """

    question = question.lower().strip()

    # ----------------------------------
    # Check known follow-up phrases
    # ----------------------------------

    for phrase in FOLLOW_UP_PHRASES:

        if phrase in question:
            return True

    # ----------------------------------
    # Check standalone pronouns only
    # ----------------------------------

    cleaned_question = (
        question
        .replace("?", "")
        .replace(".", "")
        .replace(",", "")
        .replace("!", "")
    )

    words = cleaned_question.split()

    for word in words:

        if word in PRONOUNS:
            return True

    return False


def rewrite_question(
    question: str,
    history: list[dict]
) -> str:
    """
    Rewrite ambiguous follow-up questions into
    standalone questions.
    """

    # No conversation yet
    if not history:
        return question

    # Question is already standalone
    if not should_rewrite(question):
        return question

    conversation = []

    for message in history:

        role = (
            "User"
            if message["role"] == "user"
            else "Assistant"
        )

        conversation.append(
            f"{role}: {message['content']}"
        )

    conversation_text = "\n".join(conversation)

    prompt = f"""
You are an AI assistant.

Your ONLY task is to rewrite the latest user question into
a complete standalone question.

Rules:

- Do NOT answer the question.
- Do NOT summarize.
- Do NOT change the meaning.
- Preserve names exactly.
- Return ONLY the rewritten question.

Previous Conversation:

{conversation_text}

Current Question:

{question}

Standalone Question:
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

    rewritten = response.json()["response"].strip()

    print("\nQuery Rewriter Activated")
    print("Original :", question)
    print("Rewritten:", rewritten)

    return rewritten