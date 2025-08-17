"""
Prediction schemas
"""

from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime

class PredictionRequest(BaseModel):
    """Schema for prediction request"""
    data: Dict[str, Any]
    model_version: Optional[str] = None

class PredictionResponse(BaseModel):
    """Schema for prediction response"""
    prediction: float
    confidence: Optional[float] = None
    model_version: str
    timestamp: datetime

class BatchPredictionRequest(BaseModel):
    """Schema for batch prediction request"""
    data: List[Dict[str, Any]]
    model_version: Optional[str] = None

class BatchPredictionResponse(BaseModel):
    """Schema for batch prediction response"""
    predictions: List[float]
    confidences: Optional[List[float]] = None
    model_version: str
    timestamp: datetime

class ForecastRequest(BaseModel):
    """Schema for forecast request"""
    horizon_days: int
    start_date: Optional[datetime] = None

class ForecastResponse(BaseModel):
    """Schema for forecast response"""
    forecast_values: List[float]
    forecast_dates: List[datetime]
    confidence_intervals: Optional[List[Dict[str, float]]] = None
    model_version: str

class ModelPredictionConfig(BaseModel):
    """Schema for model prediction configuration"""
    temperature: Optional[float] = 0.1
    max_tokens: Optional[int] = 1000
    top_p: Optional[float] = 0.9
