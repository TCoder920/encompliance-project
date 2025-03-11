from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_service import ai_service

router = APIRouter()


@router.post("", response_model=ChatResponse)
def chat(
    *,
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Chat with the AI assistant
    """
    # Get operation type from user if not provided in request
    operation_type = request.operation_type
    if not operation_type and current_user.operation_type:
        operation_type = current_user.operation_type
    
    # Get response from AI service
    response = ai_service.get_response(
        prompt=request.prompt,
        operation_type=operation_type,
        message_history=request.message_history
    )
    
    return response 