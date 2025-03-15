import os
import sys
import traceback
import json
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.document import Document
from app.services.document_service import get_document_context
from app.core.config import get_settings

settings = get_settings()

async def debug_document_context():
    """
    Debug how document context is being extracted and formatted.
    """
    try:
        # Create a database session
        db = SessionLocal()
        
        # Get the document with ID 16 (real test.pdf)
        doc_id = 16
        document = db.query(Document).filter(Document.id == doc_id).first()
        
        if not document:
            print(f"Document with ID {doc_id} not found in the database")
            return
        
        print(f"Found document: ID={document.id}, Filename={document.filename}, Path={document.filepath}")
        
        # Get document context
        print("\nGetting document context...")
        document_context = await get_document_context([doc_id], db)
        print(f"Document context length: {len(document_context)}")
        print(f"Document context: {document_context}")
        
        # Manually construct a system message with the document context
        document_system_message = f"""
        The user has provided the following documents for reference. Use this information to answer their questions:
        
        {document_context}
        
        Remember to cite specific information from these documents when answering questions about them.
        """
        
        print("\nSystem message with document context:")
        print(document_system_message)
        
        # Save the document context to a file for inspection
        with open("debug_document_context.txt", "w") as f:
            f.write(document_context)
        
        print("\nSaved document context to debug_document_context.txt")
        
        # Now try with both documents (chapter-746-centers.pdf and real test.pdf)
        print("\nGetting context for both documents...")
        both_context = await get_document_context([8, 16], db)
        print(f"Both documents context length: {len(both_context)}")
        
        # Save the combined context to a file for inspection
        with open("debug_both_documents_context.txt", "w") as f:
            f.write(both_context)
        
        print("\nSaved both documents context to debug_both_documents_context.txt")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(debug_document_context()) 