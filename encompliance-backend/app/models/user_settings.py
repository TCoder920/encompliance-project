from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Encrypted API keys
    encrypted_api_key = Column(Text, nullable=True)
    provider = Column(String, default="auto")
    other_api_url = Column(String, nullable=True)
    
    # Legacy fields (kept for backward compatibility)
    encrypted_openai_api_key = Column(Text, nullable=True)
    encrypted_anthropic_api_key = Column(Text, nullable=True)
    encrypted_custom_api_key = Column(Text, nullable=True)
    local_model_url = Column(String, default="http://127.0.0.1:1234")
    
    # Relationship to user
    user = relationship("User", back_populates="settings") 