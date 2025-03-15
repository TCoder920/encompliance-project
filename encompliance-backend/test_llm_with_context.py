import os
import sys
import traceback
import json
import asyncio
from app.services.llm_service import get_llm_response
from app.core.config import get_settings

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
        # Read the document context from the debug file
        with open("debug_document_context.txt", "r") as f:
            document_context = f.read()
        
        print(f"Document context length: {len(document_context)}")
        print(f"Document context: {document_context}")
        
        # Construct the prompt
        prompt = "What does the real test.pdf file say?"
        
        # Define the operation type
        operation_type = "chat"
        
        # Construct message history
        message_history = [
            {"role": "system", "content": DEFAULT_SYSTEM_MESSAGE},
            {"role": "system", "content": f"""
            The user has provided the following documents for reference. Use this information to answer their questions:
            
            {document_context}
            
            Remember to cite specific information from these documents when answering questions about them.
            """}
        ]
        
        # Print the messages that will be sent to the LLM
        print("\nMessages to be sent to LLM:")
        for i, msg in enumerate(message_history):
            print(f"Message {i+1}:")
            print(f"  Role: {msg['role']}")
            print(f"  Content: {msg['content'][:100]}..." if len(msg['content']) > 100 else f"  Content: {msg['content']}")
        
        # Get response from LLM
        print("\nGetting response from LLM...")
        response = await get_llm_response(
            prompt=prompt,
            operation_type=operation_type,
            message_history=message_history,
            document_context=document_context,
            stream=False
        )
        
        print("\nLLM Response:")
        print(response)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_llm_with_context()) 