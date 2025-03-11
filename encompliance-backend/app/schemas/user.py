from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.schemas.role import Role


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    operation_name: str
    operation_type: Optional[str] = None
    state: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str
    role_id: Optional[int] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    operation_name: Optional[str] = None
    operation_type: Optional[str] = None
    state: Optional[str] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role_id: Optional[int] = None


class UserInDBBase(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    subscription_status: str = "free"
    subscription_end_date: Optional[datetime] = None
    role_id: int

    class Config:
        from_attributes = True


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    hashed_password: str 