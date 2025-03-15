import os
import sys
import traceback
import json
import asyncio
from app.services.llm_service import get_llm_response
from app.core.config import get_settings
from app.database import SessionLocal
from app.services.document_service import get_document_context

settings = get_settings()

# Default system message
DEFAULT_SYSTEM_MESSAGE = """
You are an AI assistant for Encompliance.io, a platform that helps daycare operators comply with regulations.
Your role is to provide helpful, accurate information about childcare regulations and compliance.
Be concise, professional, and focus on answering the user's questions directly.
"""

async def test_llm_with_context():
    """
    Test the LLM with document context directly.
    """
    try:
        # Create a database session
        db = SessionLocal()
        
        # Get document context for document ID 17
        doc_id = 17
        document_context = await get_document_context([doc_id], db)
        
        print(f"Document context length: {len(document_context)}")
        print(f"Document context: {document_context}")
        
        # Construct the prompt
        prompt = "What does the real test.pdf file say?"
        
        # Define the operation type
        operation_type = "chat"
        
        # Get response from LLM
        print("\nGetting response from LLM...")
        response = await get_llm_response(
            prompt=prompt,
            operation_type=operation_type,
            document_ids=[doc_id],
            document_context=document_context,
            db=db,
            stream=False
        )
        
        print("\nLLM Response:")
        print(response)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_llm_with_context()) 