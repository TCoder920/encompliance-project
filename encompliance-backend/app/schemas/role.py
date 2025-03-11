from enum import Enum
from pydantic import BaseModel


class RoleEnum(str, Enum):
    FREE = "free"
    PREMIUM = "premium"
    ADMIN = "admin"


class RoleBase(BaseModel):
    name: str


class RoleCreate(RoleBase):
    pass


class RoleUpdate(RoleBase):
    pass


class Role(RoleBase):
    id: int
    
    class Config:
        from_attributes = True 