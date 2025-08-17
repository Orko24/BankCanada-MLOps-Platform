"""
MLflow service that works with both Databricks and local modes
"""

import logging
import mlflow
from typing import Dict, Any, Optional
import os

from config import MLflowConfig, DatabricksConfig

logger = logging.getLogger(__name__)

class MLflowService:
    """Service for MLflow operations that adapts to available infrastructure"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.mode = MLflowConfig.get_mode()
        self.initialized = False
    
    async def initialize(self):
        """Initialize MLflow with appropriate configuration"""
        try:
            # Setup environment
            config = MLflowConfig.setup_environment()
            
            # Set tracking URI
            mlflow.set_tracking_uri(config["tracking_uri"])
            
            if self.mode == "databricks":
                self.logger.info("🎯 MLflow initialized with Databricks backend")
                
                # Set experiment if provided
                from config import settings
                if settings.MLFLOW_EXPERIMENT_ID:
                    try:
                        mlflow.set_experiment(experiment_id=settings.MLFLOW_EXPERIMENT_ID)
                        self.logger.info(f"Using Databricks experiment: {settings.MLFLOW_EXPERIMENT_ID}")
                    except Exception as e:
                        self.logger.warning(f"Could not set Databricks experiment: {e}")
            else:
                self.logger.info("🔧 MLflow initialized with local file backend")
                
                # Create local MLflow directories
                os.makedirs("./mlruns", exist_ok=True)
                os.makedirs("./artifacts", exist_ok=True)
                
                # Create or get default experiment
                try:
                    experiment_name = MLflowConfig.get_experiment_name("economic_forecasting")
                    experiment = mlflow.get_experiment_by_name(experiment_name)
                    if experiment is None:
                        experiment_id = mlflow.create_experiment(
                            name=experiment_name,
                            artifact_location=config["artifact_root"]
                        )
                        self.logger.info(f"Created local experiment: {experiment_name} (ID: {experiment_id})")
                    else:
                        mlflow.set_experiment(experiment_name)
                        self.logger.info(f"Using existing local experiment: {experiment_name}")
                except Exception as e:
                    self.logger.warning(f"Could not setup local experiment: {e}")
            
            self.initialized = True
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize MLflow: {e}")
            return False
    
    async def start_run(self, run_name: Optional[str] = None, nested: bool = False) -> Optional[str]:
        """Start a new MLflow run"""
        try:
            if not self.initialized:
                await self.initialize()
            
            run = mlflow.start_run(run_name=run_name, nested=nested)
            self.logger.info(f"Started MLflow run: {run.info.run_id}")
            return run.info.run_id
            
        except Exception as e:
            self.logger.error(f"Failed to start MLflow run: {e}")
            return None
    
    async def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None):
        """Log metrics to MLflow"""
        try:
            for key, value in metrics.items():
                mlflow.log_metric(key, value, step=step)
            self.logger.debug(f"Logged {len(metrics)} metrics to MLflow")
            
        except Exception as e:
            self.logger.error(f"Failed to log metrics: {e}")
    
    async def log_params(self, params: Dict[str, Any]):
        """Log parameters to MLflow"""
        try:
            mlflow.log_params(params)
            self.logger.debug(f"Logged {len(params)} parameters to MLflow")
            
        except Exception as e:
            self.logger.error(f"Failed to log parameters: {e}")
    
    async def log_model(self, model, artifact_path: str, **kwargs):
        """Log model to MLflow"""
        try:
            # Use appropriate logging method based on model type
            if hasattr(model, 'sklearn'):
                mlflow.sklearn.log_model(model, artifact_path, **kwargs)
            else:
                # Generic Python model logging
                mlflow.pyfunc.log_model(artifact_path, python_model=model, **kwargs)
            
            self.logger.info(f"Logged model to artifact path: {artifact_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to log model: {e}")
    
    async def get_experiment_info(self) -> Dict[str, Any]:
        """Get information about current MLflow setup"""
        try:
            current_experiment = mlflow.get_experiment(mlflow.get_experiment(0).experiment_id)
            
            return {
                "mode": self.mode,
                "tracking_uri": mlflow.get_tracking_uri(),
                "experiment_id": current_experiment.experiment_id if current_experiment else None,
                "experiment_name": current_experiment.name if current_experiment else None,
                "artifact_location": current_experiment.artifact_location if current_experiment else None,
                "databricks_configured": DatabricksConfig.is_configured(),
                "initialized": self.initialized
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get experiment info: {e}")
            return {"error": str(e), "mode": self.mode}
    
    def end_run(self, status: str = "FINISHED"):
        """End the current MLflow run"""
        try:
            mlflow.end_run(status=status)
            self.logger.debug("Ended MLflow run")
            
        except Exception as e:
            self.logger.error(f"Failed to end MLflow run: {e}")

# Global MLflow service instance
mlflow_service = MLflowService()
