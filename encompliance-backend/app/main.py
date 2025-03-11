from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.models.user import Base

# Create database tables
Base.metadata.create_all(bind=engine)

# Create the app
app = FastAPI(
    title="Encompliance.io API",
    description="Backend API for Encompliance.io compliance platform",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers after creating the app to avoid circular imports
from app.api.routes import chat
from app.api import auth
from app.api.routes import protected
from app.api.routes import users

# Include routers
app.include_router(chat.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(protected.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1/users")

@app.get("/")
async def root():
    return {"message": "Welcome to Encompliance.io API"} 