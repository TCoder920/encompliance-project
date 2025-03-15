from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from app.services.llm_service import get_llm_response, call_openai_api_streaming, call_local_model_api
from app.services.document_service import get_document_context
from app.core.config import get_settings
from app.database import get_db
from app.models.query_log import QueryLog
from app.models.document import Document
from app.auth.dependencies import get_current_user
from fastapi.responses import JSONResponse, StreamingResponse
from app.core.chat_utils import enhance_system_message_with_pdf_context, get_compliance_system_message
import traceback
import datetime
from sqlalchemy import func

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
    operation_type: str = "daycare"
    message_history: Optional[List[Dict[str, str]]] = None
    model: Optional[str] = None
    pdf_ids: Optional[List[int]] = None  # For backward compatibility
    document_ids: Optional[List[int]] = None
    stream: Optional[bool] = False  # New parameter to enable streaming

class ChatResponse(BaseModel):
    text: str
    error: Optional[str] = None

class ChatHistoryRequest(BaseModel):
    user_message: str
    ai_response: str
    operation_type: str
    document_ids: Optional[List[int]] = None

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Process a chat request and return a response from the LLM.
    If streaming is requested, returns a StreamingResponse.
    """
    # If streaming is requested, redirect to the streaming endpoint
    if request.stream:
        return await stream_chat(request, db, current_user)
        
    try:
        # Convert message_history to the expected format if needed
        message_history = request.message_history or []
        
        # Get document IDs if provided (use pdf_ids for backward compatibility)
        document_ids = request.document_ids or request.pdf_ids or []
        document_name = None
        document_context = None
        
        # Print debug information
        print(f"Chat request: prompt={request.prompt[:50]}..., operation_type={request.operation_type}, model={request.model}")
        print(f"Document IDs: {document_ids}")
        print(f"User ID: {current_user.id}")
        
        # Get first document name for logging (if any documents are provided)
        if document_ids and len(document_ids) > 0:
            try:
                # Print all documents for debugging
                print("Available documents:")
                print(f"- User documents ({len(db.query(Document).filter(Document.uploaded_by == current_user.id).all())}):")
                for doc in db.query(Document).filter(Document.uploaded_by == current_user.id).all():
                    print(f"  ID: {doc.id}, Filename: {doc.filename}, Path: {doc.filepath}")
                
                print(f"- All documents ({len(db.query(Document).all())}):")
                for doc in db.query(Document).all():
                    print(f"  ID: {doc.id}, Filename: {doc.filename}, Path: {doc.filepath}")
                
                print(f"- Active PDF IDs that will be sent to API: ")
                for doc_id in document_ids:
                    doc = db.query(Document).filter(Document.id == doc_id).first()
                    if doc:
                        print(f"{doc.id}, ", end="")
                    else:
                        print(f"Document with ID {doc_id} not found")
                print()
                
                document = db.query(Document).filter(Document.id == document_ids[0]).first()
                if document:
                    document_name = document.filename
                    print(f"Using document: {document_name} (ID: {document.id})")
            except Exception as e:
                print(f"Error getting document info: {str(e)}")
                print(f"Traceback: {traceback.format_exc()}")
        
        # Get document context if document_ids provided
        if document_ids:
            try:
                document_context = await get_document_context(document_ids, db, current_user.id)
                print(f"Retrieved {len(document_context)} characters of context from {len(document_ids)} documents")
                
                # Trim context if it's too long (to avoid token limits)
                max_context_length = 50000  # Adjust based on model's context window
                if len(document_context) > max_context_length:
                    print(f"Trimming context from {len(document_context)} to {max_context_length} characters")
                    document_context = document_context[:max_context_length] + "\n[Context truncated due to length]"
            except Exception as e:
                print(f"Error getting document context: {str(e)}")
                print(f"Traceback: {traceback.format_exc()}")
                document_context = f"[Error retrieving document context: {str(e)}]"
        
        # Get response from LLM
        response_text = await get_llm_response(
            prompt=request.prompt,
            operation_type=request.operation_type,
            message_history=message_history,
            document_ids=document_ids,
            model=request.model,
            document_context=document_context,  # Pass the document context explicitly
            db=db,
            current_user_id=current_user.id
        )
        
        # Log the query
        try:
            # Check if this is a duplicate query (same user, same prompt, within last minute)
            recent_time = func.now() - datetime.timedelta(minutes=1)
            existing_log = db.query(QueryLog).filter(
                QueryLog.user_id == current_user.id,
                QueryLog.query == request.prompt,
                QueryLog.created_at > recent_time
            ).first()
            
            if existing_log:
                print(f"Duplicate query detected, skipping log creation. Existing log ID: {existing_log.id}")
            else:
                # Generate a unique conversation ID if not provided
                conversation_id = None
                if message_history and len(message_history) > 0:
                    # If this is part of an existing conversation, try to get the conversation_id
                    # from the most recent query log with the same context
                    recent_log = db.query(QueryLog).filter(
                        QueryLog.user_id == current_user.id,
                        QueryLog.document_reference == document_name
                    ).order_by(QueryLog.created_at.desc()).first()
                    
                    if recent_log and recent_log.conversation_id:
                        conversation_id = recent_log.conversation_id
                    else:
                        # Generate a new conversation ID based on timestamp
                        conversation_id = int(datetime.datetime.now().timestamp())
                
                query_log = QueryLog(
                    user_id=current_user.id,
                    query=request.prompt,
                    response=response_text,
                    operation_type=request.operation_type,
                    document_reference=document_name,
                    document_id=document_ids[0] if document_ids and len(document_ids) > 0 else None,
                    conversation_id=conversation_id
                )
                db.add(query_log)
                db.commit()
                print(f"Query log created with ID: {query_log.id}, conversation_id: {conversation_id}")
        except Exception as log_error:
            print(f"Error logging query: {str(log_error)}")
            # Continue even if logging fails
        
        return {"text": response_text}
    except Exception as e:
        print(f"Error processing chat request: {str(e)}")
        print(traceback.format_exc())
        return {"text": "", "error": str(e)}

@router.post("/chat/stream", response_class=StreamingResponse)
async def stream_chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Process a chat request and return a streaming response from the LLM.
    This endpoint streams the response as it's generated by the model.
    """
    try:
        # Convert message_history to the expected format if needed
        message_history = request.message_history or []
        
        # Get document IDs if provided (use pdf_ids for backward compatibility)
        document_ids = request.document_ids or request.pdf_ids or []
        document_name = None
        document_context = None
        
        # Get first document name for logging (if any documents are provided)
        if document_ids and len(document_ids) > 0:
            try:
                document = db.query(Document).filter(Document.id == document_ids[0]).first()
                if document:
                    document_name = document.filename
                    print(f"Using document: {document_name} (ID: {document.id})")
            except Exception as e:
                print(f"Error getting document info: {str(e)}")
        
        # Get document context if document_ids provided
        if document_ids:
            try:
                document_context = await get_document_context(document_ids, db, current_user.id)
                print(f"Retrieved {len(document_context)} characters of context from {len(document_ids)} documents")
                
                # Trim context if it's too long (to avoid token limits)
                max_context_length = 50000  # Adjust based on model's context window
                if len(document_context) > max_context_length:
                    print(f"Trimming context from {len(document_context)} to {max_context_length} characters")
                    document_context = document_context[:max_context_length] + "\n[Context truncated due to length]"
            except Exception as e:
                print(f"Error getting document context: {str(e)}")
                document_context = f"[Error retrieving document context: {str(e)}]"
        
        # Get system message
        system_message = get_compliance_system_message(request.operation_type)
        
        # Enhance system message with document context if available
        if document_context:
            system_message = enhance_system_message_with_pdf_context(system_message, document_context)
        
        # Prepare messages for the API call - start with system message
        messages = [
            {"role": "system", "content": system_message}
        ]
        
        # Add any message history (if provided)
        if message_history:
            # Process each message to ensure it has the correct format
            for msg in message_history:
                if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                    # Ensure role is valid
                    role = msg['role'].lower()
                    if role not in ['system', 'user', 'assistant']:
                        role = 'user' if role == 'human' else 'assistant'
                    
                    messages.append({
                        "role": role,
                        "content": msg['content']
                    })
        
        # Add the current prompt
        messages.append({"role": "user", "content": request.prompt})
        
        # Select model - prefer the request model, fallback to default
        model = request.model or get_settings().DEFAULT_MODEL
        settings = get_settings()
        
        # Create a streaming response with the OpenAI API
        async def stream_response():
            collected_response = ""
            try:
                # Check if we should use OpenAI or local model
                if model.startswith("gpt-"):
                    # Use OpenAI streaming
                    async for chunk in call_openai_api_streaming(messages, model):
                        collected_response += chunk
                        yield chunk
                elif model == "local-model" or settings.USE_LOCAL_MODEL:
                    # Use local model streaming
                    # Important: We need to await the function to get the async generator
                    stream_generator = await get_llm_response(
                        prompt=request.prompt,
                        operation_type=request.operation_type,
                        message_history=message_history,
                        document_ids=document_ids,
                        model=model,
                        document_context=document_context,
                        current_user_id=current_user.id,
                        stream=True
                    )
                    # Now we can iterate over the generator
                    async for chunk in stream_generator:
                        collected_response += chunk
                        yield chunk
                else:
                    # Fallback for unknown models - non-streaming response
                    result = await get_llm_response(
                        prompt=request.prompt,
                        operation_type=request.operation_type,
                        message_history=message_history,
                        document_ids=document_ids,
                        model=model,
                        document_context=document_context,
                        current_user_id=current_user.id
                    )
                    collected_response = result
                    yield result
                
                # Log the query after completion
                try:
                    # Check if this is a duplicate query (same user, same prompt, within last minute)
                    recent_time = func.now() - datetime.timedelta(minutes=1)
                    existing_log = db.query(QueryLog).filter(
                        QueryLog.user_id == current_user.id,
                        QueryLog.query == request.prompt,
                        QueryLog.created_at > recent_time
                    ).first()
                    
                    if existing_log:
                        print(f"Duplicate streaming query detected, skipping log creation. Existing log ID: {existing_log.id}")
                    else:
                        # Generate a unique conversation ID if not provided
                        conversation_id = None
                        if message_history and len(message_history) > 0:
                            # If this is part of an existing conversation, try to get the conversation_id
                            # from the most recent query log with the same context
                            recent_log = db.query(QueryLog).filter(
                                QueryLog.user_id == current_user.id,
                                QueryLog.document_reference == document_name
                            ).order_by(QueryLog.created_at.desc()).first()
                            
                            if recent_log and recent_log.conversation_id:
                                conversation_id = recent_log.conversation_id
                            else:
                                # Generate a new conversation ID based on timestamp
                                conversation_id = int(datetime.datetime.now().timestamp())
                        
                        query_log = QueryLog(
                            user_id=current_user.id,
                            query=request.prompt,
                            response=collected_response,
                            operation_type=request.operation_type,
                            document_reference=document_name,
                            document_id=document_ids[0] if document_ids and len(document_ids) > 0 else None,
                            conversation_id=conversation_id
                        )
                        db.add(query_log)
                        db.commit()
                        print(f"Streaming query log created with ID: {query_log.id}, conversation_id: {conversation_id}")
                except Exception as log_error:
                    print(f"Error logging query: {str(log_error)}")
            except Exception as e:
                print(f"Error in streaming response: {str(e)}")
                print(f"Traceback: {traceback.format_exc()}")
                yield f"Error: {str(e)}"
        
        return StreamingResponse(
            stream_response(),
            media_type="text/plain"
        )
        
    except Exception as e:
        print(f"Error in stream_chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")

