from typing import Any, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.pdf import PDF
from app.models.user import User
from app.schemas.pdf import PDF as PDFSchema
from app.schemas.pdf import PDFCreate, PDFUpdate, PDFUploadResponse
from app.services.s3 import s3_service
from app.utils.deps import get_current_active_user, get_db

router = APIRouter()


@router.post("/upload", response_model=PDFUploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    is_public: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Upload a PDF file
    """
    # Validate file type
    if not file.content_type in ["application/pdf", "application/octet-stream"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed",
        )
    
    # Generate unique object name
    object_name = f"user_{current_user.id}/{file.filename}"
    
    try:
        # Upload file to S3/MinIO
        file_path = await s3_service.upload_file(file, object_name)
        
        # Get file size
        file_content = await file.read()
        file_size = len(file_content)
        
        # Create PDF record in database
        pdf = PDF(
            title=title,
            description=description,
            filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file.content_type,
            category=category,
            is_public=is_public,
            is_processed=False,
            owner_id=current_user.id,
        )
        db.add(pdf)
        db.commit()
        db.refresh(pdf)
        
        return {
            "id": pdf.id,
            "title": pdf.title,
            "filename": pdf.filename,
            "file_size": pdf.file_size,
            "file_type": pdf.file_type,
            "upload_success": True,
            "message": "File uploaded successfully",
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}",
        )


@router.get("/", response_model=List[PDFSchema])
async def get_pdfs(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get all PDFs for the current user
    """
    query = db.query(PDF).filter(PDF.owner_id == current_user.id)
    
    if category:
        query = query.filter(PDF.category == category)
    
    pdfs = query.offset(skip).limit(limit).all()
    return pdfs


@router.get("/public", response_model=List[PDFSchema])
async def get_public_pdfs(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
) -> Any:
    """
    Get all public PDFs
    """
    query = db.query(PDF).filter(PDF.is_public == True)
    
    if category:
        query = query.filter(PDF.category == category)
    
    pdfs = query.offset(skip).limit(limit).all()
    return pdfs


@router.get("/{pdf_id}", response_model=PDFSchema)
async def get_pdf(
    pdf_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific PDF
    """
    pdf = db.query(PDF).filter(PDF.id == pdf_id).first()
    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not found",
        )
    
    # Check if user has access to this PDF
    if pdf.owner_id != current_user.id and not pdf.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return pdf


@router.get("/{pdf_id}/download")
async def download_pdf(
    pdf_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Download a specific PDF
    """
    pdf = db.query(PDF).filter(PDF.id == pdf_id).first()
    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not found",
        )
    
    # Check if user has access to this PDF
    if pdf.owner_id != current_user.id and not pdf.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    try:
        # Download file from S3/MinIO
        content, content_type = await s3_service.download_file(pdf.file_path)
        
        # Return file as response
        from fastapi.responses import Response
        return Response(
            content=content,
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={pdf.filename}",
                "Content-Length": str(len(content)),
            },
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error downloading file: {str(e)}",
        )


@router.put("/{pdf_id}", response_model=PDFSchema)
async def update_pdf(
    pdf_id: int,
    pdf_in: PDFUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a specific PDF
    """
    pdf = db.query(PDF).filter(PDF.id == pdf_id).first()
    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not found",
        )
    
    # Check if user has access to this PDF
    if pdf.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Update PDF
    update_data = pdf_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(pdf, field, value)
    
    db.add(pdf)
    db.commit()
    db.refresh(pdf)
    
    return pdf


@router.delete("/{pdf_id}", response_model=dict)
async def delete_pdf(
    pdf_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a specific PDF
    """
    pdf = db.query(PDF).filter(PDF.id == pdf_id).first()
    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not found",
        )
    
    # Check if user has access to this PDF
    if pdf.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    try:
        # Delete file from S3/MinIO
        await s3_service.delete_file(pdf.file_path)
        
        # Delete PDF from database
        db.delete(pdf)
        db.commit()
        
        return {"success": True, "message": "PDF deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting PDF: {str(e)}",
        )
