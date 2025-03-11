import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.session import Base


class Pdf(Base):
    __tablename__ = "pdfs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    state = Column(String, index=True, nullable=False)
    category = Column(String, index=True, nullable=False)
    operation_type = Column(String, index=True, nullable=True)
    document_type = Column(String, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow) 