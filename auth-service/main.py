from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from contextlib import asynccontextmanager

from config import settings
from database.connection import create_tables
# Removed local auth controller - OAuth only
from controllers.auth_controller import oauth_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Auth Service...")
    try:
        await create_tables()
        logger.info("Auth Service started successfully")
    except Exception as e:
        logger.error(f"Failed to start Auth Service: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Auth Service shutting down...")

app = FastAPI(
    title="Auth Service",
    description="Authentication and user management microservice",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
logger.info(f"CORS allowed origins: {settings.allowed_origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth router (OAuth-only implementation)
app.include_router(oauth_router, prefix="/auth")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "auth-service",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Auth Service is running"}

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        debug=settings.debug
    )