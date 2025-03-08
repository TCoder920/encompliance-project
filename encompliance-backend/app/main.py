from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.auth import routes as auth_routes
from app.api.chat import routes as chat_routes
from app.api.pdfs import routes as pdfs_routes
from app.api.payments import routes as payments_routes
from app.api.users import routes as users_routes
from app.core.config import settings
from app.utils.logging import setup_logging

# Setup logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title="Encompliance.io API",
    description="API for Texas daycare and GRO compliance assistant",
    version="0.1.0",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API routers
app.include_router(auth_routes.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(chat_routes.router, prefix=f"{settings.API_V1_STR}/chat", tags=["chat"])
app.include_router(pdfs_routes.router, prefix=f"{settings.API_V1_STR}/pdfs", tags=["pdfs"])
app.include_router(payments_routes.router, prefix=f"{settings.API_V1_STR}/payments", tags=["payments"])
app.include_router(users_routes.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])

# Set up Prometheus monitoring
Instrumentator().instrument(app).expose(app, include_in_schema=False, should_gzip=True)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Encompliance.io API",
        "docs": f"{settings.API_V1_STR}/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
