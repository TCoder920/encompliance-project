from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    operation_name: str
    operation_type: Optional[str] = None
    state: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: Optional[bool] = True


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str


# Properties to receive via API on update
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    operation_name: Optional[str] = None
    operation_type: Optional[str] = None
    state: Optional[str] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


# Properties shared by models stored in DB
class UserInDBBase(UserBase):
    id: int
    subscription_status: str
    subscription_end_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Properties to return via API
class User(UserInDBBase):
    pass


# Properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
