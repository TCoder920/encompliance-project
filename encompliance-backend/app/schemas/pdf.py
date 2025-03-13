from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PDFBase(BaseModel):
    filename: str
    filepath: str

class PDFCreate(PDFBase):
    pass

class PDFResponse(PDFBase):
    id: int
    uploaded_at: datetime
    uploaded_by: int
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None

    class Config:
        from_attributes = True

class PDFList(BaseModel):
    pdfs: list[PDFResponse] 