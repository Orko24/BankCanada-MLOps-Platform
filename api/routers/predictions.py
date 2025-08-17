"""
ML prediction and forecasting API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
import logging
import json

from ..database import get_db
from ..schemas.prediction_schemas import (
    PredictionRequest,
    PredictionResponse,
    BatchPredictionRequest,
    BatchPredictionResponse,
    ForecastRequest,
    ForecastResponse,
    ModelPredictionConfig
)
from ..services.prediction_service import PredictionService
from ..services.model_service import ModelService
from ..utils.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/predict/{model_name}", response_model=PredictionResponse)
async def make_prediction(
    model_name: str,
    request: PredictionRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Make a single prediction using a deployed model
    
    - **model_name**: Name of the deployed model
    - **request**: Prediction request with input features
    """
    try:
        prediction_service = PredictionService(db)
        model_service = ModelService(db)
        
        # Validate model exists and is deployed
        model = await model_service.get_model_by_name(model_name)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Check if model is in production
        if model.status != "production":
            raise HTTPException(status_code=400, detail="Model is not in production")
        
        # Make prediction
        result = await prediction_service.predict(
            model_name=model_name,
            input_data=request.input_data,
            model_version=request.model_version,
            include_confidence=request.include_confidence,
            include_explanations=request.include_explanations
        )
        
        return PredictionResponse(
            model_name=model_name,
            model_version=result.get('model_version'),
            prediction=result.get('prediction'),
            confidence_score=result.get('confidence_score'),
            prediction_interval=result.get('prediction_interval'),
            feature_importance=result.get('feature_importance'),
            explanations=result.get('explanations'),
            metadata=result.get('metadata', {}),
            prediction_id=result.get('prediction_id'),
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error making prediction with model {model_name}: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed")


@router.post("/predict/{model_name}/batch", response_model=BatchPredictionResponse)
async def make_batch_predictions(
    model_name: str,
    request: BatchPredictionRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Make batch predictions for multiple inputs
    
    - **model_name**: Name of the deployed model
    - **request**: Batch prediction request with multiple inputs
    """
    try:
        prediction_service = PredictionService(db)
        model_service = ModelService(db)
        
        # Validate model
        model = await model_service.get_model_by_name(model_name)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Validate batch size
        if len(request.input_data_batch) > 1000:
            raise HTTPException(status_code=400, detail="Batch size too large (max 1000)")
        
        # For small batches, process synchronously
        if len(request.input_data_batch) <= 100:
            results = await prediction_service.batch_predict(
                model_name=model_name,
                input_data_batch=request.input_data_batch,
                model_version=request.model_version,
                include_confidence=request.include_confidence
            )
            
            return BatchPredictionResponse(
                model_name=model_name,
                batch_id=results.get('batch_id'),
                status="completed",
                predictions=results.get('predictions', []),
                total_predictions=len(results.get('predictions', [])),
                successful_predictions=results.get('successful_count', 0),
                failed_predictions=results.get('failed_count', 0),
                timestamp=datetime.utcnow(),
                processing_time_seconds=results.get('processing_time')
            )
        
        # For large batches, process asynchronously
        else:
            batch_id = await prediction_service.submit_batch_job(
                model_name=model_name,
                input_data_batch=request.input_data_batch,
                model_version=request.model_version,
                user_id=current_user.id
            )
            
            # Add background task
            background_tasks.add_task(
                prediction_service.process_batch_job,
                batch_id=batch_id
            )
            
            return BatchPredictionResponse(
                model_name=model_name,
                batch_id=batch_id,
                status="processing",
                message="Batch job submitted for processing",
                total_predictions=len(request.input_data_batch),
                timestamp=datetime.utcnow()
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error making batch predictions: {e}")
        raise HTTPException(status_code=500, detail="Batch prediction failed")


@router.get("/batch/{batch_id}/status")
async def get_batch_status(
    batch_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get status of a batch prediction job"""
    try:
        prediction_service = PredictionService(db)
        status = await prediction_service.get_batch_status(batch_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Batch job not found")
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching batch status {batch_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch batch status")


@router.post("/forecast/{indicator_code}", response_model=ForecastResponse)
async def generate_forecast(
    indicator_code: str,
    request: ForecastRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Generate economic forecast for a specific indicator
    
    - **indicator_code**: Economic indicator to forecast
    - **request**: Forecast configuration and parameters
    """
    try:
        prediction_service = PredictionService(db)
        
        # Generate forecast
        forecast = await prediction_service.generate_forecast(
            indicator_code=indicator_code,
            horizon_days=request.horizon_days,
            confidence_level=request.confidence_level,
            model_name=request.model_name,
            scenario=request.scenario,
            external_factors=request.external_factors
        )
        
        return ForecastResponse(
            indicator_code=indicator_code,
            forecast_date=datetime.utcnow(),
            horizon_days=request.horizon_days,
            forecasts=forecast.get('forecasts', []),
            confidence_intervals=forecast.get('confidence_intervals', []),
            model_info=forecast.get('model_info', {}),
            scenario_analysis=forecast.get('scenario_analysis', {}),
            forecast_quality=forecast.get('quality_metrics', {}),
            metadata=forecast.get('metadata', {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating forecast for {indicator_code}: {e}")
        raise HTTPException(status_code=500, detail="Forecast generation failed")


@router.get("/forecasts/recent")
async def get_recent_forecasts(
    indicator_codes: Optional[List[str]] = Query(None),
    days_back: int = Query(7, ge=1, le=30),
    model_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get recent forecasts for economic indicators
    
    - **indicator_codes**: List of indicator codes (optional)
    - **days_back**: Number of days to look back
    - **model_name**: Filter by specific model
    """
    try:
        prediction_service = PredictionService(db)
        forecasts = await prediction_service.get_recent_forecasts(
            indicator_codes=indicator_codes,
            days_back=days_back,
            model_name=model_name
        )
        
        return {
            "forecasts": forecasts,
            "total_forecasts": len(forecasts),
            "date_range": {
                "start_date": datetime.utcnow() - timedelta(days=days_back),
                "end_date": datetime.utcnow()
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching recent forecasts: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch recent forecasts")


@router.post("/models/{model_name}/scenario")
async def run_scenario_analysis(
    model_name: str,
    scenarios: Dict[str, Any],
    base_date: Optional[datetime] = None,
    horizon_days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Run scenario analysis using economic models
    
    - **model_name**: Name of the model to use
    - **scenarios**: Dictionary of scenario configurations
    - **base_date**: Base date for scenario analysis
    - **horizon_days**: Forecast horizon for scenarios
    """
    try:
        prediction_service = PredictionService(db)
        
        # Validate scenarios
        if not scenarios or len(scenarios) > 10:
            raise HTTPException(status_code=400, detail="Invalid number of scenarios (1-10 allowed)")
        
        results = await prediction_service.run_scenario_analysis(
            model_name=model_name,
            scenarios=scenarios,
            base_date=base_date or datetime.utcnow(),
            horizon_days=horizon_days
        )
        
        return {
            "model_name": model_name,
            "base_date": base_date or datetime.utcnow(),
            "horizon_days": horizon_days,
            "scenarios": results.get('scenarios', {}),
            "comparison": results.get('comparison', {}),
            "insights": results.get('insights', []),
            "metadata": results.get('metadata', {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running scenario analysis: {e}")
        raise HTTPException(status_code=500, detail="Scenario analysis failed")


@router.get("/models/{model_name}/performance")
async def get_model_performance(
    model_name: str,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    metric_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get model performance metrics and analysis
    
    - **model_name**: Name of the model
    - **start_date**: Start date for performance analysis
    - **end_date**: End date for performance analysis
    - **metric_type**: Specific metric type to focus on
    """
    try:
        prediction_service = PredictionService(db)
        performance = await prediction_service.get_model_performance(
            model_name=model_name,
            start_date=start_date,
            end_date=end_date,
            metric_type=metric_type
        )
        
        return {
            "model_name": model_name,
            "analysis_period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "performance_metrics": performance.get('metrics', {}),
            "trend_analysis": performance.get('trends', {}),
            "accuracy_analysis": performance.get('accuracy', {}),
            "drift_detection": performance.get('drift', {}),
            "recommendations": performance.get('recommendations', [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching model performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch model performance")


@router.post("/models/{model_name}/explain")
async def explain_prediction(
    model_name: str,
    input_data: Dict[str, Any],
    explanation_type: str = Query("shap", regex="^(shap|lime|permutation)$"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get explanation for a specific prediction
    
    - **model_name**: Name of the model
    - **input_data**: Input data for explanation
    - **explanation_type**: Type of explanation (shap, lime, permutation)
    """
    try:
        prediction_service = PredictionService(db)
        explanation = await prediction_service.explain_prediction(
            model_name=model_name,
            input_data=input_data,
            explanation_type=explanation_type
        )
        
        return {
            "model_name": model_name,
            "input_data": input_data,
            "explanation_type": explanation_type,
            "feature_importance": explanation.get('feature_importance', {}),
            "feature_contributions": explanation.get('contributions', {}),
            "explanation_plots": explanation.get('plots', {}),
            "summary": explanation.get('summary', ""),
            "metadata": explanation.get('metadata', {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error explaining prediction: {e}")
        raise HTTPException(status_code=500, detail="Prediction explanation failed")


@router.get("/predictions/history")
async def get_prediction_history(
    model_name: Optional[str] = None,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(100, le=1000),
    skip: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get prediction history with filtering options
    
    - **model_name**: Filter by specific model
    - **start_date**: Start date for history
    - **end_date**: End date for history
    - **limit**: Maximum number of records
    - **skip**: Number of records to skip
    """
    try:
        prediction_service = PredictionService(db)
        history = await prediction_service.get_prediction_history(
            model_name=model_name,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            skip=skip
        )
        
        return {
            "predictions": history.get('predictions', []),
            "total_count": history.get('total_count', 0),
            "filters": {
                "model_name": model_name,
                "start_date": start_date,
                "end_date": end_date
            },
            "pagination": {
                "limit": limit,
                "skip": skip,
                "has_more": history.get('has_more', False)
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching prediction history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch prediction history")
