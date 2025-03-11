import os
import secrets
from typing import List, Union

from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Encompliance.io"
    VERSION: str = "0.1.0"
    
    # Security
    SECRET_KEY: str = os.environ.get("SECRET_KEY", secrets.token_urlsafe(32))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days
    ALGORITHM: str = "HS256"
    
    # CORS
    CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Database
    POSTGRES_SERVER: str = os.environ.get("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.environ.get("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.environ.get("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.environ.get("POSTGRES_DB", "encompliance")
    POSTGRES_PORT: str = os.environ.get("POSTGRES_PORT", "5432")
    SQLALCHEMY_DATABASE_URI: PostgresDsn = None
    
    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: str, values: dict) -> str:
        if isinstance(v, str):
            return v
        
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_SERVER"),
            port=int(values.data.get("POSTGRES_PORT")),
            path=f"{values.data.get('POSTGRES_DB')}"
        )
    
    # Local Storage
    PDF_STORAGE_PATH: str = os.environ.get("PDF_STORAGE_PATH", "storage/pdfs")
    
    # AI Model
    AI_MODEL_PATH: str = os.environ.get("AI_MODEL_PATH", "models/llama-3-8b-instruct.gguf")
    USE_LOCAL_AI: bool = os.environ.get("USE_LOCAL_AI", "true").lower() == "true"


settings = Settings() 