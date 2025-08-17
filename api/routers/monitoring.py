"""
Monitoring API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health")
async def get_system_health():
    """Get system health status"""
    return {
        "status": "healthy",
        "services": {
            "database": "operational",
            "redis": "operational",
            "api": "operational"
        }
    }

@router.get("/metrics")
async def get_metrics():
    """Get system metrics"""
    return {"cpu_usage": 25.5, "memory_usage": 60.2, "active_connections": 15}
