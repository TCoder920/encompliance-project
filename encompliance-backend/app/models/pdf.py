from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.session import Base


class PDF(Base):
    __tablename__ = "pdfs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)  # S3 key or path
    file_size = Column(Integer, nullable=False)  # Size in bytes
    file_type = Column(String, nullable=False)  # MIME type
    category = Column(String, nullable=True)  # Compliance category
    is_public = Column(Boolean, default=False)
    is_processed = Column(Boolean, default=False)  # Whether AI has processed it
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    owner = relationship("User", back_populates="pdfs")
