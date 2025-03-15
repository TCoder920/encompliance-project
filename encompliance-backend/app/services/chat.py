from typing import Union, Optional, List, AsyncGenerator
from datetime import datetime
import traceback
from sqlalchemy.orm import Session
from app.models.chat import Chat, ChatMessage
from app.utils.llm import get_llm_response
from app.services.document_service import get_document_context
from app.config import settings

async def get_chat_response(
    chat_id: int,
    message: str,
    db: Session,
    current_user_id: int,
    stream: bool = False,
    model_name: Optional[str] = None,
    document_ids: Optional[List[int]] = None,
) -> Union[str, AsyncGenerator[str, None]]:
    """
    Get a response from the LLM for a chat message.
    
    Args:
        chat_id: ID of the chat
        message: User message
        db: Database session
        current_user_id: ID of the current user
        stream: Whether to stream the response
        model_name: Name of the model to use
        document_ids: List of document IDs to include in the context
        
    Returns:
        Response from the LLM
    """
    try:
        print(f"Getting chat response for chat_id={chat_id}, user_id={current_user_id}, stream={stream}, model_name={model_name}, document_ids={document_ids}")
        
        # Get chat from database
        chat = db.query(Chat).filter(Chat.id == chat_id).first()
        if not chat:
            error_msg = f"Chat with ID {chat_id} not found"
            print(error_msg)
            return error_msg
        
        # Get chat messages from database
        chat_messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.chat_id == chat_id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )
        
        print(f"Found {len(chat_messages)} existing messages in chat")
        
        # Format messages for the LLM
        messages = []
        
        # Add system message
        system_message = chat.system_message or settings.DEFAULT_SYSTEM_MESSAGE
        messages.append({"role": "system", "content": system_message})
        
        # Add document context if provided
        document_context = ""
        if document_ids:
            print(f"Getting document context for document_ids={document_ids}")
            document_context = await get_document_context(document_ids, db, current_user_id)
            print(f"Document context length: {len(document_context)}")
            
            if document_context:
                # Add document context to system message
                document_system_message = f"""
                The user has provided the following documents for reference. Use this information to answer their questions:
                
                {document_context}
                
                Remember to cite specific information from these documents when answering questions about them.
                """
                messages.append({"role": "system", "content": document_system_message})
                print(f"Added document context to messages (length: {len(document_system_message)})")
            else:
                print("No document context was retrieved")
        
        # Add chat history
        for chat_message in chat_messages:
            role = "assistant" if chat_message.is_bot else "user"
            messages.append({"role": role, "content": chat_message.content})
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        # Print message count and preview
        print(f"Sending {len(messages)} messages to LLM")
        for i, msg in enumerate(messages):
            content_preview = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            print(f"  Message {i+1}: role={msg['role']}, content={content_preview}")
        
        # Get response from LLM
        print(f"Calling LLM with stream={stream}, model_name={model_name}")
        
        # Save user message to database
        user_message = ChatMessage(
            chat_id=chat_id,
            content=message,
            is_bot=False,
            created_at=datetime.now(),
        )
        db.add(user_message)
        db.commit()
        
        # Get response from LLM
        if stream:
            print("Streaming response from LLM")
            
            # Create bot message in database
            bot_message = ChatMessage(
                chat_id=chat_id,
                content="",  # Will be updated as chunks come in
                is_bot=True,
                created_at=datetime.now(),
            )
            db.add(bot_message)
            db.commit()
            
            # Get bot message ID
            bot_message_id = bot_message.id
            print(f"Created bot message with ID {bot_message_id}")
            
            # Define async generator to stream response
            async def stream_response():
                full_response = ""
                
                try:
                    print("Starting to stream response")
                    async for chunk in get_llm_response(messages, stream=True, model_name=model_name):
                        print(f"Received chunk: {chunk[:20]}..." if len(chunk) > 20 else f"Received chunk: {chunk}")
                        full_response += chunk
                        
                        # Update bot message in database
                        db.query(ChatMessage).filter(ChatMessage.id == bot_message_id).update(
                            {"content": full_response}
                        )
                        db.commit()
                        
                        # Yield chunk to client
                        yield chunk
                    
                    print(f"Finished streaming response, total length: {len(full_response)}")
                
                except Exception as e:
                    error_msg = f"Error streaming response: {str(e)}"
                    print(error_msg)
                    print(f"Traceback: {traceback.format_exc()}")
                    
                    # Update bot message with error
                    db.query(ChatMessage).filter(ChatMessage.id == bot_message_id).update(
                        {"content": f"{full_response}\n\n[Error: {error_msg}]"}
                    )
                    db.commit()
                    
                    # Yield error message to client
                    yield f"\n\n[Error: {error_msg}]"
            
            # Return async generator
            return stream_response()
        
        else:
            print("Getting non-streaming response from LLM")
            
            # Get response from LLM
            response = await get_llm_response(messages, stream=False, model_name=model_name)
            print(f"Received response from LLM (length: {len(response)})")
            
            # Save bot message to database
            bot_message = ChatMessage(
                chat_id=chat_id,
                content=response,
                is_bot=True,
                created_at=datetime.now(),
            )
            db.add(bot_message)
            db.commit()
            
            # Return response
            return response
    
    except Exception as e:
        error_msg = f"Error getting chat response: {str(e)}"
        print(error_msg)
        print(f"Traceback: {traceback.format_exc()}")
        
        if stream:
            # For streaming, return an async generator that yields the error message
            async def error_generator():
                yield f"[Error: {error_msg}]"
            
            return error_generator()
        else:
            # For non-streaming, return the error message directly
            return f"[Error: {error_msg}]" 