import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.pdf import PDF
from app.schemas.pdf import PDFResponse, PDFList
from app.auth.dependencies import get_current_user
from app.models.user import User

router = APIRouter()

DOCUMENTS_DIR = "../../encompliance-documents"
# Ensure the documents directory exists
os.makedirs(DOCUMENTS_DIR, exist_ok=True)

@router.post("/upload", response_model=PDFResponse, status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Save file to the documents directory
    file_path = os.path.join(DOCUMENTS_DIR, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Create PDF record in database
    db_pdf = PDF(
        filename=file.filename,
        filepath=file_path,
        uploaded_by=current_user.id
    )
    
    db.add(db_pdf)
    db.commit()
    db.refresh(db_pdf)
    
    return db_pdf

@router.get("/list", response_model=PDFList)
async def list_pdfs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get all non-deleted PDFs
    pdfs = db.query(PDF).filter(PDF.is_deleted == False).all()
    
    # Ensure chapter-746-centers.pdf is first
    sorted_pdfs = sorted(
        pdfs,
        key=lambda pdf: 0 if pdf.filename == "chapter-746-centers.pdf" else 1
    )
    
    return {"pdfs": sorted_pdfs}

@router.get("/download/{pdf_id}", response_model=PDFResponse)
async def download_pdf(
    pdf_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pdf = db.query(PDF).filter(PDF.id == pdf_id, PDF.is_deleted == False).first()
    
    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not found"
        )
    
    return pdf

@router.delete("/delete/{pdf_id}", response_model=PDFResponse)
async def delete_pdf(
    pdf_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pdf = db.query(PDF).filter(PDF.id == pdf_id, PDF.is_deleted == False).first()
    
    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not found"
        )
    
    # Mark as deleted in database
    pdf.is_deleted = True
    pdf.deleted_at = datetime.now()
    pdf.deleted_by = current_user.id
    
    db.commit()
    db.refresh(pdf)
    
    return pdf 