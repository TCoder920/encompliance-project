from datetime import datetime, timedelta
from typing import Any, Optional, Union

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password
    """
    return pwd_context.hash(password)


# Placeholder for AWS Cognito integration
class CognitoAuth:
    """
    AWS Cognito authentication handler
    This is a placeholder for future implementation
    """
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """
        Verify a Cognito JWT token
        """
        # This would be implemented when integrating with AWS Cognito
        # For now, return None to fall back to JWT authentication
        return None
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[dict]:
        """
        Authenticate a user with Cognito
        """
        # This would be implemented when integrating with AWS Cognito
        # For now, return None to fall back to JWT authentication
        return None
