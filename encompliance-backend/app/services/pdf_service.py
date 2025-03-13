import os
import PyPDF2
from typing import List, Optional, Dict
from app.core.config import get_settings
from app.models.pdf import PDF
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi import Depends

settings = get_settings()

async def get_pdf_context(pdf_ids: List[int], db: Session = Depends(get_db)) -> str:
    """
    Extract text from PDFs and return it as context for the LLM.
    
    Args:
        pdf_ids: List of PDF IDs to extract text from
        db: Database session
        
    Returns:
        Extracted text from the PDFs
    """
    context = []
    
    try:
        # Get PDF records from database
        pdfs = db.query(PDF).filter(PDF.id.in_(pdf_ids), PDF.is_deleted == False).all()
        
        print(f"Found {len(pdfs)} PDF records for IDs: {pdf_ids}")
        
        if not pdfs:
            print(f"WARNING: No PDF records found for IDs: {pdf_ids}")
            # Check what PDFs are available
            all_pdfs = db.query(PDF).all()
            print(f"Available PDFs in database: {len(all_pdfs)}")
            for pdf in all_pdfs:
                print(f"  - ID: {pdf.id}, Filename: {pdf.filename}, Path: {pdf.filepath}, Deleted: {pdf.is_deleted}")
        
        # Check storage directory exists
        storage_dir = settings.PDF_STORAGE_PATH
        if not os.path.exists(storage_dir):
            print(f"Creating PDF storage directory: {storage_dir}")
            os.makedirs(storage_dir, exist_ok=True)
        
        # List all files in the storage directory
        print(f"Files in storage directory {storage_dir}:")
        try:
            storage_files = os.listdir(storage_dir)
            for file in storage_files:
                file_path = os.path.join(storage_dir, file)
                file_size = os.path.getsize(file_path) if os.path.isfile(file_path) else 0
                print(f"  - {file} ({file_size} bytes)")
        except Exception as e:
            print(f"Error listing files in storage directory: {str(e)}")
            
        for pdf in pdfs:
            # Get the full path to the PDF file
            pdf_path = os.path.join(settings.PDF_STORAGE_PATH, pdf.filepath)
            
            print(f"Processing PDF: {pdf.filename}, path: {pdf_path}")
            
            # Check if the file exists
            if not os.path.exists(pdf_path):
                print(f"ERROR: PDF file not found at {pdf_path}")
                
                # Try to find by filename (without timestamp prefix)
                for file in storage_files:
                    if pdf.filename in file:
                        alt_path = os.path.join(storage_dir, file)
                        print(f"Found alternative path by filename: {alt_path}")
                        pdf_path = alt_path
                        break
                
                if not os.path.exists(pdf_path):
                    print(f"PDF file {pdf.filepath} not found in storage directory")
                    context.append(f"[Error: PDF file {pdf.filename} not found]")
                    continue
            
            # Get file size
            file_size = os.path.getsize(pdf_path)
            print(f"PDF file size: {file_size} bytes")
            
            # Extract text from the PDF
            print(f"Extracting text from {pdf_path}")
            pdf_text = extract_text_from_pdf(pdf_path)
            print(f"Extracted {len(pdf_text)} characters of text from {pdf.filename}")
            
            # Add PDF metadata and text to context
            context.append(f"--- Document: {pdf.filename} ---\n{pdf_text}\n")
        
        full_context = "\n".join(context)
        print(f"Returning context of length: {len(full_context)}")
        if len(full_context) == 0:
            print("WARNING: Empty context returned from PDFs!")
            return "No text could be extracted from the requested PDF documents."
        return full_context
    except Exception as e:
        print(f"Error getting PDF context: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return f"[Error: Failed to process PDFs: {str(e)}]"

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text from the PDF
    """
    try:
        text = []
        
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)
            print(f"PDF has {num_pages} pages")
            
            # Extract text from each page
            for page_num in range(num_pages):
                try:
                    page = reader.pages[page_num]
                    page_text = page.extract_text()
                    print(f"Extracted {len(page_text)} characters from page {page_num + 1}")
                    text.append(f"Page {page_num + 1}:\n{page_text}")
                except Exception as page_error:
                    print(f"Error extracting text from page {page_num + 1}: {str(page_error)}")
                    text.append(f"Page {page_num + 1}: [Error: {str(page_error)}]")
        
        combined_text = "\n\n".join(text)
        print(f"Total extracted text: {len(combined_text)} characters")
        return combined_text
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return f"[Error extracting text from {os.path.basename(pdf_path)}: {str(e)}]"

async def list_pdfs(db: Session = Depends(get_db)) -> List[Dict]:
    """
    List all non-deleted PDFs.
    
    Args:
        db: Database session
        
    Returns:
        List of PDF records
    """
    pdfs = db.query(PDF).filter(PDF.is_deleted == False).all()
    
    return [
        {
            "id": pdf.id,
            "filename": pdf.filename,
            "filepath": pdf.filepath,
            "uploaded_at": pdf.uploaded_at,
            "uploaded_by": pdf.uploaded_by
        }
        for pdf in pdfs
    ]

async def get_pdf(pdf_id: int, db: Session = Depends(get_db)) -> Optional[Dict]:
    """
    Get a PDF by ID.
    
    Args:
        pdf_id: ID of the PDF to get
        db: Database session
        
    Returns:
        PDF record or None if not found
    """
    pdf = db.query(PDF).filter(PDF.id == pdf_id, PDF.is_deleted == False).first()
    
    if not pdf:
        return None
    
    return {
        "id": pdf.id,
        "filename": pdf.filename,
        "filepath": pdf.filepath,
        "uploaded_at": pdf.uploaded_at,
        "uploaded_by": pdf.uploaded_by
    } 