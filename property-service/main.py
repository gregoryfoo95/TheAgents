from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from contextlib import asynccontextmanager

from config import settings
from database.connection import create_tables
from controllers import property_router, bookings_router

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
    logger.info("Starting Property Service...")
    try:
        await create_tables()
        logger.info("Property Service started successfully")
    except Exception as e:
        logger.error(f"Failed to start Property Service: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Property Service shutting down...")

app = FastAPI(
    title="Property Service",
    description="Property management and booking microservice",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "property-service",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Property Service is running"}

# Routers
app.include_router(property_router)
app.include_router(bookings_router)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        debug=settings.debug
    )