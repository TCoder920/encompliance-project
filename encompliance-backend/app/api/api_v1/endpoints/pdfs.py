from typing import Any, List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_current_admin_user, get_db
from app.crud import pdf as pdf_crud
from app.models.user import User
from app.schemas.pdf import Pdf, PdfCreate, PdfSearchParams, PdfUpdate
from app.services.pdf_service import pdf_service

router = APIRouter()


@router.get("/", response_model=List[Pdf])
def read_pdfs(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve all PDFs
    """
    pdfs = pdf_crud.get_multi(db, skip=skip, limit=limit)
    return pdfs


@router.post("/search", response_model=List[Pdf])
def search_pdfs(
    *,
    db: Session = Depends(get_db),
    params: PdfSearchParams,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Search PDFs with filters
    """
    pdfs = pdf_crud.search(db, params=params, skip=skip, limit=limit)
    return pdfs


@router.post("/", response_model=Pdf)
async def create_pdf(
    *,
    db: Session = Depends(get_db),
    title: str = Form(...),
    description: str = Form(None),
    state: str = Form(...),
    category: str = Form(...),
    operation_type: str = Form(None),
    document_type: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Create new PDF (admin only)
    """
    # Validate file is a PDF
    if not file.content_type == "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a PDF"
        )
    
    # Save the file
    file_path = await pdf_service.save_pdf(file, state, category)
    
    # Create PDF record in database
    pdf_in = PdfCreate(
        title=title,
        description=description,
        filename=file.filename,
        state=state,
        category=category,
        operation_type=operation_type,
        document_type=document_type
    )
    pdf = pdf_crud.create(db, obj_in=pdf_in, file_path=file_path)
    
    return pdf


@router.get("/{pdf_id}", response_model=Pdf)
def read_pdf(
    *,
    db: Session = Depends(get_db),
    pdf_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get PDF by ID
    """
    pdf = pdf_crud.get(db, pdf_id=pdf_id)
    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not found"
        )
    return pdf


@router.get("/{pdf_id}/download")
def download_pdf(
    *,
    db: Session = Depends(get_db),
    pdf_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Download PDF file
    """
    pdf = pdf_crud.get(db, pdf_id=pdf_id)
    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not found"
        )
    
    file_path = pdf_service.get_pdf_path(pdf.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF file not found"
        )
    
    return FileResponse(
        path=str(file_path),
        filename=pdf.filename,
        media_type="application/pdf"
    )


@router.put("/{pdf_id}", response_model=Pdf)
def update_pdf(
    *,
    db: Session = Depends(get_db),
    pdf_id: int,
    pdf_in: PdfUpdate,
    current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Update PDF metadata (admin only)
    """
    pdf = pdf_crud.get(db, pdf_id=pdf_id)
    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not found"
        )
    
    pdf = pdf_crud.update(db, db_obj=pdf, obj_in=pdf_in)
    return pdf


@router.delete("/{pdf_id}", response_model=Pdf)
def delete_pdf(
    *,
    db: Session = Depends(get_db),
    pdf_id: int,
    current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Delete PDF (admin only)
    """
    pdf = pdf_crud.get(db, pdf_id=pdf_id)
    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not found"
        )
    
    # Delete the file
    pdf_service.delete_pdf(pdf.file_path)
    
    # Delete the database record
    pdf = pdf_crud.delete(db, pdf_id=pdf_id)
    return pdf 