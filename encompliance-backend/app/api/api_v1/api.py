from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, users, pdfs, chat

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(pdfs.router, prefix="/pdfs", tags=["pdfs"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"]) 