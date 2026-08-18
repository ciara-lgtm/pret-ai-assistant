from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.chat import router as chat_router
from app.api.routes.health import router as health_router

# Load .env file from project root (one level up from backend/)
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

app = FastAPI(
    title="Pret AI Assistant",
    version="0.1.0",
    description="Prototype backend foundation for the Pret AI Assistant local testing environment.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(chat_router)


@app.get("/")
def root() -> dict[str, str]:
    """Return a simple API root response for discovery."""
    return {"message": "Pret AI Assistant backend is running."}
