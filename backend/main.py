from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import logging
import os
import json
from datetime import datetime
from decimal import Decimal

from utilities.config import get_settings
from utilities.database import create_tables
from utilities.redis import redis_client
from controllers.user_controller import user_router
from controllers.property_controller import property_router
from schemas.base import ErrorResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime and decimal objects."""
    
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


class CustomJSONResponse(JSONResponse):
    """Custom JSON response that handles datetime serialization."""
    
    def render(self, content):
        return json.dumps(
            content,
            cls=CustomJSONEncoder,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Property Marketplace API...")
    
    try:
        # Create database tables
        await create_tables()
        logger.info("Database tables created successfully")
        
        # Test Redis connection
        if await redis_client.ping():
            logger.info("Redis connection established")
        else:
            logger.warning("Redis connection failed")
        
        # Create uploads directory
        os.makedirs("uploads", exist_ok=True)
        logger.info("Upload directory created")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Property Marketplace API...")
    try:
        await redis_client.close()
        logger.info("Redis connection closed")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    debug=settings.debug,
    lifespan=lifespan,
    default_response_class=CustomJSONResponse
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(user_router)
app.include_router(property_router)


# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions with consistent error format."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            detail=exc.detail,
            error_code=f"HTTP_{exc.status_code}"
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            detail="Internal server error",
            error_code="INTERNAL_ERROR"
        ).dict()
    )


# Health check endpoints
@app.get("/", tags=["health"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Property Marketplace API",
        "version": settings.api_version,
        "status": "running"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    try:
        # Check Redis connection
        redis_status = await redis_client.ping()
        
        return {
            "status": "healthy",
            "redis": "connected" if redis_status else "disconnected",
            "version": settings.api_version
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


# API info endpoint
@app.get("/api/info", tags=["api"])
async def api_info():
    """Get API information and available endpoints."""
    return {
        "title": settings.api_title,
        "description": settings.api_description,
        "version": settings.api_version,
        "endpoints": {
            "users": "/api/users",
            "properties": "/api/properties",
            "documentation": "/docs",
            "redoc": "/redoc"
        },
        "features": [
            "User authentication with JWT",
            "Property listings with search and filters",
            "Image upload for properties",
            "Redis caching for performance",
            "Comprehensive validation",
            "Role-based access control"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    ) 