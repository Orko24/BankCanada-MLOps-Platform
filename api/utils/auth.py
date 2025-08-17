"""
Authentication utilities
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from database import get_db
from models.user_models import User

logger = logging.getLogger(__name__)
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    # For now, return a mock user to get the app running
    # In production, you'd decode the JWT token and fetch the real user
    mock_user = User(
        id=1,
        username="test_user",
        email="test@bankofcanada.ca",
        is_active=True,
        is_verified=True
    )
    return mock_user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

async def get_optional_user(
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current user, but don't require authentication for demo purposes"""
    try:
        # For demo purposes, return mock user without requiring valid token
        mock_user = User(
            id=1,
            username="demo_user",
            email="demo@bankofcanada.ca",
            is_active=True,
            is_verified=True
        )
        return mock_user
    except Exception:
        # Fallback mock user if anything fails
        return User(
            id=1,
            username="demo_user",
            email="demo@bankofcanada.ca",
            is_active=True,
            is_verified=True
        )