@router.post("/chat/history")
async def save_chat_history(
    request: ChatHistoryRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Save chat history to the database
    """
    try:
        # Get document name for reference (if any documents are provided)
        document_name = None
        document_id = None
        if request.document_ids and len(request.document_ids) > 0:
            try:
                document = db.query(Document).filter(Document.id == request.document_ids[0]).first()
                if document:
                    document_name = document.filename
                    document_id = document.id
            except Exception as e:
                print(f"Error getting document info: {str(e)}")
        
        # Check if this is a duplicate query (same user, same prompt, within last minute)
        recent_time = func.now() - datetime.timedelta(minutes=1)
        existing_log = db.query(QueryLog).filter(
            QueryLog.user_id == current_user.id,
            QueryLog.query == request.user_message,
            QueryLog.created_at > recent_time
        ).first()
        
        if existing_log:
            print(f"Duplicate chat history detected, skipping log creation. Existing log ID: {existing_log.id}")
            return {"success": True, "message": "Chat history already exists"}
        
        # Generate a unique conversation ID if not provided
        # Try to find the most recent conversation with the same document
        conversation_id = None
        recent_log = db.query(QueryLog).filter(
            QueryLog.user_id == current_user.id,
            QueryLog.document_reference == document_name
        ).order_by(QueryLog.created_at.desc()).first()
        
        if recent_log and recent_log.conversation_id:
            # Check if the recent log is from the last hour (likely the same conversation)
            recent_time = datetime.datetime.now() - datetime.timedelta(hours=1)
            if recent_log.created_at > recent_time:
                conversation_id = recent_log.conversation_id
        
        # If no conversation ID found, generate a new one based on timestamp
        if not conversation_id:
            conversation_id = int(datetime.datetime.now().timestamp())
        
        # Log the query
        query_log = QueryLog(
            user_id=current_user.id,
            query=request.user_message,
            response=request.ai_response,
            operation_type=request.operation_type,
            document_reference=document_name,
            document_id=document_id,
            conversation_id=conversation_id
        )
        db.add(query_log)
        db.commit()
        
        return {"success": True, "message": "Chat history saved successfully", "conversation_id": conversation_id}
    except Exception as e:
        print(f"Error saving chat history: {str(e)}")
        return {"success": False, "error": str(e)} 