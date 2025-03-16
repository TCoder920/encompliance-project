import os
from typing import Optional
# Updated import for Pydantic v2.x
try:
    # Try to import from pydantic-settings (Pydantic v2.x)
    from pydantic_settings import BaseSettings
    PYDANTIC_V2 = True
except ImportError:
    # Fallback for Pydantic v1.x
    from pydantic import BaseSettings
    PYDANTIC_V2 = False
from functools import lru_cache
from dotenv import load_dotenv
from typing import List, Optional

# Load environment variables from .env file
load_dotenv()

# System prompt for all LLM providers
SYSTEM_PROMPT = """
You are an AI assistant integrated into Encompliance.io, a compliance management platform. 
Your role is to provide accurate, concise, and helpful responses related to childcare 
facility compliance, regulatory guidelines, and best practices.

Guidelines:
- Always prioritize compliance-related accuracy.
- Use a neutral and professional tone.
- Do not generate speculative or unverifiable information.
- Reference official regulations when applicable.

Source Citations:
- Whenever providing factual information, include sources.
- If a regulation or law is referenced, specify the law, section, and jurisdiction.
- If an external source is used, provide the link or citation where possible.
- If no source is available, state that the information is based on general compliance knowledge.
"""

class Settings(BaseSettings):
    """Application settings."""
    APP_NAME: str = "Encompliance.io API"
    API_V1_STR: str = "/api/v1"
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_super_secret_key_here")  # Should be set via environment variable
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your_super_secret_key_change_this_in_production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/encompliance")
    
    # CORS settings
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    # PDF storage settings - use folder within backend for simplicity
    PDF_STORAGE_PATH: str = os.getenv(
        "PDF_STORAGE_PATH", 
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "encompliance-documents")
    )
    
    # LLM settings
    USE_LOCAL_MODEL: bool = True  # Use local model by default
    LOCAL_MODEL_URL: str = os.getenv("LOCAL_MODEL_URL", "http://127.0.0.1:1234")
    LOCAL_MODEL_NAME: str = os.getenv("LOCAL_MODEL_NAME", "local-model")
    
    # OpenAI API settings (not currently active, but available for future use)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    DEFAULT_MODEL: str = "local-model"  # Default to local model
    
    if PYDANTIC_V2:
        # Pydantic v2.x uses model_config instead of Config
        model_config = {
            "env_file": ".env",
            "case_sensitive": True,
            "extra": "ignore"  # Allow extra fields as a safety measure
        }
    else:
        # Pydantic v1.x uses Config class
        class Config:
            env_file = ".env"
            case_sensitive = True
            extra = "ignore"  # Allow extra fields as a safety measure

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings."""
    return Settings() 