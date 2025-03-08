from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.ai_service import ai_service
from app.utils.deps import get_current_active_user, get_db

router = APIRouter()


class ChatMessage(BaseModel):
    role: str  # user or assistant
    content: str


class ChatRequest(BaseModel):
    prompt: str
    operation_type: str  # daycare or gro
    message_history: Optional[List[ChatMessage]] = None


class ChatResponse(BaseModel):
    text: str
    error: Optional[str] = None


@router.post("/", response_model=ChatResponse)
async def get_ai_response(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get a response from the AI model
    """
    # Convert message history to the format expected by the AI service
    message_history = []
    if request.message_history:
        message_history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.message_history
        ]
    
    # Get response from AI service
    response = await ai_service.get_ai_response(
        prompt=request.prompt,
        operation_type=request.operation_type,
        message_history=message_history,
    )
    
    return response


class HealthCheckResponse(BaseModel):
    status: str
    model_type: str


@router.get("/health", response_model=HealthCheckResponse)
async def health_check() -> Any:
    """
    Check if the AI service is healthy
    """
    return {
        "status": "ok",
        "model_type": ai_service.model_type,
    }
