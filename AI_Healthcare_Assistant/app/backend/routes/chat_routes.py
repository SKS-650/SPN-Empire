"""
AI Chat API route.
POST /api/v1/chat  — accepts a message + conversation history, returns GPT reply.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.backend.services.chat_service import chat_service

router = APIRouter()


class ChatMessage(BaseModel):
    role: str        # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []
    language: str = "Auto-detect"
    model: str = "gpt-4o"


class ChatResponse(BaseModel):
    reply: str
    model_used: str


@router.post("", response_model=ChatResponse)
@router.post("/", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    """
    Sends a message to the GPT-powered health assistant.
    Falls back to offline keyword matching when the API key is absent.
    """
    if not payload.message or not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    try:
        history_dicts = [{"role": m.role, "content": m.content} for m in payload.history]
        reply = chat_service.chat(
            message=payload.message.strip(),
            history=history_dicts,
            language=payload.language,
            model=payload.model,
        )
        model_used = payload.model if chat_service._client else "offline"
        return ChatResponse(reply=reply, model_used=model_used)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
