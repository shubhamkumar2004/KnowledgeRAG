from fastapi import APIRouter

from app.models.chat_models import (
    ChatRequest,
    ChatResponse
)

from app.rag.generator import generate_answer


router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse
)

def chat(request: ChatRequest):

    result = generate_answer(
        session_id=request.session_id,
        question=request.question
    )

    return ChatResponse(
    answer=result["answer"],
    response_time=result["response_time"]
    )