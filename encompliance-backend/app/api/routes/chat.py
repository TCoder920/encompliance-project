from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from app.services.llm_service import get_llm_response, call_openai_api_streaming, call_local_model_api
from app.services.document_service import get_document_context
from app.core.config import get_settings, SYSTEM_PROMPT
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
    model: Optional[str] = None  # 'local-model' or 'cloud-model'
    pdf_ids: Optional[List[int]] = None  # For backward compatibility
    document_ids: Optional[List[int]] = None
    stream: Optional[bool] = False  # New parameter to enable streaming
    provider: Optional[str] = "auto"  # Provider selection (auto, openai, anthropic, google)

class ChatResponse(BaseModel):
    text: str
    error: Optional[str] = None

class ChatHistoryRequest(BaseModel):
    user_message: str
    ai_response: str
    operation_type: str
    document_ids: Optional[List[int]] = None

class TestConnectionRequest(BaseModel):
    api_key: Optional[str] = None
    provider: Optional[str] = "auto"
    other_api_url: Optional[str] = None
    local_model_url: Optional[str] = None
    is_local: Optional[bool] = False

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
            current_user_id=current_user.id,
            provider=request.provider  # Pass the provider parameter
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
        
        # Create a streaming response with the appropriate API
        async def stream_response():
            collected_response = ""
            try:
                # Use the simplified model selection logic
                stream_generator = await get_llm_response(
                    prompt=request.prompt,
                    operation_type=request.operation_type,
                    message_history=message_history,
                    document_ids=document_ids,
                    model=model,
                    document_context=document_context,
                    current_user_id=current_user.id,
                    stream=True,
                    provider=request.provider
                )
                
                # Now we can iterate over the generator
                async for chunk in stream_generator:
                    collected_response += chunk
                    yield chunk
                
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

