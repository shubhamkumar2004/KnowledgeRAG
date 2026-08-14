from uuid import uuid4


# Stores conversations in memory
MEMORY: dict[str, list[dict]] = {}

# Maximum messages to remember
MAX_MESSAGES = 6


def create_session() -> str:
    """
    Create a new chat session.

    Returns:
        session_id
    """

    session_id = str(uuid4())

    MEMORY[session_id] = []

    return session_id


def get_history(session_id: str) -> list[dict]:
    """
    Return conversation history.
    """

    return MEMORY.get(session_id, [])


def save_message(
    session_id: str,
    role: str,
    content: str
):
    """
    Save one chat message.
    """

    if session_id not in MEMORY:
        MEMORY[session_id] = []

    MEMORY[session_id].append(
        {
            "role": role,
            "content": content
        }
    )

    # Keep only the latest messages
    MEMORY[session_id] = MEMORY[session_id][-MAX_MESSAGES:]


def clear_history(session_id: str):
    """
    Clear one conversation.
    """

    MEMORY.pop(session_id, None)

if __name__ == "__main__":

    session = create_session()

    save_message(session, "user", "Hello")
    save_message(session, "assistant", "Hi")
    save_message(session, "user", "Tell me about loans")

    print(get_history(session))