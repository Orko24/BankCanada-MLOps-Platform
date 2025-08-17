"""
Economic data API endpoints for Bank of Canada indicators and time series data
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
import logging

from ..database import get_db
from ..models.economic_data_models import EconomicIndicator, EconomicDataPoint, EconomicForecast
from ..schemas.economic_schemas import (
    EconomicIndicatorResponse,
    EconomicDataPointResponse,
    EconomicDataRequest,
    TimeSeriesResponse,
    ForecastResponse
)
from ..services.economic_data_service import EconomicDataService
from ..utils.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/indicators", response_model=List[EconomicIndicatorResponse])
async def get_economic_indicators(
    category: Optional[str] = None,
    is_active: bool = True,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get list of available economic indicators
    
    - **category**: Filter by indicator category (inflation, employment, gdp, etc.)
    - **is_active**: Include only active indicators
    - **skip**: Number of records to skip for pagination
    - **limit**: Maximum number of records to return
    """
    try:
        service = EconomicDataService(db)
        indicators = await service.get_indicators(
            category=category,
            is_active=is_active,
            skip=skip,
            limit=limit
        )
        return indicators
    except Exception as e:
        logger.error(f"Error fetching economic indicators: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch economic indicators")


@router.get("/indicators/{indicator_code}", response_model=EconomicIndicatorResponse)
async def get_indicator_by_code(
    indicator_code: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get detailed information about a specific economic indicator"""
    try:
        service = EconomicDataService(db)
        indicator = await service.get_indicator_by_code(indicator_code)
        if not indicator:
            raise HTTPException(status_code=404, detail="Economic indicator not found")
        return indicator
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching indicator {indicator_code}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch indicator")


@router.get("/indicators/{indicator_code}/data", response_model=TimeSeriesResponse)
async def get_indicator_data(
    indicator_code: str,
    start_date: Optional[datetime] = Query(None, description="Start date for data range"),
    end_date: Optional[datetime] = Query(None, description="End date for data range"),
    frequency: Optional[str] = Query(None, description="Data frequency (daily, weekly, monthly)"),
    quality_threshold: float = Query(0.7, ge=0.0, le=1.0, description="Minimum quality score"),
    include_preliminary: bool = Query(True, description="Include preliminary data points"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get time series data for a specific economic indicator
    
    - **indicator_code**: Code of the economic indicator
    - **start_date**: Start date for data range (defaults to last year)
    - **end_date**: End date for data range (defaults to today)
    - **frequency**: Resample data to specified frequency
    - **quality_threshold**: Filter data points below quality threshold
    - **include_preliminary**: Whether to include preliminary data points
    """
    try:
        service = EconomicDataService(db)
        
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=365)
        
        data = await service.get_indicator_data(
            indicator_code=indicator_code,
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
            quality_threshold=quality_threshold,
            include_preliminary=include_preliminary
        )
        
        return TimeSeriesResponse(
            indicator_code=indicator_code,
            start_date=start_date,
            end_date=end_date,
            data_points=data.get('data_points', []),
            statistics=data.get('statistics', {}),
            metadata=data.get('metadata', {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching data for indicator {indicator_code}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch indicator data")


@router.get("/indicators/{indicator_code}/latest", response_model=EconomicDataPointResponse)
async def get_latest_data_point(
    indicator_code: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get the most recent data point for an economic indicator"""
    try:
        service = EconomicDataService(db)
        latest_point = await service.get_latest_data_point(indicator_code)
        if not latest_point:
            raise HTTPException(status_code=404, detail="No data found for indicator")
        return latest_point
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching latest data for indicator {indicator_code}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch latest data")


@router.get("/indicators/{indicator_code}/forecasts", response_model=List[ForecastResponse])
async def get_indicator_forecasts(
    indicator_code: str,
    horizon_days: Optional[int] = Query(30, ge=1, le=365),
    model_name: Optional[str] = None,
    confidence_level: float = Query(0.95, ge=0.5, le=0.99),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get forecasts for a specific economic indicator
    
    - **indicator_code**: Code of the economic indicator
    - **horizon_days**: Forecast horizon in days
    - **model_name**: Filter by specific model name
    - **confidence_level**: Confidence level for forecast intervals
    """
    try:
        service = EconomicDataService(db)
        forecasts = await service.get_forecasts(
            indicator_code=indicator_code,
            horizon_days=horizon_days,
            model_name=model_name,
            confidence_level=confidence_level
        )
        return forecasts
    except Exception as e:
        logger.error(f"Error fetching forecasts for indicator {indicator_code}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch forecasts")


@router.post("/indicators/{indicator_code}/ingest")
async def trigger_data_ingestion(
    indicator_code: str,
    background_tasks: BackgroundTasks,
    force_refresh: bool = Query(False, description="Force refresh even if data is recent"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Trigger data ingestion for a specific economic indicator
    
    Requires economist or admin role.
    """
    try:
        # Check user permissions
        if not current_user.role.name in ['economist', 'admin']:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        service = EconomicDataService(db)
        
        # Add background task for data ingestion
        background_tasks.add_task(
            service.ingest_indicator_data,
            indicator_code=indicator_code,
            force_refresh=force_refresh,
            user_id=current_user.id
        )
        
        return {
            "message": f"Data ingestion triggered for indicator {indicator_code}",
            "status": "scheduled",
            "indicator_code": indicator_code,
            "force_refresh": force_refresh
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering ingestion for indicator {indicator_code}: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger data ingestion")


@router.get("/dashboard/summary")
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get summary data for economic dashboard
    
    Returns key economic indicators and their latest values
    """
    try:
        service = EconomicDataService(db)
        summary = await service.get_dashboard_summary()
        
        return {
            "timestamp": datetime.utcnow(),
            "key_indicators": summary.get('key_indicators', []),
            "market_overview": summary.get('market_overview', {}),
            "recent_updates": summary.get('recent_updates', []),
            "data_quality": summary.get('data_quality', {}),
            "system_status": summary.get('system_status', {})
        }
        
    except Exception as e:
        logger.error(f"Error fetching dashboard summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard summary")


@router.get("/correlations")
async def get_indicator_correlations(
    indicators: List[str] = Query(..., description="List of indicator codes"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    method: str = Query("pearson", regex="^(pearson|spearman|kendall)$"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Calculate correlations between economic indicators
    
    - **indicators**: List of indicator codes to correlate
    - **start_date**: Start date for correlation analysis
    - **end_date**: End date for correlation analysis  
    - **method**: Correlation method (pearson, spearman, kendall)
    """
    try:
        if len(indicators) < 2:
            raise HTTPException(status_code=400, detail="At least 2 indicators required for correlation")
        
        service = EconomicDataService(db)
        correlations = await service.calculate_correlations(
            indicators=indicators,
            start_date=start_date,
            end_date=end_date,
            method=method
        )
        
        return {
            "indicators": indicators,
            "correlation_matrix": correlations.get('matrix', {}),
            "analysis_period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "method": method,
            "statistics": correlations.get('statistics', {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating correlations: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate correlations")


@router.get("/quality/report")
async def get_data_quality_report(
    indicator_code: Optional[str] = None,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get data quality report for economic indicators
    
    - **indicator_code**: Specific indicator to check (optional)
    - **start_date**: Start date for quality analysis
    - **end_date**: End date for quality analysis
    """
    try:
        service = EconomicDataService(db)
        quality_report = await service.get_data_quality_report(
            indicator_code=indicator_code,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "report_timestamp": datetime.utcnow(),
            "analysis_period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "overall_quality": quality_report.get('overall_quality', {}),
            "indicator_quality": quality_report.get('indicator_quality', {}),
            "quality_issues": quality_report.get('quality_issues', []),
            "recommendations": quality_report.get('recommendations', [])
        }
        
    except Exception as e:
        logger.error(f"Error generating quality report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate quality report")
