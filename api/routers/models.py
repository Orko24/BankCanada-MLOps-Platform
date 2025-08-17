"""
ML Models API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/")
async def get_models():
    """Get list of available models"""
    return {"models": ["economic_forecasting_v1", "inflation_predictor_v2"], "count": 2}

@router.get("/{model_name}")
async def get_model_info(model_name: str):
    """Get information about a specific model"""
    return {"model_name": model_name, "status": "active", "version": "1.0"}
