from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router
from app.rag.retriever import load_retrieval_system


# --------------------------------------------------
# Application Startup
# --------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Load heavy AI components once when the API starts.

    This prevents the first user request from waiting
    for the embedding model and vector database to load.
    """

    print("\n========================================")
    print("Starting Ekta Trust Chatbot Backend...")
    print("========================================")

    print("\nLoading AI retrieval system...")

    load_retrieval_system()

    print("AI retrieval system loaded successfully.")
    print("Backend is ready to accept requests.\n")

    yield

    print("\nShutting down backend...\n")


# --------------------------------------------------
# FastAPI Application
# --------------------------------------------------

app = FastAPI(
    title="Ekta Trust Chatbot API",
    version="1.0.0",
    description="Backend API for the Ekta Trust RAG Chatbot",
    lifespan=lifespan,
)


# --------------------------------------------------
# CORS Configuration
# Allows the React frontend to communicate
# with this FastAPI backend.
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# API Routes
# --------------------------------------------------

app.include_router(router)


# --------------------------------------------------
# Health Endpoints
# --------------------------------------------------

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