@router.post("/chat/test-connection")
async def test_connection(
    request: TestConnectionRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Test the connection to the LLM provider API.
    """
    try:
        from app.services.llm_service import detect_provider
        from app.core.config import SYSTEM_PROMPT
        
        # Check if we're testing a local model
        if request.is_local:
            if not request.local_model_url:
                return {"success": False, "error": "Local model URL is required"}
            
            # Test connection to local LLM
            import httpx
            try:
                # Use the LM Studio OpenAI-compatible chat endpoint with the correct path
                base_url = request.local_model_url
                # Remove trailing slash if present
                if base_url.endswith('/'):
                    base_url = base_url[:-1]
                
                # Check if /v1 is already in the base URL to avoid duplication
                if '/v1' in base_url:
                    endpoint_url = f"{base_url}/chat/completions"
                else:
                    endpoint_url = f"{base_url}/v1/chat/completions"
                
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(
                        endpoint_url,
                        headers={"Content-Type": "application/json"},
                        json={
                            "messages": [
                                {"role": "system", "content": SYSTEM_PROMPT},
                                {"role": "user", "content": "Hello, this is a test message."}
                            ],
                            "max_tokens": 10
                        },
                        timeout=10.0
                    )
                    
                    if response.status_code != 200:
                        return {"success": False, "error": f"Failed to connect to local LLM: {response.text}"}
                    
                    return {"success": True, "provider": "local"}
            except Exception as e:
                return {"success": False, "error": f"Failed to connect to local LLM: {str(e)}"}
        
        # For cloud providers, detect the provider based on the API key
        if not request.api_key:
            return {"success": False, "error": "API key is required for cloud providers"}
            
        provider = request.provider if request.provider != "auto" else None
        detected_provider = detect_provider(request.api_key, provider)
        
        # Set the appropriate environment variable temporarily for testing
        import os
        original_env = {}
        
        # Save original environment variables
        if "OPENAI_API_KEY" in os.environ:
            original_env["OPENAI_API_KEY"] = os.environ["OPENAI_API_KEY"]
        if "ANTHROPIC_API_KEY" in os.environ:
            original_env["ANTHROPIC_API_KEY"] = os.environ["ANTHROPIC_API_KEY"]
        if "GOOGLE_API_KEY" in os.environ:
            original_env["GOOGLE_API_KEY"] = os.environ["GOOGLE_API_KEY"]
        if "OTHER_API_KEY" in os.environ:
            original_env["OTHER_API_KEY"] = os.environ["OTHER_API_KEY"]
        if "OTHER_API_URL" in os.environ:
            original_env["OTHER_API_URL"] = os.environ["OTHER_API_URL"]
        
        try:
            # Set the API key for the detected provider
            if detected_provider == "openai":
                os.environ["OPENAI_API_KEY"] = request.api_key
                # Make a simple test request to the OpenAI API
                import httpx
                async with httpx.AsyncClient(timeout=10.0) as client:
                    # First check if the API key is valid by getting models
                    response = await client.get(
                        "https://api.openai.com/v1/models",
                        headers={
                            "Authorization": f"Bearer {request.api_key}",
                            "Content-Type": "application/json"
                        }
                    )
                    if response.status_code != 200:
                        return {"success": False, "error": f"Failed to connect to OpenAI API: {response.text}"}
                    
                    # Then test a simple chat completion with our system prompt
                    chat_response = await client.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {request.api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "gpt-3.5-turbo",
                            "messages": [
                                {"role": "system", "content": SYSTEM_PROMPT},
                                {"role": "user", "content": "Hello, this is a test message."}
                            ],
                            "max_tokens": 10
                        }
                    )
                    if chat_response.status_code != 200:
                        return {"success": False, "error": f"Failed to test chat completion: {chat_response.text}"}
            elif detected_provider == "anthropic":
                os.environ["ANTHROPIC_API_KEY"] = request.api_key
                # Make a simple test request to the Anthropic API
                import httpx
                async with httpx.AsyncClient(timeout=10.0) as client:
                    # First check if the API key is valid by getting models
                    response = await client.get(
                        "https://api.anthropic.com/v1/models",
                        headers={
                            "x-api-key": request.api_key,
                            "anthropic-version": "2023-06-01",
                            "Content-Type": "application/json"
                        }
                    )
                    if response.status_code != 200:
                        return {"success": False, "error": f"Failed to connect to Anthropic API: {response.text}"}
                    
                    # Then test a simple message with our system prompt
                    chat_response = await client.post(
                        "https://api.anthropic.com/v1/messages",
                        headers={
                            "x-api-key": request.api_key,
                            "anthropic-version": "2023-06-01",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "claude-3-haiku-20240307",
                            "system": SYSTEM_PROMPT,
                            "messages": [
                                {"role": "user", "content": "Hello, this is a test message."}
                            ],
                            "max_tokens": 10
                        }
                    )
                    if chat_response.status_code != 200:
                        return {"success": False, "error": f"Failed to test chat completion: {chat_response.text}"}
            elif detected_provider == "google":
                os.environ["GOOGLE_API_KEY"] = request.api_key
                # Make a simple test request to the Google Gemini API
                import httpx
                async with httpx.AsyncClient(timeout=10.0) as client:
                    # First check if the API key is valid by getting models
                    response = await client.get(
                        "https://generativelanguage.googleapis.com/v1/models?key=" + request.api_key
                    )
                    if response.status_code != 200:
                        return {"success": False, "error": f"Failed to connect to Google Gemini API: {response.text}"}
                    
                    # Then test a simple generation with our system prompt
                    # Gemini doesn't support system messages directly, so we'll prepend it to the user message
                    chat_response = await client.post(
                        "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key=" + request.api_key,
                        headers={
                            "Content-Type": "application/json"
                        },
                        json={
                            "contents": [
                                {
                                    "role": "user",
                                    "parts": [{"text": f"System instructions: {SYSTEM_PROMPT}\n\nUser message: Hello, this is a test message."}]
                                }
                            ],
                            "generationConfig": {
                                "maxOutputTokens": 10
                            }
                        }
                    )
                    if chat_response.status_code != 200:
                        return {"success": False, "error": f"Failed to test chat completion: {chat_response.text}"}
            elif detected_provider == "other":
                # For custom API providers
                if not request.other_api_url:
                    return {"success": False, "error": "Custom API URL is required for 'Other' provider"}
                
                os.environ["OTHER_API_KEY"] = request.api_key
                os.environ["OTHER_API_URL"] = request.other_api_url
                
                # Make a simple test request to the custom API
                import httpx
                
                # Ensure the URL ends with /models for OpenAI compatibility
                api_url = request.other_api_url
                if api_url.endswith("/"):
                    api_url = api_url[:-1]
                
                if not api_url.endswith("/models"):
                    if "/v1" in api_url:
                        api_url = f"{api_url}/models"
                    else:
                        api_url = f"{api_url}/v1/models"
                
                try:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        response = await client.get(
                            api_url,
                            headers={
                                "Authorization": f"Bearer {request.api_key}",
                                "Content-Type": "application/json"
                            }
                        )
                        if response.status_code != 200:
                            # If the models endpoint fails, try a simple chat completion
                            chat_url = api_url.replace("/models", "/chat/completions")
                            chat_response = await client.post(
                                chat_url,
                                headers={
                                    "Authorization": f"Bearer {request.api_key}",
                                    "Content-Type": "application/json"
                                },
                                json={
                                    "messages": [
                                        {"role": "system", "content": SYSTEM_PROMPT},
                                        {"role": "user", "content": "Hello, this is a test message."}
                                    ],
                                    "max_tokens": 10
                                }
                            )
                            if chat_response.status_code != 200:
                                return {"success": False, "error": f"Failed to connect to custom API: {response.text}"}
                except Exception as e:
                    return {"success": False, "error": f"Failed to connect to custom API: {str(e)}"}
            else:
                return {"success": False, "error": f"Unknown provider: {detected_provider}. Please select a provider manually."}
            
            return {"success": True, "provider": detected_provider}
        finally:
            # Restore original environment variables
            for key, value in original_env.items():
                os.environ[key] = value
    except Exception as e:
        print(f"Error testing connection: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return {"success": False, "error": str(e)} 