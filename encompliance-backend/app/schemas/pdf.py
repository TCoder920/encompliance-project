from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# Shared properties
class PDFBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    is_public: Optional[bool] = False


# Properties to receive via API on creation
class PDFCreate(PDFBase):
    pass


# Properties to receive via API on update
class PDFUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    is_public: Optional[bool] = None
    is_processed: Optional[bool] = None


# Properties shared by models stored in DB
class PDFInDBBase(PDFBase):
    id: int
    filename: str
    file_path: str
    file_size: int
    file_type: str
    is_processed: bool
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Properties to return via API
class PDF(PDFInDBBase):
    pass


# Properties stored in DB
class PDFInDB(PDFInDBBase):
    pass


# Properties for file upload response
class PDFUploadResponse(BaseModel):
    id: int
    title: str
    filename: str
    file_size: int
    file_type: str
    upload_success: bool
    message: str
