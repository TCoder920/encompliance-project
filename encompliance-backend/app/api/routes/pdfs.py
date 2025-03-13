import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models.pdf import PDF
from app.services.pdf_service import list_pdfs, get_pdf
from app.auth.dependencies import get_current_user
from app.core.config import get_settings

router = APIRouter(tags=["pdfs"])
settings = get_settings()

# Add OPTIONS handler for CORS preflight requests
@router.options("/pdfs/list")
@router.options("/pdfs/upload")
@router.options("/pdfs/download/{pdf_id}")
@router.options("/pdfs/delete/{pdf_id}")
async def options_pdfs():
    """
    Handle OPTIONS requests for PDF endpoints.
    """
    headers = {
        "Access-Control-Allow-Origin": "http://localhost:5173",
        "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Authorization, Content-Type, x-token",
        "Access-Control-Max-Age": "600",
        "Access-Control-Allow-Credentials": "true",
    }
    return JSONResponse(content={}, headers=headers)

@router.post("/pdfs/upload", status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Upload a PDF file.
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    try:
        # Create storage directory if it doesn't exist
        os.makedirs(settings.PDF_STORAGE_PATH, exist_ok=True)
        
        # Generate a unique filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(settings.PDF_STORAGE_PATH, unique_filename)
        
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create PDF record in database
        pdf = PDF(
            filename=file.filename,
            filepath=unique_filename,
            uploaded_by=current_user.id
        )
        db.add(pdf)
        db.commit()
        db.refresh(pdf)
        
        return {
            "id": pdf.id,
            "filename": pdf.filename,
            "filepath": unique_filename,
            "uploaded_at": pdf.uploaded_at,
            "uploaded_by": pdf.uploaded_by
        }
    except Exception as e:
        # Log the error
        print(f"Error uploading PDF: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload PDF: {str(e)}"
        )

@router.get("/pdfs/list")
async def get_pdfs(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    List all PDFs.
    """
    try:
        pdfs = await list_pdfs(db)
        return {"pdfs": pdfs}
    except Exception as e:
        # Log the error
        print(f"Error listing PDFs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list PDFs: {str(e)}"
        )

@router.get("/pdfs/download/{pdf_id}")
async def download_pdf(
    pdf_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get a PDF by ID.
    """
    try:
        pdf = await get_pdf(pdf_id, db)
        
        if not pdf:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"PDF with ID {pdf_id} not found"
            )
        
        # Return the PDF data
        return pdf
    except HTTPException:
        raise
    except Exception as e:
        # Log the error
        print(f"Error downloading PDF: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download PDF: {str(e)}"
        )

@router.delete("/pdfs/delete/{pdf_id}")
async def delete_pdf(
    pdf_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Delete a PDF by ID.
    """
    try:
        # Get the PDF
        pdf = db.query(PDF).filter(PDF.id == pdf_id, PDF.is_deleted == False).first()
        
        if not pdf:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"PDF with ID {pdf_id} not found"
            )
        
        # Mark the PDF as deleted
        pdf.is_deleted = True
        pdf.deleted_at = datetime.now()
        pdf.deleted_by = current_user.id
        
        db.commit()
        db.refresh(pdf)
        
        return {
            "id": pdf.id,
            "filename": pdf.filename,
            "filepath": pdf.filepath,
            "uploaded_at": pdf.uploaded_at,
            "uploaded_by": pdf.uploaded_by,
            "is_deleted": pdf.is_deleted,
            "deleted_at": pdf.deleted_at,
            "deleted_by": pdf.deleted_by
        }
    except HTTPException:
        raise
    except Exception as e:
        # Log the error
        print(f"Error deleting PDF: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete PDF: {str(e)}"
        ) 