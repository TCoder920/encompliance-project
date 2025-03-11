from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class PdfBase(BaseModel):
    title: str
    description: Optional[str] = None
    filename: str
    state: str
    category: str
    operation_type: Optional[str] = None
    document_type: str


class PdfCreate(PdfBase):
    pass


class PdfUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    state: Optional[str] = None
    category: Optional[str] = None
    operation_type: Optional[str] = None
    document_type: Optional[str] = None


class Pdf(PdfBase):
    id: int
    created_at: datetime
    updated_at: datetime
    file_path: str
    
    class Config:
        from_attributes = True


class PdfSearchParams(BaseModel):
    state: Optional[str] = None
    category: Optional[str] = None
    operation_type: Optional[str] = None
    document_type: Optional[str] = None
    query: Optional[str] = None 