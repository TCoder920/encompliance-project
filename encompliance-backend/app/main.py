from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import logging
from app.database import engine
from app.models.user import Base
from app.models.pdf import PDF

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

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
    allow_headers=["*", "Authorization", "Content-Type", "x-token"],
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
    response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, x-token"
    
    return response

# Import routers after creating the app to avoid circular imports
from app.api.routes import chat
from app.api import auth
from app.api.routes import protected
from app.api.routes import users
from app.api.routes import pdfs

# Include routers
app.include_router(chat.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(protected.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1/users")
app.include_router(pdfs.router, prefix="/api/v1/pdfs")

@app.get("/")
async def root():
    return {"message": "Welcome to Encompliance.io API"} 