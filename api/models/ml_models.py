"""
Database models for ML model lifecycle management and MLOps tracking
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

from ..database import Base


class MLExperiment(Base):
    """ML experiments for organizing model development"""
    __tablename__ = "ml_experiments"
    
    id = Column(Integer, primary_key=True, index=True)
    mlflow_experiment_id = Column(String(100), unique=True, index=True)
    
    # Experiment details
    name = Column(String(200), nullable=False, unique=True)
    description = Column(Text)
    objective = Column(String(100))  # minimize_mae, maximize_accuracy, etc.
    
    # Economic focus
    target_indicators = Column(JSON)  # List of economic indicators being predicted
    forecast_horizon_days = Column(Integer)
    
    # Status and lifecycle
    status = Column(String(20), default="active")  # active, completed, archived
    created_by = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Configuration
    experiment_config = Column(JSON)
    
    # Relationships
    runs = relationship("MLRun", back_populates="experiment")
    models = relationship("MLModel", back_populates="experiment")
    
    def __repr__(self):
        return f"<MLExperiment(name='{self.name}', status='{self.status}')>"


class MLRun(Base):
    """Individual ML training runs and experiments"""
    __tablename__ = "ml_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    mlflow_run_id = Column(String(100), unique=True, index=True, nullable=False)
    experiment_id = Column(Integer, ForeignKey("ml_experiments.id"), nullable=False)
    
    # Run details
    name = Column(String(200))
    status = Column(String(20))  # running, finished, failed, killed
    
    # Timing
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True))
    duration_seconds = Column(Float)
    
    # Model and data information
    model_type = Column(String(50))  # lstm, arima, xgboost, etc.
    algorithm = Column(String(100))
    data_version = Column(String(50))
    train_data_start = Column(DateTime(timezone=True))
    train_data_end = Column(DateTime(timezone=True))
    
    # Hyperparameters and configuration
    hyperparameters = Column(JSON)
    model_config = Column(JSON)
    
    # Performance metrics
    metrics = Column(JSON)
    validation_score = Column(Float)
    test_score = Column(Float)
    
    # Resource usage
    compute_resources = Column(JSON)
    memory_usage_mb = Column(Float)
    cpu_time_seconds = Column(Float)
    
    # Tags and metadata
    tags = Column(JSON)
    notes = Column(Text)
    
    # User tracking
    created_by = Column(String(100))
    
    # Relationships
    experiment = relationship("MLExperiment", back_populates="runs")
    model_versions = relationship("MLModelVersion", back_populates="training_run")
    
    # Indexes
    __table_args__ = (
        Index('idx_experiment_status', 'experiment_id', 'status'),
        Index('idx_start_time', 'start_time'),
    )
    
    def __repr__(self):
        return f"<MLRun(mlflow_run_id='{self.mlflow_run_id}', status='{self.status}')>"


class MLModel(Base):
    """ML model registry and metadata"""
    __tablename__ = "ml_models"
    
    id = Column(Integer, primary_key=True, index=True)
    mlflow_model_name = Column(String(200), unique=True, index=True, nullable=False)
    experiment_id = Column(Integer, ForeignKey("ml_experiments.id"))
    
    # Model details
    name = Column(String(200), nullable=False)
    description = Column(Text)
    model_type = Column(String(50))  # forecasting, classification, regression
    algorithm = Column(String(100))
    
    # Economic model specifics
    target_indicator = Column(String(50))  # What economic indicator this predicts
    forecast_horizon_days = Column(Integer)
    update_frequency_hours = Column(Integer, default=24)
    
    # Model lifecycle
    status = Column(String(20), default="development")  # development, staging, production, archived
    current_version = Column(String(50))
    latest_version = Column(String(50))
    
    # Performance tracking
    best_validation_score = Column(Float)
    production_score = Column(Float)
    
    # Business metadata
    business_impact = Column(Text)
    use_cases = Column(JSON)
    stakeholders = Column(JSON)
    
    # Compliance and governance
    approval_status = Column(String(20), default="pending")  # pending, approved, rejected
    approved_by = Column(String(100))
    approval_date = Column(DateTime(timezone=True))
    
    # Metadata
    created_by = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Configuration
    model_config = Column(JSON)
    
    # Relationships
    experiment = relationship("MLExperiment", back_populates="models")
    versions = relationship("MLModelVersion", back_populates="model")
    deployments = relationship("ModelDeployment", back_populates="model")
    
    def __repr__(self):
        return f"<MLModel(name='{self.name}', status='{self.status}', current_version='{self.current_version}')>"


class MLModelVersion(Base):
    """Specific versions of ML models"""
    __tablename__ = "ml_model_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("ml_models.id"), nullable=False)
    training_run_id = Column(Integer, ForeignKey("ml_runs.id"))
    mlflow_version = Column(String(50), nullable=False)
    
    # Version details
    version = Column(String(50), nullable=False)
    name = Column(String(200))
    description = Column(Text)
    
    # Performance metrics
    validation_metrics = Column(JSON)
    test_metrics = Column(JSON)
    benchmark_scores = Column(JSON)
    
    # Model artifacts
    model_uri = Column(String(500))
    model_size_mb = Column(Float)
    artifact_location = Column(String(500))
    
    # Data information
    training_data_version = Column(String(50))
    training_data_size = Column(Integer)
    feature_schema = Column(JSON)
    
    # Status and lifecycle
    status = Column(String(20), default="candidate")  # candidate, staging, production, archived
    stage_transition_date = Column(DateTime(timezone=True))
    
    # Approval workflow
    review_status = Column(String(20), default="pending")  # pending, approved, rejected
    reviewed_by = Column(String(100))
    review_date = Column(DateTime(timezone=True))
    review_notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(100))
    
    # Relationships
    model = relationship("MLModel", back_populates="versions")
    training_run = relationship("MLRun", back_populates="model_versions")
    deployments = relationship("ModelDeployment", back_populates="model_version")
    
    # Indexes
    __table_args__ = (
        Index('idx_model_version', 'model_id', 'version'),
        Index('idx_status_date', 'status', 'created_at'),
    )
    
    def __repr__(self):
        return f"<MLModelVersion(model_id={self.model_id}, version='{self.version}', status='{self.status}')>"


class ModelDeployment(Base):
    """Model deployment tracking and management"""
    __tablename__ = "model_deployments"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("ml_models.id"), nullable=False)
    model_version_id = Column(Integer, ForeignKey("ml_model_versions.id"), nullable=False)
    
    # Deployment details
    deployment_name = Column(String(200), nullable=False)
    environment = Column(String(50), nullable=False)  # development, staging, production
    platform = Column(String(50))  # azure-ml, kubernetes, local
    
    # Endpoint information
    endpoint_url = Column(String(500))
    endpoint_type = Column(String(50))  # rest-api, batch, streaming
    
    # Status and lifecycle
    status = Column(String(20), default="deploying")  # deploying, active, inactive, failed, terminated
    health_status = Column(String(20), default="unknown")  # healthy, unhealthy, degraded
    
    # Deployment configuration
    resource_config = Column(JSON)  # CPU, memory, GPU requirements
    scaling_config = Column(JSON)   # Auto-scaling configuration
    deployment_config = Column(JSON)
    
    # Performance and monitoring
    request_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    average_response_time_ms = Column(Float)
    last_health_check = Column(DateTime(timezone=True))
    
    # Timing
    deployed_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())
    terminated_at = Column(DateTime(timezone=True))
    
    # User tracking
    deployed_by = Column(String(100))
    
    # Relationships
    model = relationship("MLModel", back_populates="deployments")
    model_version = relationship("MLModelVersion", back_populates="deployments")
    
    # Indexes
    __table_args__ = (
        Index('idx_environment_status', 'environment', 'status'),
        Index('idx_deployed_at', 'deployed_at'),
    )
    
    def __repr__(self):
        return f"<ModelDeployment(name='{self.deployment_name}', environment='{self.environment}', status='{self.status}')>"


class ModelPerformanceMetric(Base):
    """Ongoing model performance monitoring"""
    __tablename__ = "model_performance_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    model_version_id = Column(Integer, ForeignKey("ml_model_versions.id"), nullable=False)
    deployment_id = Column(Integer, ForeignKey("model_deployments.id"))
    
    # Metric details
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_type = Column(String(50))  # accuracy, mae, rmse, latency, throughput
    
    # Context
    evaluation_date = Column(DateTime(timezone=True), nullable=False, index=True)
    data_period_start = Column(DateTime(timezone=True))
    data_period_end = Column(DateTime(timezone=True))
    sample_size = Column(Integer)
    
    # Metadata
    calculation_method = Column(String(100))
    benchmark_value = Column(Float)  # Expected/baseline value
    threshold_min = Column(Float)    # Minimum acceptable value
    threshold_max = Column(Float)    # Maximum acceptable value
    
    # Status
    is_within_threshold = Column(Boolean)
    alert_triggered = Column(Boolean, default=False)
    
    # Additional context
    tags = Column(JSON)
    metadata = Column(JSON)
    
    # Indexes
    __table_args__ = (
        Index('idx_model_metric_date', 'model_version_id', 'metric_name', 'evaluation_date'),
        Index('idx_eval_date', 'evaluation_date'),
    )
    
    def __repr__(self):
        return f"<ModelPerformanceMetric(model_version_id={self.model_version_id}, metric='{self.metric_name}', value={self.metric_value})>"
