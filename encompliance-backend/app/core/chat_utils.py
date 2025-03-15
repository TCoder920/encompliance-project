import os
from typing import List, Dict, Any, Optional
from app.services.document_service import get_document_context, extract_text_from_pdf
from app.core.config import get_settings
from sqlalchemy.orm import Session

settings = get_settings()

def get_document_filename_from_path(filepath: str) -> str:
    """Get the original filename from a filepath"""
    return os.path.basename(filepath).split("_", 1)[1] if "_" in os.path.basename(filepath) else os.path.basename(filepath)

async def enhance_system_message_with_document_context(
    system_message: str,
    document_ids: List[int],
    db: Session,
    current_user_id: Optional[int] = None
) -> str:
    """
    Enhance the system message with document content for RAG
    
    Args:
        system_message: The original system message
        document_ids: List of document IDs to extract content from
        db: Database session
        current_user_id: ID of the current user (for document access control)
        
    Returns:
        Enhanced system message with document content
    """
    if not document_ids:
        return system_message
    
    try:
        # Get document context
        document_context = await get_document_context(document_ids, db, current_user_id)
        
        if not document_context:
            print("Warning: No document context retrieved")
            return system_message
        
        # Add document context to system message
        enhanced_message = f"{system_message}\n\n"
        enhanced_message += "Here are the relevant documents for reference:\n\n"
        enhanced_message += document_context
        
        print(f"Enhanced system message with {len(document_context)} characters of document context")
        return enhanced_message
    except Exception as e:
        print(f"Error enhancing system message with document context: {str(e)}")
        import traceback
        print(traceback.format_exc())
        # Return the original message if there's an error
        return system_message

def enhance_system_message_with_pdf_context(
    system_message: str,
    document_context: str
) -> str:
    """
    Enhance the system message with document content (backward compatibility function)
    
    Args:
        system_message: The original system message
        document_context: Document content to include
        
    Returns:
        Enhanced system message with document content
    """
    if not document_context:
        return system_message
    
    # Check if the document context contains any highlighted important documents
    has_important_docs = "⭐⭐⭐ IMPORTANT DOCUMENT ⭐⭐⭐" in document_context
    
    # Add document context to system message
    enhanced_message = f"{system_message}\n\n"
    
    # Add stronger emphasis for important documents
    if has_important_docs:
        enhanced_message += "CRITICAL INSTRUCTION: The user has provided documents for reference. Some documents are marked with ⭐⭐⭐ symbols as IMPORTANT. These IMPORTANT documents contain critical information that you MUST reference and acknowledge in your response.\n\n"
    else:
        enhanced_message += "IMPORTANT: The user has provided the following documents for reference. You MUST use this information to answer their questions.\n\n"
    
    enhanced_message += document_context
    
    enhanced_message += "\n\nYou MUST acknowledge and cite the content from ALL provided documents in your responses, especially those marked as IMPORTANT. If asked about a specific document by name (like 'real test.pdf'), you MUST directly quote its contents in your response. Do not ignore any document, no matter how small."
    
    print(f"Enhanced system message with document context. Total length: {len(enhanced_message)}")
    print(f"Document context preview: {document_context[:500]}...")
    
    if has_important_docs:
        print("Document context contains IMPORTANT highlighted documents")
    
    return enhanced_message

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