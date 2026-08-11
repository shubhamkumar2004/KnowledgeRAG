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
    request.question
    )

    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"],
        response_time=result["response_time"]
    )