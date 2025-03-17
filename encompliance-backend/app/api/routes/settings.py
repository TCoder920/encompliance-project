from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from app.database import get_db
from app.auth.dependencies import get_current_user
from fastapi.responses import JSONResponse
import logging
import os
from pydantic import BaseModel
from app.models.user_settings import UserSettings
from app.core.security import encrypt_api_key, decrypt_api_key

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["settings"])

# Define the settings model
class ModelSettings(BaseModel):
    # New unified fields
    api_key: Optional[str] = None
    provider: Optional[str] = "auto"  # 'auto', 'openai', 'anthropic', 'google', 'other'
    other_api_url: Optional[str] = None  # URL for custom API provider
    
    # Legacy fields (kept for backward compatibility)
    local_model_url: Optional[str] = "http://127.0.0.1:1234"
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    custom_model_url: Optional[str] = None
    custom_api_key: Optional[str] = None

# Add OPTIONS handler for CORS preflight requests
@router.options("/settings/model")
async def options_settings():
    """
    Handle OPTIONS requests for settings endpoints.
    """
    headers = {
        "Access-Control-Allow-Origin": "http://localhost:5173",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Authorization, Content-Type, x-token",
        "Access-Control-Max-Age": "600",
        "Access-Control-Allow-Credentials": "true",
    }
    return JSONResponse(content={}, headers=headers)

@router.get("/settings/model")
async def get_model_settings(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get model settings for the current user.
    """
    try:
        # Check if user has settings in the database
        user_settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
        
        if user_settings:
            # Return settings without decrypting API keys (just indicating if they exist)
            settings = {
                "provider": user_settings.provider,
                "other_api_url": user_settings.other_api_url,
                "local_model_url": user_settings.local_model_url,
                
                # For security, only return indicators that keys exist, not the actual keys
                "api_key": "********" if user_settings.encrypted_api_key else "",
                "openai_api_key": "********" if user_settings.encrypted_openai_api_key else "",
                "anthropic_api_key": "********" if user_settings.encrypted_anthropic_api_key else "",
                "custom_api_key": "********" if user_settings.encrypted_custom_api_key else ""
            }
            return settings
        else:
            # Return default settings
            return {
                "api_key": "",
                "provider": "auto",
                "local_model_url": "http://127.0.0.1:1234",
                "openai_api_key": "",
                "anthropic_api_key": "",
                "other_api_url": "",
                "custom_api_key": ""
            }
    except Exception as e:
        logger.error(f"Error getting model settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get model settings"
        )

@router.post("/settings/model")
async def save_model_settings(
    settings: ModelSettings,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Save model settings for the current user.
    """
    try:
        # Check if user already has settings
        user_settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
        
        if not user_settings:
            # Create new settings
            user_settings = UserSettings(user_id=current_user.id)
            db.add(user_settings)
        
        # Update settings with new values
        if settings.provider:
            user_settings.provider = settings.provider
            
        if settings.other_api_url:
            user_settings.other_api_url = settings.other_api_url
            
        if settings.local_model_url:
            user_settings.local_model_url = settings.local_model_url
            
        # Encrypt and save API keys if provided
        if settings.api_key and settings.api_key != "********":
            user_settings.encrypted_api_key = encrypt_api_key(settings.api_key)
            
        if settings.openai_api_key and settings.openai_api_key != "********":
            user_settings.encrypted_openai_api_key = encrypt_api_key(settings.openai_api_key)
            
        if settings.anthropic_api_key and settings.anthropic_api_key != "********":
            user_settings.encrypted_anthropic_api_key = encrypt_api_key(settings.anthropic_api_key)
            
        if settings.custom_api_key and settings.custom_api_key != "********":
            user_settings.encrypted_custom_api_key = encrypt_api_key(settings.custom_api_key)
            
        # Commit changes to database
        db.commit()
            
        # Update environment variables for the current session
        # Handle the unified API key based on provider
        if settings.api_key and settings.api_key != "********":
            from app.services.llm_service import detect_provider
            provider = settings.provider if settings.provider != "auto" else None
            detected_provider = detect_provider(settings.api_key, provider)
            
            # Clear existing API keys first
            if "OPENAI_API_KEY" in os.environ:
                del os.environ["OPENAI_API_KEY"]
            if "ANTHROPIC_API_KEY" in os.environ:
                del os.environ["ANTHROPIC_API_KEY"]
            if "GOOGLE_API_KEY" in os.environ:
                del os.environ["GOOGLE_API_KEY"]
            if "OTHER_API_KEY" in os.environ:
                del os.environ["OTHER_API_KEY"]
            
            # Set the appropriate environment variable based on the detected provider
            if detected_provider == "openai":
                os.environ["OPENAI_API_KEY"] = settings.api_key
            elif detected_provider == "anthropic":
                os.environ["ANTHROPIC_API_KEY"] = settings.api_key
            elif detected_provider == "google":
                os.environ["GOOGLE_API_KEY"] = settings.api_key
            elif detected_provider == "other":
                os.environ["OTHER_API_KEY"] = settings.api_key
                
                # Set the custom API URL if provided
                if settings.other_api_url:
                    os.environ["OTHER_API_URL"] = settings.other_api_url
        
        # Also handle legacy fields for backward compatibility
        if settings.openai_api_key and settings.openai_api_key != "********":
            os.environ["OPENAI_API_KEY"] = settings.openai_api_key
        if settings.anthropic_api_key and settings.anthropic_api_key != "********":
            os.environ["ANTHROPIC_API_KEY"] = settings.anthropic_api_key
            
        # Update local model URL if provided
        if settings.local_model_url:
            os.environ["LOCAL_MODEL_URL"] = settings.local_model_url
            
        return {"message": "Settings saved successfully"}
    except Exception as e:
        logger.error(f"Error saving model settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save model settings"
        ) 