from typing import List, Optional
from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    prompt: str
    operation_type: Optional[str] = None
    message_history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    text: str
    error: Optional[str] = None 