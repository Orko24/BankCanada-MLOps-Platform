"""
Configuration management for Bank of Canada MLOps Platform
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings with validation"""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    TESTING: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql://admin:pass@localhost:5432/bankcanada_mlops"
    REDIS_URL: str = "redis://localhost:6379"
    
    # Databricks Configuration
    DATABRICKS_HOST: Optional[str] = None
    DATABRICKS_TOKEN: Optional[str] = None  
    DATABRICKS_SQL_WAREHOUSE_ID: Optional[str] = None
    DATABRICKS_CREDIT_THRESHOLD: float = 80.0
    DATABRICKS_WORKSPACE_URL: Optional[str] = None
    
    # MLflow - Updated for Databricks integration
    MLFLOW_TRACKING_URI: str = "databricks"  # Changed from local to databricks
    MLFLOW_EXPERIMENT_ID: Optional[str] = None
    MLFLOW_BACKEND_STORE_URI: str = "postgresql://admin:pass@localhost:5432/bankcanada_mlops"
    MLFLOW_DEFAULT_ARTIFACT_ROOT: str = "./artifacts"
    
    # Azure Configuration
    AZURE_CLIENT_ID: Optional[str] = None
    AZURE_CLIENT_SECRET: Optional[str] = None
    AZURE_TENANT_ID: Optional[str] = None
    AZURE_SUBSCRIPTION_ID: Optional[str] = None
    AZURE_RESOURCE_GROUP: str = "bankcanada-mlops-rg"
    AZURE_ML_WORKSPACE: str = "bankcanada-ml-workspace"
    AZURE_STORAGE_ACCOUNT: Optional[str] = None
    AZURE_CONTAINER_NAME: str = "economic-data"
    
    # API Keys
    DEEPSEEK_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # Bank of Canada API
    BANK_CANADA_API_URL: str = "https://www.bankofcanada.ca/valet/"
    BANK_CANADA_API_KEY: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    PROMETHEUS_PORT: int = 9090
    GRAFANA_PORT: int = 3001
    
    # Email Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # Model Configuration
    DEFAULT_MODEL_REGISTRY: str = "mlflow"
    MODEL_SERVING_TIMEOUT: int = 30
    BATCH_PREDICTION_SIZE: int = 1000
    
    # Economic Data Settings
    DATA_UPDATE_INTERVAL_HOURS: int = 6
    HISTORICAL_DATA_YEARS: int = 10
    ECONOMIC_INDICATORS: list = [
        "inflation_rate",
        "unemployment_rate", 
        "gdp_growth",
        "interest_rate",
        "exchange_rate_usd",
        "consumer_price_index",
        "housing_price_index"
    ]
    
    # AI Agent Configuration
    MAX_AGENT_RESPONSE_TOKENS: int = 4000
    AGENT_TEMPERATURE: float = 0.1
    RAG_CHUNK_SIZE: int = 1000
    RAG_CHUNK_OVERLAP: int = 200
    
    @field_validator('ENVIRONMENT')
    @classmethod
    def validate_environment(cls, v):
        if v not in ['development', 'staging', 'production']:
            raise ValueError('Environment must be development, staging, or production')
        return v
    
    @field_validator('LOG_LEVEL')
    @classmethod
    def validate_log_level(cls, v):
        if v not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            raise ValueError('Invalid log level')
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True


# Global settings instance
settings = Settings()


class DatabaseConfig:
    """Database-specific configuration"""
    
    @staticmethod
    def get_database_url() -> str:
        return settings.DATABASE_URL
    
    @staticmethod
    def get_redis_url() -> str:
        return settings.REDIS_URL
    
    @staticmethod
    def get_connection_params() -> dict:
        return {
            "pool_size": 20,
            "max_overflow": 30,
            "pool_timeout": 30,
            "pool_recycle": 3600,
            "echo": settings.DEBUG
        }


class DatabricksConfig:
    """Databricks-specific configuration"""
    
    @staticmethod
    def get_connection_params() -> dict:
        return {
            "server_hostname": settings.DATABRICKS_HOST,
            "http_path": f"/sql/1.0/warehouses/{settings.DATABRICKS_SQL_WAREHOUSE_ID}",
            "access_token": settings.DATABRICKS_TOKEN
        }
    
    @staticmethod
    def get_workspace_url() -> str:
        return f"https://{settings.DATABRICKS_HOST}" if settings.DATABRICKS_HOST else ""
    
    @staticmethod
    def is_configured() -> bool:
        return all([
            settings.DATABRICKS_HOST,
            settings.DATABRICKS_TOKEN,
            settings.DATABRICKS_SQL_WAREHOUSE_ID
        ])
    
    @staticmethod
    def get_credit_threshold() -> float:
        return settings.DATABRICKS_CREDIT_THRESHOLD


class MLflowConfig:
    """MLflow-specific configuration"""
    
    @staticmethod
    def get_tracking_uri() -> str:
        # Use Databricks if configured, otherwise fallback to local
        if DatabricksConfig.is_configured():
            return "databricks"
        return "http://localhost:5000"
    
    @staticmethod
    def get_artifact_root() -> str:
        return settings.MLFLOW_DEFAULT_ARTIFACT_ROOT
    
    @staticmethod
    def get_experiment_name(model_type: str) -> str:
        return f"bankcanada_{model_type}_models"


class SecurityConfig:
    """Security-specific configuration"""
    
    @staticmethod
    def get_cors_origins() -> list:
        if settings.ENVIRONMENT == "production":
            return ["https://*.bankofcanada.ca"]
        return ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    @staticmethod
    def get_allowed_hosts() -> list:
        if settings.ENVIRONMENT == "production":
            return ["api.bankcanada.ca", "mlops.bankcanada.ca"]
        return ["localhost", "127.0.0.1"]
    
    @staticmethod
    def get_jwt_config() -> dict:
        return {
            "secret_key": settings.SECRET_KEY,
            "algorithm": settings.JWT_ALGORITHM,
            "access_token_expire_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES
        }
