"""
Authentication schemas
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    """Schema for user creation"""
    username: str
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    """Schema for authentication token"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str

class PasswordChange(BaseModel):
    """Schema for password change"""
    current_password: str
    new_password: str

class UserUpdate(BaseModel):
    """Schema for user update"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
