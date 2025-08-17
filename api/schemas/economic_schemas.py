"""
Pydantic schemas for economic data API endpoints
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class EconomicIndicatorResponse(BaseModel):
    """Response schema for economic indicator data"""
    id: int
    code: str
    name: str
    description: Optional[str] = None
    unit: Optional[str] = None
    frequency: Optional[str] = None
    source: Optional[str] = None
    category: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EconomicDataPointResponse(BaseModel):
    """Response schema for economic data points"""
    id: int
    indicator_id: int
    date: datetime
    value: float
    is_forecast: bool = False
    confidence_level: Optional[float] = None
    revision_flag: Optional[str] = None
    quality_flag: Optional[str] = None
    data_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class EconomicDataRequest(BaseModel):
    """Request schema for economic data"""
    indicator_code: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    frequency: Optional[str] = None


class TimeSeriesResponse(BaseModel):
    """Response schema for time series data"""
    indicator: EconomicIndicatorResponse
    data_points: List[EconomicDataPointResponse]
    total_count: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class ForecastResponse(BaseModel):
    """Response schema for forecast data"""
    id: int
    indicator_id: int
    forecast_date: datetime
    forecast_value: float
    confidence_interval_lower: Optional[float] = None
    confidence_interval_upper: Optional[float] = None
    model_version: Optional[str] = None
    confidence_score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True
