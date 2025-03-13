from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from app.services.llm_service import get_llm_response
from app.services.pdf_service import get_pdf_context
from app.core.config import get_settings
from app.database import get_db
from app.models.query_log import QueryLog
from app.models.pdf import PDF
from app.auth.dependencies import get_current_user
from fastapi.responses import JSONResponse

router = APIRouter(tags=["chat"])

# Add OPTIONS handler for CORS preflight requests
@router.options("/chat")
async def options_chat():
    """
    Handle OPTIONS requests for chat endpoints.
    """
    headers = {
        "Access-Control-Allow-Origin": "http://localhost:5173",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Authorization, Content-Type, x-token",
        "Access-Control-Max-Age": "600",
        "Access-Control-Allow-Credentials": "true",
    }
    return JSONResponse(content={}, headers=headers)

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
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Process a chat request and return a response from the LLM.
    """
    try:
        # Convert message_history to the expected format if needed
        message_history = request.message_history or []
        
        # Get PDF IDs if provided
        pdf_ids = request.pdf_ids or []
        pdf_name = None
        
        # Get first PDF name for logging (if any PDFs are provided)
        if pdf_ids and len(pdf_ids) > 0:
            try:
                pdf = db.query(PDF).filter(PDF.id == pdf_ids[0]).first()
                if pdf:
                    pdf_name = pdf.filename
                    print(f"Using PDF: {pdf_name} (ID: {pdf.id})")
            except Exception as e:
                print(f"Error getting PDF name: {str(e)}")
        
        # Get response from LLM - pass db session for PDF context handling
        response = await get_llm_response(
            prompt=request.prompt,
            operation_type=request.operation_type,
            message_history=message_history,
            pdf_ids=pdf_ids,
            model=request.model,
            db=db  # Pass the database session
        )
        
        # Log the query
        try:
            query_log = QueryLog(
                user_id=current_user.id,
                query_text=request.prompt,
                response_text=response,
                document_name=pdf_name,
                document_id=pdf_ids[0] if pdf_ids and len(pdf_ids) > 0 else None
            )
            db.add(query_log)
            db.commit()
        except Exception as log_err:
            print(f"Error logging query: {str(log_err)}")
            # Continue even if logging fails
        
        return ChatResponse(text=response)
    except Exception as e:
        # Log the error (in a production environment)
        print(f"Error processing chat request: {str(e)}")
        import traceback
        print(traceback.format_exc())
        
        # Return a user-friendly error message
        return ChatResponse(
            text="I apologize, but I encountered an error processing your request. Please try again later.",
            error=str(e)
        ) 