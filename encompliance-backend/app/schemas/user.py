from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    operation_name: str
    state: Optional[str] = None
    phone_number: Optional[str] = None
    operation_type: Optional[str] = None
    username: Optional[str] = None

    def get_username(self) -> str:
        # Use email as username if not provided
        return self.username or self.email.split('@')[0]

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    operation_name: Optional[str] = None
    operation_type: Optional[str] = None
    state: Optional[str] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None

class User(BaseModel):
    id: int
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    operation_name: Optional[str] = None
    operation_type: Optional[str] = None
    state: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    subscription_status: str = "active"  # Default value
    subscription_end_date: Optional[str] = None
    
    class Config:
        orm_mode = True
        from_attributes = True 