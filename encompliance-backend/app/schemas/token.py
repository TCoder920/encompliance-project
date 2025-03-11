from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None


class TokenPayload(BaseModel):
    sub: str
    exp: int
    role: Optional[str] = None
    
    
class RefreshToken(BaseModel):
    refresh_token: str 