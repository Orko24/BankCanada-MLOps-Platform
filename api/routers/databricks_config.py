"""
Databricks Configuration API endpoints
"""

from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any, Optional
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory storage for Databricks configs per session
session_databricks_configs = {}

def get_session_id(request: Request) -> str:
    """Get or create session ID"""
    session_id = request.headers.get('X-Session-ID')
    if not session_id:
        client_ip = request.client.host
        user_agent = request.headers.get('User-Agent', '')
        session_id = f"{client_ip}_{hash(user_agent)}"
    return session_id

class DatabricksConfigService:
    """Service for managing Databricks configurations"""
    
    @staticmethod
    def store_config(session_id: str, host: str, token: str, workspace_id: str = None):
        """Store Databricks configuration for session"""
        session_databricks_configs[session_id] = {
            'host': host,
            'token': token,
            'workspace_id': workspace_id,
            'stored_at': datetime.utcnow()
        }
    
    @staticmethod
    def get_config(session_id: str) -> Optional[Dict[str, str]]:
        """Get Databricks configuration for session"""
        return session_databricks_configs.get(session_id)
    
    @staticmethod
    def remove_config(session_id: str):
        """Remove Databricks configuration for session"""
        session_databricks_configs.pop(session_id, None)
    
    @staticmethod
    def has_config(session_id: str) -> bool:
        """Check if session has Databricks configuration"""
        return session_id in session_databricks_configs


@router.post("/set")
async def set_databricks_config(
    request: Request,
    data: Dict[str, Any]
):
    """Set Databricks configuration for the session"""
    try:
        session_id = get_session_id(request)
        
        host = data.get('host')
        token = data.get('token')
        workspace_id = data.get('workspace_id')
        
        if not host or not token:
            raise HTTPException(
                status_code=400, 
                detail="Host and token are required"
            )
        
        DatabricksConfigService.store_config(session_id, host, token, workspace_id)
        
        return {
            "success": True,
            "message": "Databricks configuration saved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting Databricks config: {e}")
        raise HTTPException(status_code=500, detail="Failed to save Databricks configuration")


@router.post("/test")
async def test_databricks_config(
    request: Request,
    data: Dict[str, Any]
):
    """Test Databricks configuration"""
    try:
        host = data.get('host')
        token = data.get('token')
        
        if not host or not token:
            raise HTTPException(
                status_code=400,
                detail="Host and token are required"
            )
        
        # Test Databricks connection
        import httpx
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{host}/api/2.0/clusters/list",
                headers=headers
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Databricks connection successful",
                    "result": "Connected to Databricks workspace"
                }
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Databricks connection failed: {response.status_code}"
                )
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing Databricks config: {e}")
        raise HTTPException(status_code=500, detail="Failed to test Databricks configuration")


@router.get("/status")
async def get_databricks_config_status(
    request: Request
):
    """Check if Databricks configuration is set for the session"""
    try:
        session_id = get_session_id(request)
        has_config = DatabricksConfigService.has_config(session_id)
        
        return {
            "has_config": has_config,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error checking Databricks config status: {e}")
        raise HTTPException(status_code=500, detail="Failed to check configuration status")


@router.delete("/")
async def remove_databricks_config(
    request: Request
):
    """Remove Databricks configuration"""
    try:
        session_id = get_session_id(request)
        DatabricksConfigService.remove_config(session_id)
        
        return {
            "success": True,
            "message": "Databricks configuration removed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error removing Databricks config: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove Databricks configuration")
