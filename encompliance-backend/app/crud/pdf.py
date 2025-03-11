from typing import Any, Dict, List, Optional, Union

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.pdf import Pdf
from app.schemas.pdf import PdfCreate, PdfUpdate, PdfSearchParams


def get(db: Session, pdf_id: int) -> Optional[Pdf]:
    return db.query(Pdf).filter(Pdf.id == pdf_id).first()


def get_multi(
    db: Session, *, skip: int = 0, limit: int = 100
) -> List[Pdf]:
    return db.query(Pdf).offset(skip).limit(limit).all()


def create(db: Session, *, obj_in: PdfCreate, file_path: str) -> Pdf:
    db_obj = Pdf(
        title=obj_in.title,
        description=obj_in.description,
        filename=obj_in.filename,
        file_path=file_path,
        state=obj_in.state,
        category=obj_in.category,
        operation_type=obj_in.operation_type,
        document_type=obj_in.document_type
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(
    db: Session, *, db_obj: Pdf, obj_in: Union[PdfUpdate, Dict[str, Any]]
) -> Pdf:
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.dict(exclude_unset=True)
    
    for field in update_data:
        if field in update_data and hasattr(db_obj, field):
            setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete(db: Session, *, pdf_id: int) -> Pdf:
    obj = db.query(Pdf).get(pdf_id)
    db.delete(obj)
    db.commit()
    return obj


def search(db: Session, *, params: PdfSearchParams, skip: int = 0, limit: int = 100) -> List[Pdf]:
    query = db.query(Pdf)
    
    # Apply filters
    if params.state:
        query = query.filter(Pdf.state == params.state)
    
    if params.category:
        query = query.filter(Pdf.category == params.category)
    
    if params.operation_type:
        query = query.filter(Pdf.operation_type == params.operation_type)
    
    if params.document_type:
        query = query.filter(Pdf.document_type == params.document_type)
    
    # Apply text search if query provided
    if params.query:
        search_term = f"%{params.query}%"
        query = query.filter(
            or_(
                Pdf.title.ilike(search_term),
                Pdf.description.ilike(search_term)
            )
        )
    
    return query.offset(skip).limit(limit).all() 