from fastapi import FastAPI

from app.api.chat import router   # NEW

app = FastAPI(
    title="Ekta Trust Chatbot API",
    version="1.0.0",
    description="Backend API for the Ekta Trust RAG Chatbot"
)

app.include_router(router)        # NEW


@app.get("/")
def home():
    return {
        "message": "Ekta Trust Chatbot API is running 🚀"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }