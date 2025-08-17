"""
Database models for user management, authentication, and authorization
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any

from database import Base


class Role(Base):
    """User roles and permissions"""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(Text)
    
    # Permission levels
    level = Column(Integer, default=1)  # 1=viewer, 2=analyst, 3=economist, 4=admin
    
    # Permissions
    permissions = Column(JSON)  # Detailed permissions object
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="role")
    
    def __repr__(self):
        return f"<Role(name='{self.name}', level={self.level})>"


class User(Base):
    """Application users with authentication and profile information"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Authentication
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile information
    first_name = Column(String(50))
    last_name = Column(String(50))
    full_name = Column(String(100))
    
    # Role and permissions
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    
    # Security
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True))
    password_changed_at = Column(DateTime(timezone=True))
    last_login = Column(DateTime(timezone=True))
    
    # Two-factor authentication
    totp_secret = Column(String(32))  # TOTP secret for 2FA
    backup_codes = Column(JSON)       # Backup codes for 2FA
    mfa_enabled = Column(Boolean, default=False)
    
    # Preferences
    preferences = Column(JSON)  # User preferences and settings
    timezone = Column(String(50), default="UTC")
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(100))
    
    # Profile completion
    profile_completed = Column(Boolean, default=False)
    
    # Relationships
    role = relationship("Role", back_populates="users")
    sessions = relationship("UserSession", back_populates="user")
    api_keys = relationship("APIKey", back_populates="user")
    audit_logs = relationship("UserAuditLog", back_populates="user")
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}', role_id={self.role_id})>"


class UserSession(Base):
    """User session tracking for security and analytics"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Session details
    session_token = Column(String(255), unique=True, index=True, nullable=False)
    refresh_token = Column(String(255), unique=True, index=True)
    
    # Device and location information
    ip_address = Column(String(45))  # IPv6 support
    user_agent = Column(String(500))
    device_type = Column(String(50))  # desktop, mobile, tablet
    browser = Column(String(100))
    platform = Column(String(100))
    
    # Location (if available)
    country = Column(String(2))  # ISO country code
    city = Column(String(100))
    
    # Session lifecycle
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Security flags
    is_suspicious = Column(Boolean, default=False)
    risk_score = Column(Float, default=0.0)  # 0.0 to 1.0
    
    # Metadata
    session_data = Column(JSON)  # Additional session context
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_active', 'user_id', 'is_active'),
        Index('idx_session_expires_at', 'expires_at'),
    )
    
    def __repr__(self):
        return f"<UserSession(user_id={self.user_id}, ip='{self.ip_address}', active={self.is_active})>"


class APIKey(Base):
    """API keys for programmatic access"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # API key details
    name = Column(String(100), nullable=False)
    key_hash = Column(String(255), unique=True, index=True, nullable=False)
    key_prefix = Column(String(10), index=True)  # First few chars for identification
    
    # Permissions and scope
    scopes = Column(JSON)  # List of allowed operations
    rate_limit_per_hour = Column(Integer, default=1000)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Usage tracking
    last_used = Column(DateTime(timezone=True))
    usage_count = Column(Integer, default=0)
    
    # Lifecycle
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    revoked_at = Column(DateTime(timezone=True))
    revoked_reason = Column(String(200))
    
    # Security
    allowed_ips = Column(JSON)  # List of allowed IP addresses
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_active_keys', 'user_id', 'is_active'),
        Index('idx_api_key_expires_at', 'expires_at'),
    )
    
    def __repr__(self):
        return f"<APIKey(name='{self.name}', user_id={self.user_id}, active={self.is_active})>"


class UserAuditLog(Base):
    """Audit log for user actions and security events"""
    __tablename__ = "user_audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Event details
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50))  # model, data, user, etc.
    resource_id = Column(String(100))
    
    # Event metadata
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    session_id = Column(String(255))
    
    # Request details
    method = Column(String(10))  # GET, POST, PUT, DELETE
    endpoint = Column(String(200))
    request_id = Column(String(100))
    
    # Event outcome
    status = Column(String(20))  # success, failure, error
    status_code = Column(Integer)
    error_message = Column(Text)
    
    # Data changes (for sensitive operations)
    old_values = Column(JSON)  # Previous values
    new_values = Column(JSON)  # New values
    
    # Risk assessment
    risk_level = Column(String(20), default="low")  # low, medium, high, critical
    is_suspicious = Column(Boolean, default=False)
    
    # Additional context
    session_metadata = Column(JSON)
    tags = Column(JSON)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_action_timestamp', 'action', 'timestamp'),
        Index('idx_risk_level', 'risk_level', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<UserAuditLog(user_id={self.user_id}, action='{self.action}', status='{self.status}')>"


class SecurityEvent(Base):
    """Security events and threat detection"""
    __tablename__ = "security_events"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Event classification
    event_type = Column(String(50), nullable=False, index=True)  # failed_login, suspicious_activity, etc.
    severity = Column(String(20), nullable=False, index=True)    # low, medium, high, critical
    category = Column(String(50))  # authentication, authorization, data_access, etc.
    
    # Event details
    title = Column(String(200), nullable=False)
    description = Column(Text)
    source = Column(String(100))  # system, user, external
    
    # Affected entities
    user_id = Column(Integer, ForeignKey("users.id"))
    ip_address = Column(String(45))
    session_id = Column(String(255))
    
    # Event data
    event_data = Column(JSON)  # Detailed event information
    indicators = Column(JSON)  # IOCs and patterns
    
    # Response
    status = Column(String(20), default="open")  # open, investigating, resolved, false_positive
    assigned_to = Column(String(100))
    resolution_notes = Column(Text)
    
    # Timing
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    resolved_at = Column(DateTime(timezone=True))
    
    # Automated response
    auto_response_taken = Column(Boolean, default=False)
    response_actions = Column(JSON)
    
    # Indexes
    __table_args__ = (
        Index('idx_severity_detected', 'severity', 'detected_at'),
        Index('idx_status_detected', 'status', 'detected_at'),
        Index('idx_user_events', 'user_id', 'detected_at'),
    )
    
    def __repr__(self):
        return f"<SecurityEvent(type='{self.event_type}', severity='{self.severity}', status='{self.status}')>"
