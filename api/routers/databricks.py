"""
Databricks monitoring and management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, Optional
import logging

from services.hybrid_database import HybridDatabaseService
from services.credit_monitor import CreditMonitorService
from services.mlflow_service import mlflow_service
from utils.auth import get_current_user
from models.user_models import User
from config import DatabricksConfig, MLflowConfig

router = APIRouter()
logger = logging.getLogger(__name__)

# Global instances
hybrid_db = HybridDatabaseService()
credit_monitor = CreditMonitorService()

@router.get("/status")
async def get_databricks_status(
    current_user: User = Depends(get_current_user)
):
    """Get Databricks connection and credit status"""
    try:
        status = await hybrid_db.get_status()
        return {
            "status": "success",
            "databricks": status,
            "timestamp": "2024-01-15T10:30:00Z"
        }
    except Exception as e:
        logger.error(f"Failed to get Databricks status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve Databricks status")

@router.get("/credits")
async def get_credit_usage(
    current_user: User = Depends(get_current_user)
):
    """Get detailed credit usage information"""
    try:
        credit_info = await credit_monitor.check_credit_usage()
        recommendations = await credit_monitor.get_recommendations()
        
        return {
            "status": "success",
            "credit_usage": credit_info,
            "recommendations": recommendations,
            "fallback_active": credit_monitor.is_fallback_mode()
        }
    except Exception as e:
        logger.error(f"Failed to get credit usage: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve credit usage")

@router.post("/credits/simulate")
async def simulate_credit_usage(
    usage_percent: float = Query(..., ge=0, le=100, description="Credit usage percentage to simulate"),
    current_user: User = Depends(get_current_user)
):
    """Simulate credit usage for testing fallback mechanisms"""
    try:
        if usage_percent < 0 or usage_percent > 100:
            raise HTTPException(status_code=400, detail="Usage percentage must be between 0 and 100")
        
        status = await hybrid_db.simulate_credit_usage(usage_percent)
        
        return {
            "status": "success",
            "message": f"Credit usage simulated at {usage_percent}%",
            "new_status": status,
            "fallback_activated": status["credit_usage"]["fallback_mode"]
        }
    except Exception as e:
        logger.error(f"Failed to simulate credit usage: {e}")
        raise HTTPException(status_code=500, detail="Failed to simulate credit usage")

@router.post("/fallback/reset")
async def reset_fallback_mode(
    current_user: User = Depends(get_current_user)
):
    """Reset fallback mode (admin function)"""
    try:
        credit_monitor.reset_fallback()
        status = await hybrid_db.get_status()
        
        return {
            "status": "success",
            "message": "Fallback mode reset",
            "new_status": status
        }
    except Exception as e:
        logger.error(f"Failed to reset fallback mode: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset fallback mode")

@router.get("/database/health")
async def check_database_health(
    current_user: User = Depends(get_current_user)
):
    """Check health of both Databricks and PostgreSQL connections"""
    try:
        # Test a simple query on both systems
        test_query = "SELECT 1 as test_value"
        
        # Test Databricks
        databricks_result = await hybrid_db.execute_query(test_query, prefer_databricks=True)
        databricks_healthy = databricks_result is not None
        
        # Test PostgreSQL 
        postgres_result = await hybrid_db.execute_query(test_query, prefer_databricks=False)
        postgres_healthy = postgres_result is not None
        
        overall_status = await hybrid_db.get_status()
        
        return {
            "status": "success",
            "health_check": {
                "databricks": {
                    "healthy": databricks_healthy,
                    "available": overall_status["databricks"]["available"]
                },
                "postgresql": {
                    "healthy": postgres_healthy,
                    "available": overall_status["postgresql"]["available"]
                }
            },
            "active_database": overall_status["active_database"],
            "credit_status": overall_status["credit_usage"]
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(status_code=500, detail="Database health check failed")

@router.get("/tables")
async def list_tables(
    database: Optional[str] = Query(None, description="Specific database to query (databricks or postgresql)"),
    current_user: User = Depends(get_current_user)
):
    """List available tables in the active database"""
    try:
        if database and database.lower() not in ["databricks", "postgresql"]:
            raise HTTPException(status_code=400, detail="Database must be 'databricks' or 'postgresql'")
        
        prefer_databricks = database != "postgresql" if database else True
        
        # Query to get table list (works on both Databricks and PostgreSQL)
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'system')
        ORDER BY table_name
        """
        
        result = await hybrid_db.execute_query(query, prefer_databricks=prefer_databricks)
        
        if result is not None:
            tables = result['table_name'].tolist() if 'table_name' in result.columns else []
        else:
            tables = []
        
        status = await hybrid_db.get_status()
        
        return {
            "status": "success",
            "database_used": status["active_database"],
            "tables": tables,
            "table_count": len(tables)
        }
    except Exception as e:
        logger.error(f"Failed to list tables: {e}")
        raise HTTPException(status_code=500, detail="Failed to list tables")

@router.get("/mlflow/status")
async def get_mlflow_status(
    current_user: User = Depends(get_current_user)
):
    """Get MLflow configuration and status"""
    try:
        mlflow_info = await mlflow_service.get_experiment_info()
        
        return {
            "status": "success",
            "mlflow": mlflow_info,
            "databricks_available": DatabricksConfig.is_configured(),
            "mode": MLflowConfig.get_mode()
        }
    except Exception as e:
        logger.error(f"Failed to get MLflow status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve MLflow status")

@router.get("/system/overview")
async def get_system_overview(
    current_user: User = Depends(get_current_user)
):
    """Get complete system overview including database and MLflow status"""
    try:
        # Get database status
        db_status = await hybrid_db.get_status()
        
        # Get MLflow status
        mlflow_info = await mlflow_service.get_experiment_info()
        
        # Determine system mode
        has_databricks = DatabricksConfig.is_configured()
        db_mode = "hybrid" if has_databricks and db_status["databricks"]["available"] else "postgresql_only"
        
        return {
            "status": "success",
            "system_mode": db_mode,
            "capabilities": {
                "databricks_sql": has_databricks and db_status["databricks"]["available"],
                "postgresql": db_status["postgresql"]["available"],
                "mlflow_databricks": mlflow_info.get("mode") == "databricks",
                "mlflow_local": mlflow_info.get("mode") == "local",
                "credit_monitoring": has_databricks
            },
            "database": db_status,
            "mlflow": mlflow_info,
            "recommendations": db_status.get("recommendations", []),
            "configuration": {
                "databricks_configured": has_databricks,
                "credit_threshold": DatabricksConfig.get_credit_threshold() if has_databricks else None,
                "mlflow_mode": MLflowConfig.get_mode(),
                "tracking_uri": mlflow_info.get("tracking_uri")
            }
        }
    except Exception as e:
        logger.error(f"Failed to get system overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system overview")

@router.post("/initialize")
async def initialize_databricks(
    current_user: User = Depends(get_current_user)
):
    """Initialize Databricks connection and setup"""
    try:
        await hybrid_db.initialize()
        await mlflow_service.initialize()
        
        status = await hybrid_db.get_status()
        mlflow_info = await mlflow_service.get_experiment_info()
        
        return {
            "status": "success",
            "message": "System initialized successfully",
            "database": status,
            "mlflow": mlflow_info
        }
    except Exception as e:
        logger.error(f"Failed to initialize system: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize system")
