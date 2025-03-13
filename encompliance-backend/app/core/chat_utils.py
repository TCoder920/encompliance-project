import os
from typing import List, Dict, Any, Optional
from app.services.pdf_service import get_pdf_context, extract_text_from_pdf
from app.core.config import get_settings
from sqlalchemy.orm import Session

settings = get_settings()

def get_pdf_filename_from_path(filepath: str) -> str:
    """Get the original filename from a filepath"""
    return os.path.basename(filepath).split("_", 1)[1] if "_" in os.path.basename(filepath) else os.path.basename(filepath)

async def enhance_system_message_with_pdf_context(
    system_message: str,
    pdf_ids: List[int],
    db: Session
) -> str:
    """
    Enhance the system message with PDF content for RAG
    
    Args:
        system_message: The original system message
        pdf_ids: List of PDF IDs to extract content from
        db: Database session
        
    Returns:
        Enhanced system message with PDF content
    """
    if not pdf_ids:
        return system_message
    
    try:
        # Get PDF context
        pdf_context = await get_pdf_context(pdf_ids, db)
        
        if not pdf_context:
            print("Warning: No PDF context retrieved")
            return system_message
        
        # Add PDF context to system message
        enhanced_message = f"{system_message}\n\n"
        enhanced_message += "Here are the relevant documents for reference:\n\n"
        enhanced_message += pdf_context
        
        print(f"Enhanced system message with {len(pdf_context)} characters of PDF context")
        return enhanced_message
    except Exception as e:
        print(f"Error enhancing system message with PDF context: {str(e)}")
        import traceback
        print(traceback.format_exc())
        # Return the original message if there's an error
        return system_message

def format_chat_history(
    messages: List[Dict[str, str]], 
    system_message: str
) -> List[Dict[str, str]]:
    """
    Format chat history for the LLM
    
    Args:
        messages: List of message dictionaries with 'role' and 'content'
        system_message: System message to include
        
    Returns:
        Formatted list of messages
    """
    formatted_messages = []
    
    # Add system message
    formatted_messages.append({
        "role": "system",
        "content": system_message
    })
    
    # Add conversation history
    for msg in messages:
        if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
            # Ensure role is valid
            role = msg['role'].lower()
            if role not in ['system', 'user', 'assistant']:
                role = 'user' if role == 'human' else 'assistant'
            
            formatted_messages.append({
                "role": role,
                "content": msg['content']
            })
    
    return formatted_messages

def get_compliance_system_message(operation_type: str) -> str:
    """
    Get the system message for compliance assistant
    
    Args:
        operation_type: Type of operation (daycare, residential, etc.)
        
    Returns:
        System message
    """
    return f"""You are a compliance assistant for {operation_type} operations. 
Your job is to provide accurate, helpful information about compliance regulations and requirements.

When answering questions:
1. Be specific about regulatory requirements, including citing specific minimum standards when possible.
2. If you are referencing information from provided documents, be clear about which document you're using.
3. If you don't know the answer or don't have enough information, be honest and say so.
4. Focus on being helpful rather than just technically correct.
5. Provide practical advice on how to comply with regulations when appropriate.

Always consider the context of {operation_type} operations in your responses.""" 