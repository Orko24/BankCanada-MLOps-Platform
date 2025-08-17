"""
Bank of Canada Economic Indicator ML Pipeline - Main API Application

This FastAPI application serves as the central hub for:
- Economic data retrieval and processing
- ML model predictions and monitoring
- AI agent interactions for economic research
- Real-time economic indicator tracking
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import logging
import os
from typing import List, Dict, Any, Optional
import asyncio

from .routers import (
    economic_data, 
    predictions, 
    models, 
    monitoring, 
    ai_agents,
    auth
)
from .database import init_db, get_db
from .config import settings
from .utils.logging_config import setup_logging
from .services.economic_data_service import EconomicDataService
from .services.model_service import ModelService
from .middleware.security import SecurityMiddleware


# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Bank of Canada MLOps Platform API...")
    
    # Initialize database
    await init_db()
    
    # Initialize services
    economic_service = EconomicDataService()
    model_service = ModelService()
    
    # Start background tasks
    asyncio.create_task(economic_service.start_data_ingestion())
    
    logger.info("API startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down API...")


# Create FastAPI application
app = FastAPI(
    title="Bank of Canada Economic ML Pipeline",
    description="Enterprise MLOps platform for economic forecasting and policy analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.bankofcanada.ca"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security middleware
app.add_middleware(SecurityMiddleware)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(economic_data.router, prefix="/api/economic-data", tags=["economic-data"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["predictions"])
app.include_router(models.router, prefix="/api/models", tags=["models"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["monitoring"])
app.include_router(ai_agents.router, prefix="/api/ai-agents", tags=["ai-agents"])


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Bank of Canada Economic ML Pipeline API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "economic_data": "/api/economic-data",
            "predictions": "/api/predictions",
            "models": "/api/models",
            "monitoring": "/api/monitoring",
            "ai_agents": "/api/ai-agents"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check database connection
        # Check Redis connection
        # Check MLflow connection
        # Check external APIs
        
        return {
            "status": "healthy",
            "timestamp": "2024-01-15T10:30:00Z",
            "services": {
                "database": "operational",
                "redis": "operational", 
                "mlflow": "operational",
                "bank_canada_api": "operational"
            },
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.get("/api/system/info")
async def system_info():
    """System information for operational dashboards"""
    return {
        "environment": settings.ENVIRONMENT,
        "deployment_id": os.getenv("DEPLOYMENT_ID", "local"),
        "build_version": os.getenv("BUILD_VERSION", "dev"),
        "uptime": "get_uptime()",
        "active_models": "await model_service.get_active_models_count()",
        "daily_predictions": "await get_daily_prediction_count()",
        "system_resources": {
            "cpu_usage": "get_cpu_usage()",
            "memory_usage": "get_memory_usage()",
            "disk_usage": "get_disk_usage()"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False,
        log_level=settings.LOG_LEVEL.lower()
    )
