"""
AI Agents API endpoints for dynamic configuration and economic research
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
import logging
import asyncio
from datetime import datetime

from ..database import get_db
from ..utils.auth import get_current_user
from ..models.user_models import User

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory storage for API keys per session
# In production, you'd use Redis or encrypted session storage
session_api_keys = {}

class AIAgentService:
    """Service for managing AI agents with dynamic API keys"""
    
    @staticmethod
    def store_api_key(session_id: str, api_key: str):
        """Store API key for session"""
        session_api_keys[session_id] = {
            'api_key': api_key,
            'stored_at': datetime.utcnow(),
            'provider': 'deepseek'
        }
    
    @staticmethod
    def get_api_key(session_id: str) -> Optional[str]:
        """Get API key for session"""
        session_data = session_api_keys.get(session_id)
        return session_data['api_key'] if session_data else None
    
    @staticmethod
    def remove_api_key(session_id: str):
        """Remove API key for session"""
        session_api_keys.pop(session_id, None)
    
    @staticmethod
    def has_api_key(session_id: str) -> bool:
        """Check if session has API key"""
        return session_id in session_api_keys
    
    @staticmethod
    async def test_deepseek_api_key(api_key: str) -> Dict[str, Any]:
        """Test DeepSeek API key validity"""
        try:
            from langchain_community.chat_models import ChatOpenAI
            
            # Create a test LLM instance
            llm = ChatOpenAI(
                model="deepseek-chat",
                openai_api_key=api_key,
                openai_api_base="https://api.deepseek.com/v1",
                temperature=0.1,
                max_tokens=10
            )
            
            # Test with a simple query
            response = await asyncio.to_thread(
                llm.invoke, 
                "Hello"
            )
            
            return {
                'valid': True,
                'provider': 'DeepSeek',
                'model': 'deepseek-chat',
                'test_response': str(response.content)[:50]
            }
            
        except Exception as e:
            logger.error(f"DeepSeek API key test failed: {e}")
            return {
                'valid': False,
                'error': str(e),
                'provider': 'DeepSeek'
            }


def get_session_id(request: Request) -> str:
    """Get or create session ID"""
    # In a real app, you'd use proper session management
    # For demo purposes, we'll use a simple approach
    session_id = request.headers.get('X-Session-ID')
    if not session_id:
        # Use client IP + user agent as a simple session identifier
        client_ip = request.client.host
        user_agent = request.headers.get('User-Agent', '')
        session_id = f"{client_ip}_{hash(user_agent)}"
    return session_id


@router.post("/api-key/set")
async def set_api_key(
    request: Request,
    data: Dict[str, str],
    current_user: User = Depends(get_current_user)
):
    """Set API key for the current session"""
    try:
        api_key = data.get('api_key')
        if not api_key:
            raise HTTPException(status_code=400, detail="API key is required")
        
        session_id = get_session_id(request)
        AIAgentService.store_api_key(session_id, api_key)
        
        return {
            "success": True,
            "message": "API key stored successfully",
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"Error setting API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to store API key")


@router.post("/api-key/test")
async def test_api_key(
    request: Request,
    data: Dict[str, str],
    current_user: User = Depends(get_current_user)
):
    """Test API key validity"""
    try:
        api_key = data.get('api_key')
        if not api_key:
            raise HTTPException(status_code=400, detail="API key is required")
        
        # Test the API key
        test_result = await AIAgentService.test_deepseek_api_key(api_key)
        
        return {
            "success": True,
            "result": test_result
        }
        
    except Exception as e:
        logger.error(f"Error testing API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to test API key")


@router.get("/api-key/status")
async def get_api_key_status(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get API key status for current session"""
    try:
        session_id = get_session_id(request)
        has_key = AIAgentService.has_api_key(session_id)
        
        result = {
            "hasKey": has_key,
            "valid": False,
            "provider": None
        }
        
        if has_key:
            # Test the stored key
            api_key = AIAgentService.get_api_key(session_id)
            test_result = await AIAgentService.test_deepseek_api_key(api_key)
            result.update({
                "valid": test_result['valid'],
                "provider": test_result.get('provider', 'DeepSeek')
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error checking API key status: {e}")
        raise HTTPException(status_code=500, detail="Failed to check API key status")


@router.delete("/api-key")
async def remove_api_key(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Remove API key from current session"""
    try:
        session_id = get_session_id(request)
        AIAgentService.remove_api_key(session_id)
        
        return {
            "success": True,
            "message": "API key removed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error removing API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove API key")


@router.post("/research")
async def conduct_research(
    request: Request,
    data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Conduct economic research using AI agent"""
    try:
        session_id = get_session_id(request)
        api_key = AIAgentService.get_api_key(session_id)
        
        if not api_key:
            raise HTTPException(
                status_code=400, 
                detail="No API key configured. Please set your DeepSeek API key first."
            )
        
        question = data.get('question')
        if not question:
            raise HTTPException(status_code=400, detail="Research question is required")
        
        # Initialize agent with session API key
        from ..services.ai_agent_service import EconomicResearchService
        research_service = EconomicResearchService(api_key=api_key)
        
        # Conduct research
        result = await research_service.research(
            question=question,
            context=data.get('context'),
            indicators=data.get('indicators', [])
        )
        
        return {
            "success": True,
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error conducting research: {e}")
        raise HTTPException(status_code=500, detail="Research failed")


@router.post("/chat")
async def chat_with_agent(
    request: Request,
    data: Dict[str, str],
    current_user: User = Depends(get_current_user)
):
    """Chat with the economic research agent"""
    try:
        session_id = get_session_id(request)
        api_key = AIAgentService.get_api_key(session_id)
        
        if not api_key:
            raise HTTPException(
                status_code=400,
                detail="No API key configured. Please set your DeepSeek API key first."
            )
        
        message = data.get('message')
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Initialize agent with session API key
        from ..services.ai_agent_service import EconomicResearchService
        research_service = EconomicResearchService(api_key=api_key)
        
        # Get chat response
        response = await research_service.chat(message)
        
        return {
            "success": True,
            "response": response,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail="Chat failed")


@router.get("/capabilities")
async def get_agent_capabilities(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get available AI agent capabilities"""
    try:
        session_id = get_session_id(request)
        has_key = AIAgentService.has_api_key(session_id)
        
        capabilities = {
            "economic_research": {
                "name": "Economic Research",
                "description": "Comprehensive economic analysis and research",
                "available": has_key
            },
            "policy_analysis": {
                "name": "Policy Analysis", 
                "description": "Analysis of monetary policy documents and decisions",
                "available": has_key
            },
            "data_correlation": {
                "name": "Data Correlation",
                "description": "Statistical analysis of economic indicator relationships",
                "available": has_key
            },
            "scenario_modeling": {
                "name": "Scenario Modeling",
                "description": "Economic scenario analysis and forecasting",
                "available": has_key
            }
        }
        
        return {
            "success": True,
            "capabilities": capabilities,
            "ai_enabled": has_key
        }
        
    except Exception as e:
        logger.error(f"Error getting capabilities: {e}")
        raise HTTPException(status_code=500, detail="Failed to get capabilities")
