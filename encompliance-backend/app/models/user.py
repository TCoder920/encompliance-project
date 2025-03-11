import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, index=True)
    operation_name = Column(String)
    operation_type = Column(String, nullable=True)
    state = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    subscription_status = Column(String, default="free")
    subscription_end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Foreign keys
    role_id = Column(Integer, ForeignKey("roles.id"))
    
    # Relationships
    role = relationship("Role", back_populates="users") 