"""
Database models for system monitoring, alerting, and observability
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any

from ..database import Base


class SystemMetric(Base):
    """System-level metrics for infrastructure monitoring"""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Metric identification
    metric_name = Column(String(100), nullable=False, index=True)
    metric_type = Column(String(50), nullable=False)  # gauge, counter, histogram, summary
    service = Column(String(50), nullable=False)      # api, worker, database, etc.
    instance = Column(String(100))                    # Service instance identifier
    
    # Metric data
    value = Column(Float, nullable=False)
    unit = Column(String(20))  # cpu_percent, memory_bytes, requests_per_second, etc.
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Labels and metadata
    labels = Column(JSON)      # Key-value pairs for metric dimensions
    metadata = Column(JSON)    # Additional metric context
    
    # Quality indicators
    quality = Column(String(20), default="good")  # good, degraded, poor
    source = Column(String(50))  # prometheus, custom, azure_monitor, etc.
    
    # Indexes
    __table_args__ = (
        Index('idx_metric_service_time', 'metric_name', 'service', 'timestamp'),
        Index('idx_timestamp_desc', 'timestamp', postgresql_using='btree'),
    )
    
    def __repr__(self):
        return f"<SystemMetric(name='{self.metric_name}', service='{self.service}', value={self.value})>"


class Alert(Base):
    """Alert definitions and configurations"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Alert definition
    name = Column(String(200), nullable=False, unique=True)
    description = Column(Text)
    category = Column(String(50))  # performance, security, data_quality, model_drift, etc.
    
    # Alert conditions
    metric_name = Column(String(100), nullable=False)
    service = Column(String(50))
    condition_type = Column(String(20), nullable=False)  # threshold, anomaly, trend, etc.
    threshold_value = Column(Float)
    threshold_operator = Column(String(10))  # >, <, >=, <=, ==, !=
    
    # Severity and priority
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    priority = Column(Integer, default=3)  # 1=highest, 5=lowest
    
    # Conditions
    evaluation_window_minutes = Column(Integer, default=5)
    trigger_threshold_count = Column(Integer, default=1)  # How many times condition must be met
    
    # Status and lifecycle
    is_active = Column(Boolean, default=True)
    is_muted = Column(Boolean, default=False)
    mute_until = Column(DateTime(timezone=True))
    
    # Notification settings
    notification_channels = Column(JSON)  # email, slack, pagerduty, etc.
    escalation_policy = Column(JSON)
    
    # Metadata
    created_by = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Alert configuration
    alert_config = Column(JSON)
    
    # Relationships
    incidents = relationship("AlertIncident", back_populates="alert")
    
    def __repr__(self):
        return f"<Alert(name='{self.name}', severity='{self.severity}', active={self.is_active})>"


class AlertIncident(Base):
    """Individual alert incidents and their lifecycle"""
    __tablename__ = "alert_incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=False)
    
    # Incident details
    incident_id = Column(String(100), unique=True, index=True, nullable=False)
    title = Column(String(300), nullable=False)
    description = Column(Text)
    
    # Status and lifecycle
    status = Column(String(20), default="open")  # open, acknowledged, investigating, resolved
    severity = Column(String(20), nullable=False)
    priority = Column(Integer)
    
    # Timing
    triggered_at = Column(DateTime(timezone=True), nullable=False, index=True)
    acknowledged_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))
    duration_minutes = Column(Integer)
    
    # Values and conditions
    trigger_value = Column(Float)
    threshold_value = Column(Float)
    trigger_condition = Column(String(200))
    
    # Response
    acknowledged_by = Column(String(100))
    resolved_by = Column(String(100))
    resolution_notes = Column(Text)
    
    # Impact assessment
    affected_services = Column(JSON)
    impact_level = Column(String(20))  # low, medium, high, critical
    user_impact = Column(Text)
    
    # Notification tracking
    notifications_sent = Column(JSON)
    escalation_level = Column(Integer, default=0)
    
    # Context data
    context_data = Column(JSON)  # Metric values, logs, etc. at time of incident
    tags = Column(JSON)
    
    # Relationships
    alert = relationship("Alert", back_populates="incidents")
    
    # Indexes
    __table_args__ = (
        Index('idx_alert_status_time', 'alert_id', 'status', 'triggered_at'),
        Index('idx_triggered_at', 'triggered_at'),
    )
    
    def __repr__(self):
        return f"<AlertIncident(incident_id='{self.incident_id}', status='{self.status}', severity='{self.severity}')>"


class ModelDriftAlert(Base):
    """Specialized alerts for ML model drift detection"""
    __tablename__ = "model_drift_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, nullable=False)  # Reference to ML model
    deployment_id = Column(Integer)  # Reference to deployment
    
    # Drift detection details
    drift_type = Column(String(50), nullable=False)  # data_drift, concept_drift, performance_drift
    drift_metric = Column(String(100), nullable=False)
    drift_score = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    
    # Detection metadata
    detection_method = Column(String(100))  # statistical_test, ks_test, psi, etc.
    sample_size = Column(Integer)
    confidence_level = Column(Float, default=0.95)
    
    # Time periods
    baseline_period_start = Column(DateTime(timezone=True))
    baseline_period_end = Column(DateTime(timezone=True))
    current_period_start = Column(DateTime(timezone=True))
    current_period_end = Column(DateTime(timezone=True))
    
    # Alert details
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    severity = Column(String(20), nullable=False)
    status = Column(String(20), default="open")
    
    # Response actions
    auto_retrain_triggered = Column(Boolean, default=False)
    model_disabled = Column(Boolean, default=False)
    notification_sent = Column(Boolean, default=False)
    
    # Additional context
    feature_drift_details = Column(JSON)  # Per-feature drift scores
    recommendations = Column(JSON)        # Suggested actions
    metadata = Column(JSON)
    
    def __repr__(self):
        return f"<ModelDriftAlert(model_id={self.model_id}, drift_type='{self.drift_type}', score={self.drift_score})>"


