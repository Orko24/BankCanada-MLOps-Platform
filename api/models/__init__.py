"""
Database models for Bank of Canada MLOps Platform

This package contains all SQLAlchemy models for:
- Economic data and indicators
- ML model lifecycle management  
- User authentication and authorization
- System monitoring and alerting
"""

from .economic_data_models import (
    EconomicIndicator,
    EconomicDataPoint,
    EconomicForecast,
    DataQualityCheck,
    DataIngestionLog,
    EconomicEvent
)

from .ml_models import (
    MLExperiment,
    MLRun,
    MLModel,
    MLModelVersion,
    ModelDeployment,
    ModelPerformanceMetric
)

from .user_models import (
    Role,
    User,
    UserSession,
    APIKey,
    UserAuditLog,
    SecurityEvent
)

from .monitoring_models import (
    SystemMetric,
    Alert,
    AlertIncident,
    ModelDriftAlert,
    SystemHealth,
    PerformanceBaseline,
    SLADefinition,
    SLAPerformance
)

__all__ = [
    # Economic data models
    "EconomicIndicator",
    "EconomicDataPoint", 
    "EconomicForecast",
    "DataQualityCheck",
    "DataIngestionLog",
    "EconomicEvent",
    
    # ML models
    "MLExperiment",
    "MLRun",
    "MLModel", 
    "MLModelVersion",
    "ModelDeployment",
    "ModelPerformanceMetric",
    
    # User models
    "Role",
    "User",
    "UserSession",
    "APIKey",
    "UserAuditLog",
    "SecurityEvent",
    
    # Monitoring models
    "SystemMetric",
    "Alert",
    "AlertIncident",
    "ModelDriftAlert",
    "SystemHealth",
    "PerformanceBaseline",
    "SLADefinition",
    "SLAPerformance"
]
