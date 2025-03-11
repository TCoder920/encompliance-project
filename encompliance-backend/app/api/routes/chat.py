from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
from app.services.llm_service import get_llm_response
from app.core.config import get_settings

router = APIRouter(tags=["chat"])

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    prompt: str
    operation_type: str
    message_history: Optional[List[Dict[str, str]]] = []
    model: Optional[str] = None
    pdf_ids: Optional[List[int]] = None

class ChatResponse(BaseModel):
    text: str
    error: Optional[str] = None

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat request and return a response from the LLM.
    """
    try:
        # Convert message_history to the expected format if needed
        message_history = request.message_history or []
        
        response = await get_llm_response(
            prompt=request.prompt,
            operation_type=request.operation_type,
            message_history=message_history,
            pdf_ids=request.pdf_ids,
            model=request.model
        )
        return ChatResponse(text=response)
    except Exception as e:
        # Log the error (in a production environment)
        print(f"Error processing chat request: {str(e)}")
        # Return a user-friendly error message
        return ChatResponse(
            text="I apologize, but I encountered an error processing your request. Please try again later.",
            error=str(e)
        ) 