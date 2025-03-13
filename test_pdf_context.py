import asyncio
import os
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.pdf import PDF
from app.services.pdf_service import get_pdf_context, extract_text_from_pdf
from app.core.config import get_settings

settings = get_settings()

async def test_pdf_extraction():
    """Test PDF extraction functionality"""
    
    # Create a session
    db = SessionLocal()
    
    try:
        # Get all PDFs from the database
        pdfs = db.query(PDF).filter(PDF.is_deleted == False).all()
        
        if not pdfs:
            print("No PDFs found in the database!")
            return
        
        print(f"Found {len(pdfs)} PDFs in the database")
        for pdf in pdfs:
            print(f"ID: {pdf.id}, Filename: {pdf.filename}, Filepath: {pdf.filepath}")
            
            # Check if file exists
            file_path = os.path.join(settings.PDF_STORAGE_PATH, pdf.filepath)
            if os.path.exists(file_path):
                print(f"✅ File exists at: {file_path}")
                print(f"File size: {os.path.getsize(file_path)} bytes")
                
                # Test direct extraction
                print("\nTesting direct PDF text extraction...")
                text = extract_text_from_pdf(file_path)
                if text and len(text) > 0:
                    print(f"✅ Successfully extracted text directly ({len(text)} characters)")
                    print("Text preview:")
                    print(text[:500] + "..." if len(text) > 500 else text)
                else:
                    print("❌ Failed to extract text directly!")
            else:
                print(f"❌ File does not exist at: {file_path}")
                print(f"PDF storage path: {settings.PDF_STORAGE_PATH}")
                abs_path = os.path.abspath(file_path)
                print(f"Absolute path: {abs_path}")
                
                # Check parent directory
                parent_dir = os.path.dirname(file_path)
                if os.path.exists(parent_dir):
                    print(f"Parent directory exists: {parent_dir}")
                    print(f"Files in parent directory: {os.listdir(parent_dir)}")
                else:
                    print(f"Parent directory does not exist: {parent_dir}")
                
        # Test PDF context extraction for all PDFs
        print("\nTesting PDF context extraction for all PDFs...")
        pdf_ids = [pdf.id for pdf in pdfs]
        context = await get_pdf_context(pdf_ids, db)
        
        if context and len(context) > 0:
            print(f"✅ Successfully extracted context for all PDFs ({len(context)} characters)")
            print("Context preview:")
            print(context[:500] + "..." if len(context) > 500 else context)
        else:
            print("❌ Failed to extract context for all PDFs!")
            
        # Test individual PDF context extraction
        for pdf in pdfs:
            print(f"\nTesting PDF context extraction for PDF ID {pdf.id}...")
            single_context = await get_pdf_context([pdf.id], db)
            
            if single_context and len(single_context) > 0:
                print(f"✅ Successfully extracted context for PDF ID {pdf.id} ({len(single_context)} characters)")
                print("Context preview:")
                print(single_context[:300] + "..." if len(single_context) > 300 else single_context)
            else:
                print(f"❌ Failed to extract context for PDF ID {pdf.id}!")
            
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_pdf_extraction()) 