class SystemHealth(Base):
    """Overall system health status tracking"""
    __tablename__ = "system_health"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Service identification
    service_name = Column(String(100), nullable=False, index=True)
    component = Column(String(100))  # database, api, ml_pipeline, etc.
    instance_id = Column(String(100))
    
    # Health status
    status = Column(String(20), nullable=False)  # healthy, degraded, unhealthy, unknown
    health_score = Column(Float)  # 0.0 to 1.0
    
    # Check details
    check_type = Column(String(50))  # heartbeat, dependency, resource, custom
    check_timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    response_time_ms = Column(Float)
    
    # Health indicators
    availability = Column(Float)      # Percentage uptime
    error_rate = Column(Float)        # Error rate percentage
    resource_usage = Column(JSON)     # CPU, memory, disk usage
    
    # Dependencies
    dependencies_status = Column(JSON)  # Status of dependent services
    external_services = Column(JSON)   # External service health
    
    # Messages and details
    message = Column(String(500))
    details = Column(JSON)
    
    # Trend indicators
    trend = Column(String(20))  # improving, stable, degrading
    last_incident = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<SystemHealth(service='{self.service_name}', status='{self.status}', score={self.health_score})>"


class PerformanceBaseline(Base):
    """Performance baselines for comparison and alerting"""
    __tablename__ = "performance_baselines"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Baseline identification
    name = Column(String(200), nullable=False)
    metric_name = Column(String(100), nullable=False)
    service = Column(String(50), nullable=False)
    
    # Baseline values
    baseline_value = Column(Float, nullable=False)
    standard_deviation = Column(Float)
    percentile_95 = Column(Float)
    percentile_99 = Column(Float)
    
    # Threshold definitions
    warning_threshold = Column(Float)
    critical_threshold = Column(Float)
    
    # Data period used for baseline
    data_period_start = Column(DateTime(timezone=True), nullable=False)
    data_period_end = Column(DateTime(timezone=True), nullable=False)
    sample_count = Column(Integer)
    
    # Baseline metadata
    calculation_method = Column(String(100))  # mean, median, percentile, etc.
    confidence_level = Column(Float, default=0.95)
    seasonality_adjusted = Column(Boolean, default=False)
    
    # Status and lifecycle
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True))
    
    # Configuration
    baseline_config = Column(JSON)
    
    # Indexes
    __table_args__ = (
        Index('idx_metric_service_active', 'metric_name', 'service', 'is_active'),
    )
    
    def __repr__(self):
        return f"<PerformanceBaseline(name='{self.name}', metric='{self.metric_name}', value={self.baseline_value})>"


class SLADefinition(Base):
    """Service Level Agreement definitions and tracking"""
    __tablename__ = "sla_definitions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # SLA identification
    name = Column(String(200), nullable=False, unique=True)
    description = Column(Text)
    service = Column(String(100), nullable=False)
    
    # SLA metrics
    metric_type = Column(String(50), nullable=False)  # availability, response_time, error_rate, etc.
    target_value = Column(Float, nullable=False)
    target_unit = Column(String(20))
    
    # Time window
    measurement_window = Column(String(50), nullable=False)  # hourly, daily, weekly, monthly
    evaluation_period = Column(String(50))  # rolling, calendar
    
    # Thresholds
    warning_threshold = Column(Float)
    critical_threshold = Column(Float)
    
    # Business impact
    business_criticality = Column(String(20))  # low, medium, high, critical
    customer_impact = Column(Text)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_by = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Configuration
    sla_config = Column(JSON)
    
    # Relationships
    performance_records = relationship("SLAPerformance", back_populates="sla_definition")
    
    def __repr__(self):
        return f"<SLADefinition(name='{self.name}', service='{self.service}', target={self.target_value})>"


class SLAPerformance(Base):
    """SLA performance tracking and compliance records"""
    __tablename__ = "sla_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    sla_definition_id = Column(Integer, ForeignKey("sla_definitions.id"), nullable=False)
    
    # Performance period
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    period_type = Column(String(20), nullable=False)  # hour, day, week, month
    
    # Performance metrics
    actual_value = Column(Float, nullable=False)
    target_value = Column(Float, nullable=False)
    compliance_percentage = Column(Float)
    
    # Compliance status
    is_compliant = Column(Boolean, nullable=False)
    breach_duration_minutes = Column(Integer, default=0)
    breach_count = Column(Integer, default=0)
    
    # Performance details
    sample_count = Column(Integer)
    min_value = Column(Float)
    max_value = Column(Float)
    average_value = Column(Float)
    standard_deviation = Column(Float)
    
    # Calculated timestamp
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Metadata
    calculation_method = Column(String(100))
    exclusions = Column(JSON)  # Maintenance windows, etc.
    metadata = Column(JSON)
    
    # Relationships
    sla_definition = relationship("SLADefinition", back_populates="performance_records")
    
    # Indexes
    __table_args__ = (
        Index('idx_sla_period', 'sla_definition_id', 'period_start', 'period_end'),
        Index('idx_compliance', 'is_compliant', 'period_start'),
    )
    
    def __repr__(self):
        return f"<SLAPerformance(sla_id={self.sla_definition_id}, compliant={self.is_compliant}, value={self.actual_value})>"
