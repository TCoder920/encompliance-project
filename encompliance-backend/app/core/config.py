import os
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_ALGORITHM: str = "HS256"
    JWT_SECRET_KEY: str = SECRET_KEY
    
    # BACKEND_CORS_ORIGINS is a comma-separated list of origins
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "encompliance"
    POSTGRES_PORT: str = "5432"
    DATABASE_URL: Optional[PostgresDsn] = None

    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )
    
    # AWS
    AWS_ACCESS_KEY_ID: str = "dummy_access_key"
    AWS_SECRET_ACCESS_KEY: str = "dummy_secret_key"
    AWS_REGION: str = "us-east-1"
    
    # S3 Storage
    S3_ENDPOINT: str = "http://localhost:9000"  # For MinIO local development
    S3_BUCKET_NAME: str = "encompliance-pdfs"
    USE_MINIO: bool = True  # Use MinIO for local development, AWS S3 for production
    
    # AWS Cognito
    COGNITO_USER_POOL_ID: Optional[str] = None
    COGNITO_APP_CLIENT_ID: Optional[str] = None
    COGNITO_REGION: str = "us-east-1"
    USE_COGNITO: bool = False
    
    # Stripe
    STRIPE_API_KEY: str = "sk_test_dummy"
    STRIPE_WEBHOOK_SECRET: str = "whsec_dummy"
    STRIPE_PRICE_ID_MONTHLY: str = "price_dummy_monthly"
    STRIPE_PRICE_ID_YEARLY: str = "price_dummy_yearly"
    
    # AI Model
    AI_MODEL_ENDPOINT: str = "http://localhost:8080/generate"
    AI_MODEL_TYPE: str = "llama"  # llama or openai
    AI_MODEL_API_KEY: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
