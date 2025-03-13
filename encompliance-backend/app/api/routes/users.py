from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.database import get_db
from app.models.user import User
from app.schemas.user import User as UserSchema, UserUpdate
from app.auth.dependencies import get_current_active_user, get_current_user
import logging

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Users"])

@router.get("/me", response_model=UserSchema)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get information about the currently authenticated user.
    """
    return current_user

@router.options("/me")
async def options_me():
    """
    Handle OPTIONS requests for the /me endpoint.
    """
    headers = {
        "Access-Control-Allow-Origin": "http://localhost:5173",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Authorization, Content-Type, x-token",
        "Access-Control-Max-Age": "600",
        "Access-Control-Allow-Credentials": "true",
    }
    return JSONResponse(content={}, headers=headers)

@router.get("/user-info")
async def get_user_info(
    request: Request,
    token: Optional[str] = Header(None, alias="x-token"),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Alternative endpoint for getting user info with explicit CORS handling.
    """
    logger.info(f"User info request headers: {request.headers}")
    
    # Extract token
    if not token and authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required",
            headers={
                "Access-Control-Allow-Origin": "http://localhost:5173",
                "Access-Control-Allow-Credentials": "true"
            }
        )
    
    try:
        # Get user using the dependency
        user = await get_current_user(token=token, db=db)
        
        # Create a serializable user dict
        user_dict = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "operation_name": user.operation_name,
            "operation_type": user.operation_type,
            "state": user.state,
            "phone_number": user.phone_number,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "subscription_status": getattr(user, "subscription_status", "active"),
            "subscription_end_date": getattr(user, "subscription_end_date", None),
        }
        
        # Create response with CORS headers
        response = JSONResponse(
            content=user_dict,
            headers={
                "Access-Control-Allow-Origin": "http://localhost:5173",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Authorization, Content-Type, x-token",
                "Access-Control-Allow-Credentials": "true",
            }
        )
        return response
    except Exception as e:
        logger.error(f"Error in user-info endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={
                "Access-Control-Allow-Origin": "http://localhost:5173",
                "Access-Control-Allow-Credentials": "true"
            }
        )

@router.options("/user-info")
async def options_user_info():
    """
    Handle OPTIONS requests for the /user-info endpoint.
    """
    headers = {
        "Access-Control-Allow-Origin": "http://localhost:5173",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Authorization, Content-Type, x-token",
        "Access-Control-Max-Age": "600",
        "Access-Control-Allow-Credentials": "true",
    }
    return JSONResponse(content={}, headers=headers)

@router.get("/auth-debug")
async def auth_debug(
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """
    Debug endpoint to check authentication headers.
    """
    headers = {k: v for k, v in request.headers.items()}
    return {
        "headers": headers,
        "authorization": authorization,
        "message": "This endpoint helps debug authentication issues."
    }

@router.get("/token-test")
async def token_test(
    request: Request,
    authorization: Optional[str] = Header(None),
    token_info: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    Test endpoint to check token parsing.
    """
    headers = {k: v for k, v in request.headers.items()}
    return {
        "headers": headers,
        "authorization": authorization,
        "token_info": "Valid token" if token_info else "Invalid token", 
        "user": token_info,
        "message": "This endpoint helps debug token issues."
    }

@router.put("/me", response_model=UserSchema)
async def update_current_user(
    user_update: UserUpdate, 
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update the current user's information.
    """
    # Update user fields
    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, key, value)
    
    # Save changes
    db.commit()
    db.refresh(current_user)
    
    return current_user 