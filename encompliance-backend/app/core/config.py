import os
from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # LLM Settings
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings."""
    return Settings() 