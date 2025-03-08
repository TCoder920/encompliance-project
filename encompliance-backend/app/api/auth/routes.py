from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    CognitoAuth,
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.schemas.token import LoginRequest, Token
from app.schemas.user import UserCreate, UserInDB
from app.utils.deps import get_db

router = APIRouter()


@router.post("/login", response_model=Token)
async def login_access_token(
    db: Session = Depends(get_db), form_data: LoginRequest = None, form: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # Use either form_data or form
    email = form_data.email if form_data else form.username
    password = form_data.password if form_data else form.password
    
    # First try Cognito if enabled
    if settings.USE_COGNITO:
        cognito_user = CognitoAuth.authenticate_user(email, password)
        if cognito_user:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found in database",
                )
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            return {
                "access_token": create_access_token(
                    user.id, expires_delta=access_token_expires
                ),
                "token_type": "bearer",
            }
    
    # Fall back to JWT
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/signup", response_model=Token)
async def signup(user_in: UserCreate, db: Session = Depends(get_db)) -> Any:
    """
    Create new user and return access token
    """
    # Check if user already exists
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create new user
    db_user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        operation_name=user_in.operation_name,
        operation_type=user_in.operation_type,
        state=user_in.state,
        phone_number=user_in.phone_number,
        hashed_password=get_password_hash(user_in.password),
        is_active=True,
        is_superuser=False,
        subscription_status="free",
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            db_user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/refresh-token", response_model=Token)
async def refresh_token(
    db: Session = Depends(get_db), current_user: User = Depends(get_db)
) -> Any:
    """
    Refresh access token
    """
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            current_user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
