"""
Authentication and authorization API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import logging

from ..database import get_db
from ..schemas.auth_schemas import (
    UserCreate,
    UserResponse,
    Token,
    UserLogin,
    PasswordChange,
    UserUpdate
)
from ..services.auth_service import AuthService
from ..utils.auth import get_current_user, get_current_active_user
from ..models.user_models import User

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account
    
    - **username**: Unique username
    - **email**: Valid email address
    - **password**: Strong password
    - **first_name**: User's first name
    - **last_name**: User's last name
    - **role**: User role (default: viewer)
    """
    try:
        auth_service = AuthService(db)
        
        # Check if user already exists
        existing_user = await auth_service.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="User with this email already exists"
            )
        
        existing_username = await auth_service.get_user_by_username(user_data.username)
        if existing_username:
            raise HTTPException(
                status_code=400,
                detail="Username already taken"
            )
        
        # Create new user
        user = await auth_service.create_user(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role_name=user_data.role or "viewer"
        )
        
        return UserResponse.from_orm(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return access token
    
    - **username**: Username or email
    - **password**: User password
    """
    try:
        auth_service = AuthService(db)
        
        # Authenticate user
        user = await auth_service.authenticate_user(
            username=form_data.username,
            password=form_data.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is disabled",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Generate access token
        access_token = await auth_service.create_access_token(user.id)
        
        # Update last login
        await auth_service.update_last_login(user.id)
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=1800,  # 30 minutes
            user_id=user.id,
            username=user.username,
            role=user.role.name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(status_code=500, detail="Login failed")


@router.post("/logout")
async def logout_user(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Logout current user and invalidate session"""
    try:
        auth_service = AuthService(db)
        await auth_service.logout_user(current_user.id)
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error(f"Error during logout: {e}")
        raise HTTPException(status_code=500, detail="Logout failed")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return UserResponse.from_orm(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user profile"""
    try:
        auth_service = AuthService(db)
        updated_user = await auth_service.update_user_profile(
            user_id=current_user.id,
            **user_update.dict(exclude_unset=True)
        )
        
        return UserResponse.from_orm(updated_user)
        
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(status_code=500, detail="Profile update failed")


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Change user password"""
    try:
        auth_service = AuthService(db)
        
        # Verify current password
        if not await auth_service.verify_password(password_data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        await auth_service.update_password(
            user_id=current_user.id,
            new_password=password_data.new_password
        )
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password: {e}")
        raise HTTPException(status_code=500, detail="Password change failed")


@router.post("/refresh-token", response_model=Token)
async def refresh_access_token(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token"""
    try:
        auth_service = AuthService(db)
        
        # Generate new access token
        access_token = await auth_service.create_access_token(current_user.id)
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=1800,  # 30 minutes
            user_id=current_user.id,
            username=current_user.username,
            role=current_user.role.name
        )
        
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        raise HTTPException(status_code=500, detail="Token refresh failed")


@router.get("/permissions")
async def get_user_permissions(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's permissions"""
    try:
        return {
            "user_id": current_user.id,
            "username": current_user.username,
            "role": current_user.role.name,
            "permissions": current_user.role.permissions or {},
            "is_admin": current_user.role.name == "admin",
            "is_economist": current_user.role.name in ["economist", "admin"],
            "can_modify_data": current_user.role.name in ["economist", "admin"],
            "can_deploy_models": current_user.role.name in ["economist", "admin"],
            "can_manage_users": current_user.role.name == "admin"
        }
        
    except Exception as e:
        logger.error(f"Error fetching permissions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch permissions")


@router.get("/sessions")
async def get_user_sessions(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's active sessions"""
    try:
        auth_service = AuthService(db)
        sessions = await auth_service.get_user_sessions(current_user.id)
        
        return {
            "user_id": current_user.id,
            "total_sessions": len(sessions),
            "sessions": sessions
        }
        
    except Exception as e:
        logger.error(f"Error fetching sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch sessions")


@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Revoke a specific user session"""
    try:
        auth_service = AuthService(db)
        success = await auth_service.revoke_session(session_id, current_user.id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"message": "Session revoked successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error revoking session: {e}")
        raise HTTPException(status_code=500, detail="Session revocation failed")


@router.post("/api-keys")
async def create_api_key(
    key_name: str,
    scopes: list = None,
    expires_days: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new API key for programmatic access"""
    try:
        auth_service = AuthService(db)
        
        # Validate scopes based on user role
        allowed_scopes = auth_service.get_allowed_scopes(current_user.role.name)
        if scopes:
            invalid_scopes = set(scopes) - set(allowed_scopes)
            if invalid_scopes:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid scopes: {invalid_scopes}"
                )
        
        api_key = await auth_service.create_api_key(
            user_id=current_user.id,
            name=key_name,
            scopes=scopes or ["read"],
            expires_days=expires_days
        )
        
        return {
            "api_key_id": api_key.id,
            "name": api_key.name,
            "key": api_key.key,  # Only returned once
            "scopes": api_key.scopes,
            "expires_at": api_key.expires_at,
            "message": "Store this key securely - it won't be shown again"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating API key: {e}")
        raise HTTPException(status_code=500, detail="API key creation failed")


@router.get("/api-keys")
async def list_api_keys(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's API keys (without actual key values)"""
    try:
        auth_service = AuthService(db)
        api_keys = await auth_service.get_user_api_keys(current_user.id)
        
        return {
            "api_keys": [
                {
                    "id": key.id,
                    "name": key.name,
                    "scopes": key.scopes,
                    "created_at": key.created_at,
                    "expires_at": key.expires_at,
                    "last_used": key.last_used,
                    "is_active": key.is_active
                }
                for key in api_keys
            ]
        }
        
    except Exception as e:
        logger.error(f"Error listing API keys: {e}")
        raise HTTPException(status_code=500, detail="Failed to list API keys")


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Revoke an API key"""
    try:
        auth_service = AuthService(db)
        success = await auth_service.revoke_api_key(key_id, current_user.id)
        
        if not success:
            raise HTTPException(status_code=404, detail="API key not found")
        
        return {"message": "API key revoked successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error revoking API key: {e}")
        raise HTTPException(status_code=500, detail="API key revocation failed")
