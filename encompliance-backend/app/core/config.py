import os
from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv
from typing import List, Optional

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    PROJECT_NAME: str = "Encompliance API"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/encompliance")
    
    # CORS settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",  # Frontend dev server
        "http://localhost:3000",  # Alternative frontend port
        "http://localhost:8080",  # Another common frontend port
    ]
    
    # LLM settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    USE_LOCAL_MODEL: bool = os.getenv("USE_LOCAL_MODEL", "true").lower() == "true"
    LOCAL_MODEL_URL: str = os.getenv("LOCAL_MODEL_URL", "http://localhost:1234/v1")
    LOCAL_MODEL_NAME: str = os.getenv("LOCAL_MODEL_NAME", "local-model")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "local-model")
    
    # PDF storage settings
    PDF_STORAGE_PATH: str = os.getenv("PDF_STORAGE_PATH", os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../encompliance-documents")))
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings."""
    return Settings() 