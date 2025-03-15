from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import logging
from app.database import engine
from app.models.user import Base
from app.models.document import Document
from app.models.query_log import QueryLog
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
try:
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")
except Exception as e:
    logger.error(f"Error initializing database tables: {str(e)}")

# Custom middleware for debugging
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Log request details
        logger.info(f"Request: {request.method} {request.url.path}")
        logger.info(f"Request headers: {request.headers}")
        
        # Process the request
        response = await call_next(request)
        
        # Log response details
        logger.info(f"Response status: {response.status_code}")
        
        return response

# Create the app
app = FastAPI(
    title="Encompliance.io API",
    description="Backend API for Encompliance.io compliance platform",
    version="0.1.0"
)

# Add debug middleware
app.add_middleware(RequestLoggingMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Allow frontend origins for different environments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Authorization", "Content-Type", "x-token", "Cache-Control", "Pragma", "Expires"],
    expose_headers=["*"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Add global middleware for manual CORS handling
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    # Process the request
    response = await call_next(request)
    
    # Set CORS headers
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, x-token, Cache-Control, Pragma, Expires"
    
    return response

# Import routers after creating the app to avoid circular imports
from app.api.routes import users
from app.api import auth
from app.api.routes import chat
# from app.api.routes import pdfs  # Removed - using documents.py exclusively
from app.api.routes import documents
from app.api.routes import queries
from app.api.routes import settings

# Include routers
app.include_router(users.router, prefix="/api/v1/users")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
# app.include_router(pdfs.router, prefix="/api/v1")  # Removed - using documents.py exclusively
app.include_router(documents.router, prefix="/api/v1")  # Primary document routes
app.include_router(queries.router, prefix="/api/v1")
app.include_router(settings.router, prefix="/api/v1")

# Add a root level router for certain API endpoints that are being called directly with /api/ prefix
app.include_router(queries.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(documents.router, prefix="/api")  # Add documents router to /api prefix
app.include_router(settings.router, prefix="/api")  # Add settings router to /api prefix

# Add routes for the nested path that the frontend is using
app.include_router(chat.router, prefix="/api/v1/api")
app.include_router(queries.router, prefix="/api/v1/api")
app.include_router(documents.router, prefix="/api/v1/api")  # Add documents router to nested path
app.include_router(settings.router, prefix="/api/v1/api")  # Add settings router to nested path

@app.get("/")
async def root():
    return {"message": "Welcome to Encompliance.io API"} 