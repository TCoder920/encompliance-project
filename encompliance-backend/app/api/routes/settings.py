from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from app.database import get_db
from app.auth.dependencies import get_current_user
from fastapi.responses import JSONResponse
import logging
import json
import os
from pydantic import BaseModel

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["settings"])

# Define the settings model
class ModelSettings(BaseModel):
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
        # Create settings directory if it doesn't exist
        settings_dir = os.path.join(os.getcwd(), "user_settings")
        os.makedirs(settings_dir, exist_ok=True)
        
        # Path to user's settings file
        settings_file = os.path.join(settings_dir, f"user_{current_user.id}_model_settings.json")
        
        # Check if settings file exists
        if os.path.exists(settings_file):
            with open(settings_file, "r") as f:
                settings = json.load(f)
                
            # Mask API keys for security
            if "openai_api_key" in settings and settings["openai_api_key"]:
                settings["openai_api_key"] = "********"
            if "anthropic_api_key" in settings and settings["anthropic_api_key"]:
                settings["anthropic_api_key"] = "********"
            if "custom_api_key" in settings and settings["custom_api_key"]:
                settings["custom_api_key"] = "********"
                
            return settings
        else:
            # Return default settings
            return {
                "local_model_url": "http://127.0.0.1:1234",
                "openai_api_key": "",
                "anthropic_api_key": "",
                "custom_model_url": "",
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
        # Create settings directory if it doesn't exist
        settings_dir = os.path.join(os.getcwd(), "user_settings")
        os.makedirs(settings_dir, exist_ok=True)
        
        # Path to user's settings file
        settings_file = os.path.join(settings_dir, f"user_{current_user.id}_model_settings.json")
        
        # Save settings to file
        with open(settings_file, "w") as f:
            json.dump(settings.dict(), f)
            
        # Update environment variables for the current session
        if settings.openai_api_key:
            os.environ["OPENAI_API_KEY"] = settings.openai_api_key
        if settings.anthropic_api_key:
            os.environ["ANTHROPIC_API_KEY"] = settings.anthropic_api_key
            
        return {"message": "Settings saved successfully"}
    except Exception as e:
        logger.error(f"Error saving model settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save model settings"
        ) 