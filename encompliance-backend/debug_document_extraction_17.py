import os
import sys
import traceback
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.document import Document
from app.services.document_service import extract_text_from_pdf, get_document_context
from app.core.config import get_settings

settings = get_settings()

async def debug_document_extraction():
    """
    Debug the document extraction process for a specific document.
    """
    try:
        # Create a database session
        db = SessionLocal()
        
        # Get the document with ID 17 (real test.pdf)
        doc_id = 17
        document = db.query(Document).filter(Document.id == doc_id).first()
        
        if not document:
            print(f"Document with ID {doc_id} not found in the database")
            return
        
        print(f"Found document: ID={document.id}, Filename={document.filename}, Path={document.filepath}")
        
        # Get the full path to the document
        file_path = os.path.join(settings.PDF_STORAGE_PATH, document.filepath)
        print(f"Full file path: {file_path}")
        print(f"File exists: {os.path.exists(file_path)}")
        
        if not os.path.exists(file_path):
            print(f"ERROR: File does not exist at expected path: {file_path}")
            
            # Try to find the file in alternative locations
            alternative_paths = [
                # Try just the filename in case the path is wrong
                os.path.join(settings.PDF_STORAGE_PATH, os.path.basename(document.filepath)),
                
                # Try with the filename directly (no timestamp)
                os.path.join(settings.PDF_STORAGE_PATH, document.filename),
                
                # Try looking in the resources directory
                os.path.join(os.path.dirname(settings.PDF_STORAGE_PATH), "resources", document.filename),
                
                # Try with spaces replaced by underscores
                os.path.join(settings.PDF_STORAGE_PATH, document.filepath.replace(" ", "_")),
                
                # Try with URL encoding for spaces
                os.path.join(settings.PDF_STORAGE_PATH, document.filepath.replace(" ", "%20"))
            ]
            
            for alt_path in alternative_paths:
                print(f"Checking alternative path: {alt_path}")
                if os.path.exists(alt_path):
                    print(f"Found file at alternative path: {alt_path}")
                    file_path = alt_path
                    break
            else:
                print("File not found at any alternative path")
                
                # List all files in the directory
                print(f"Listing all files in {settings.PDF_STORAGE_PATH}:")
                try:
                    all_files = os.listdir(settings.PDF_STORAGE_PATH)
                    for file in all_files:
                        print(f"  - {file}")
                except Exception as e:
                    print(f"Error listing directory: {str(e)}")
                
                return
        
        # Check if the file is a valid PDF
        print("\nChecking if the file is a valid PDF...")
        with open(file_path, 'rb') as f:
            header = f.read(5)
            print(f"File header: {header}")
            if header != b'%PDF-':
                print(f"WARNING: File does not appear to be a valid PDF (header: {header})")
        
        # Extract text from the PDF
        print("\nExtracting text from PDF...")
        text = extract_text_from_pdf(file_path)
        print(f"Extracted {len(text)} characters of text")
        print(f"Text: {text}")
        
        # Now test the get_document_context function
        print("\nTesting get_document_context function...")
        context = await get_document_context([doc_id], db)
        print(f"Document context length: {len(context)}")
        print(f"Document context: {context}")
        
        # Test with both documents (chapter-746-centers.pdf and real test.pdf)
        print("\nTesting with both documents...")
        both_context = await get_document_context([9, 17], db)
        print(f"Both documents context length: {len(both_context)}")
        print(f"Both documents context first 200 chars: {both_context[:200]}")
        print(f"Both documents context last 200 chars: {both_context[-200:]}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(debug_document_extraction()) 