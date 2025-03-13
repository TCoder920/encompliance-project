from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, Token, User as UserSchema, UserLogin
from app.auth.utils import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.auth.dependencies import get_current_user

router = APIRouter(tags=["Authentication"])

@router.post("/signup", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.
    """
    # Check if email already exists
    db_user_email = db.query(User).filter(User.email == user.email).first()
    if db_user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate username if not provided
    username = user.get_username()
    
    # Check if username already exists
    db_user_username = db.query(User).filter(User.username == username).first()
    if db_user_username:
        # Add numeric suffix to username if it already exists
        base_username = username
        counter = 1
        while db_user_username:
            username = f"{base_username}{counter}"
            db_user_username = db.query(User).filter(User.username == username).first()
            counter += 1
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=username,
        hashed_password=hashed_password,
        full_name=user.full_name,
        operation_name=user.operation_name,
        operation_type=user.operation_type,
        state=user.state,
        phone_number=user.phone_number
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate a user and return a JWT token.
    """
    # Try to find user by username first
    user = db.query(User).filter(User.username == form_data.username).first()
    
    # If not found, try by email
    if not user:
        user = db.query(User).filter(User.email == form_data.username).first()
    
    # If user not found or password doesn't match
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/email-login", response_model=Token)
async def login_with_email(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user with email and password and return a JWT token.
    """
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()
    
    # If user not found or password doesn't match
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/refresh-token", response_model=Token)
async def refresh_access_token(
    authorization: Optional[str] = Header(None),
    token: Optional[str] = Header(None, alias="x-token"),
    db: Session = Depends(get_db)
):
    """
    Refresh an access token if it's valid.
    """
    # Extract token from Authorization header if provided
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No token provided for refresh",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        # Verify the current token is valid by getting the user
        user = await get_current_user(token=token, db=db)
        
        # Create a new access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not refresh token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        ) 