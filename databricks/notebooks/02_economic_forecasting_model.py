# Databricks notebook source
# MAGIC %md
# MAGIC # Economic Forecasting ML Pipeline - Bank of Canada
# MAGIC 
# MAGIC This notebook demonstrates enterprise-grade ML model development for economic forecasting using Bank of Canada indicators.
# MAGIC 
# MAGIC **Key Features:**
# MAGIC - MLflow experiment tracking and model versioning
# MAGIC - Time series forecasting with multiple algorithms
# MAGIC - Automated hyperparameter tuning
# MAGIC - Model validation and backtesting
# MAGIC - Production-ready model deployment

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup and Configuration

# COMMAND ----------

# Import required libraries
import mlflow
import mlflow.sklearn
import mlflow.pytorch
from mlflow.models.signature import infer_signature
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
import xgboost as xgb
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import warnings
warnings.filterwarnings('ignore')

# Setup MLflow
mlflow.set_experiment("/Workspace/BankCanada/Economic_Forecasting")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration Parameters

# COMMAND ----------

# Model configuration
MODEL_CONFIG = {
    "target_indicator": "inflation",  # inflation, unemployment, gdp
    "forecast_horizon": 12,  # months ahead
    "training_window": 60,   # months of historical data
    "validation_split": 0.2,
    "test_split": 0.1,
    "cross_validation_folds": 5
}

# Feature engineering configuration
FEATURE_CONFIG = {
    "lag_features": [1, 3, 6, 12],  # months
    "rolling_windows": [3, 6, 12],  # months
    "seasonal_features": True,
    "economic_indicators": [
        "unemployment", "gdp", "interest_rates", "exchange_rates"
    ]
}

# Model hyperparameters for tuning
HYPERPARAMETER_GRIDS = {
    "random_forest": {
        "n_estimators": [100, 200, 300],
        "max_depth": [10, 20, None],
        "min_samples_split": [2, 5, 10],
        "min_samples_leaf": [1, 2, 4]
    },
    "xgboost": {
        "n_estimators": [100, 200, 300],
        "max_depth": [3, 6, 9],
        "learning_rate": [0.01, 0.1, 0.2],
        "subsample": [0.8, 0.9, 1.0]
    },
    "gradient_boosting": {
        "n_estimators": [100, 200, 300],
        "max_depth": [3, 6, 9],
        "learning_rate": [0.01, 0.1, 0.2]
    }
}

# Performance thresholds
PERFORMANCE_THRESHOLDS = {
    "min_r2": 0.7,
    "max_mae": 0.5,
    "max_rmse": 0.8
}

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Loading and Preparation

# COMMAND ----------

def load_economic_data():
    """
    Load economic data from Delta Lake gold layer
    """
    # Read from gold layer
    gold_df = spark.read.format("delta").load("/mnt/economic-data/delta/gold/economic_analytics")
    
    # Convert to Pandas for ML processing
    pandas_df = gold_df.toPandas()
    
    # Ensure date column is datetime
    pandas_df['date'] = pd.to_datetime(pandas_df['date'])
    
    # Sort by date
    pandas_df = pandas_df.sort_values('date')
    
    return pandas_df

def prepare_time_series_data(df, target_indicator):
    """
    Prepare time series data for modeling
    """
    # Filter for target indicator
    target_df = df[df['indicator_category'] == target_indicator].copy()
    
    # Create time-based features
    target_df['year'] = target_df['date'].dt.year
    target_df['month'] = target_df['date'].dt.month
    target_df['quarter'] = target_df['date'].dt.quarter
    target_df['day_of_year'] = target_df['date'].dt.dayofyear
    
    # Sort by date
    target_df = target_df.sort_values('date').reset_index(drop=True)
    
    return target_df

def create_features(df, config):
    """
    Create features for time series forecasting
    """
    feature_df = df.copy()
    
    # Lag features
    for lag in config['lag_features']:
        feature_df[f'value_lag_{lag}'] = feature_df['value'].shift(lag)
        feature_df[f'yoy_change_lag_{lag}'] = feature_df['year_over_year_change'].shift(lag)
    
    # Rolling window features
    for window in config['rolling_windows']:
        feature_df[f'rolling_mean_{window}'] = feature_df['value'].rolling(window=window).mean()
        feature_df[f'rolling_std_{window}'] = feature_df['value'].rolling(window=window).std()
        feature_df[f'rolling_min_{window}'] = feature_df['value'].rolling(window=window).min()
        feature_df[f'rolling_max_{window}'] = feature_df['value'].rolling(window=window).max()
    
    # Seasonal features
    if config['seasonal_features']:
        feature_df['month_sin'] = np.sin(2 * np.pi * feature_df['month'] / 12)
        feature_df['month_cos'] = np.cos(2 * np.pi * feature_df['month'] / 12)
        feature_df['quarter_sin'] = np.sin(2 * np.pi * feature_df['quarter'] / 4)
        feature_df['quarter_cos'] = np.cos(2 * np.pi * feature_df['quarter'] / 4)
    
    # Economic regime features
    feature_df['value_ma_diff'] = feature_df['value'] - feature_df['rolling_mean_12']
    feature_df['volatility'] = feature_df['rolling_std_12']
    feature_df['momentum'] = feature_df['value'] - feature_df['value_lag_3']
    
    # Remove rows with NaN values (due to lags and rolling windows)
    max_lag = max(config['lag_features'] + config['rolling_windows'])
    feature_df = feature_df.iloc[max_lag:].reset_index(drop=True)
    
    return feature_df

def create_forecast_target(df, horizon):
    """
    Create forecast target variable
    """
    df = df.copy()
    df['target'] = df['value'].shift(-horizon)
    
    # Remove rows where target is NaN
    df = df[:-horizon]
    
    return df

# Load and prepare data
print("Loading economic data...")
raw_data = load_economic_data()
print(f"Loaded {len(raw_data)} records across {raw_data['indicator_category'].nunique()} indicators")

# Prepare target indicator data
target_data = prepare_time_series_data(raw_data, MODEL_CONFIG['target_indicator'])
print(f"Prepared {len(target_data)} records for {MODEL_CONFIG['target_indicator']} indicator")

# Create features
feature_data = create_features(target_data, FEATURE_CONFIG)
print(f"Created features, resulting in {len(feature_data)} usable records")

# Create forecast targets
model_data = create_forecast_target(feature_data, MODEL_CONFIG['forecast_horizon'])
print(f"Final modeling dataset: {len(model_data)} records")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Feature Selection and Data Splitting

# COMMAND ----------

def select_features(df):
    """
    Select relevant features for modeling
    """
    # Define feature columns (exclude metadata and target)
    exclude_cols = [
        'date', 'indicator_category', 'indicator_name', 'unit', 
        'frequency', 'seasonally_adjusted', 'last_updated', 'target'
    ]
    
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    # Remove features with too many missing values
    missing_threshold = 0.1
    valid_features = []
    
    for col in feature_cols:
        missing_pct = df[col].isnull().sum() / len(df)
        if missing_pct <= missing_threshold:
            valid_features.append(col)
        else:
            print(f"Removing feature {col} due to {missing_pct:.2%} missing values")
    
    return valid_features

def split_time_series_data(df, features, target_col, config):
    """
    Split time series data maintaining temporal order
    """
    # Sort by date
    df = df.sort_values('date')
    
    # Calculate split indices
    total_samples = len(df)
    train_end = int(total_samples * (1 - config['validation_split'] - config['test_split']))
    val_end = int(total_samples * (1 - config['test_split']))
    
    # Split data
    train_df = df.iloc[:train_end]
    val_df = df.iloc[train_end:val_end]
    test_df = df.iloc[val_end:]
    
    # Extract features and targets
    X_train = train_df[features].fillna(method='ffill').fillna(method='bfill')
    y_train = train_df[target_col]
    
    X_val = val_df[features].fillna(method='ffill').fillna(method='bfill')
    y_val = val_df[target_col]
    
    X_test = test_df[features].fillna(method='ffill').fillna(method='bfill')
    y_test = test_df[target_col]
    
    return (X_train, y_train), (X_val, y_val), (X_test, y_test)

# Select features
selected_features = select_features(model_data)
print(f"Selected {len(selected_features)} features for modeling")
print("Features:", selected_features[:10], "..." if len(selected_features) > 10 else "")

# Split data
(X_train, y_train), (X_val, y_val), (X_test, y_test) = split_time_series_data(
    model_data, selected_features, 'target', MODEL_CONFIG
)

print(f"Training set: {X_train.shape}")
print(f"Validation set: {X_val.shape}")
print(f"Test set: {X_test.shape}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Model Training and Hyperparameter Tuning

# COMMAND ----------

def evaluate_model(y_true, y_pred, model_name):
    """
    Calculate model performance metrics
    """
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_true, y_pred)
    
    # Calculate directional accuracy
    y_true_diff = np.diff(y_true)
    y_pred_diff = np.diff(y_pred)
    directional_accuracy = np.mean(np.sign(y_true_diff) == np.sign(y_pred_diff))
    
    metrics = {
        'model_name': model_name,
        'mae': mae,
        'mse': mse,
        'rmse': rmse,
        'r2': r2,
        'directional_accuracy': directional_accuracy
    }
    
    return metrics

def train_random_forest(X_train, y_train, X_val, y_val, hyperparams):
    """
    Train Random Forest with hyperparameter tuning
    """
    with mlflow.start_run(nested=True, run_name="RandomForest_HPTuning"):
        # Time series cross-validation
        tscv = TimeSeriesSplit(n_splits=MODEL_CONFIG['cross_validation_folds'])
        
        rf = RandomForestRegressor(random_state=42, n_jobs=-1)
        grid_search = GridSearchCV(
            rf, hyperparams, cv=tscv, 
            scoring='neg_mean_absolute_error', n_jobs=-1
        )
        
        grid_search.fit(X_train, y_train)
        best_model = grid_search.best_estimator_
        
        # Validate model
        y_pred = best_model.predict(X_val)
        metrics = evaluate_model(y_val, y_pred, "RandomForest")
        
        # Log to MLflow
        mlflow.log_params(grid_search.best_params_)
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(best_model, "model")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': X_train.columns,
            'importance': best_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        mlflow.log_text(feature_importance.to_string(), "feature_importance.txt")
        
        return best_model, metrics

def train_xgboost(X_train, y_train, X_val, y_val, hyperparams):
    """
    Train XGBoost with hyperparameter tuning
    """
    with mlflow.start_run(nested=True, run_name="XGBoost_HPTuning"):
        # Time series cross-validation
        tscv = TimeSeriesSplit(n_splits=MODEL_CONFIG['cross_validation_folds'])
        
        xgb_model = xgb.XGBRegressor(random_state=42, n_jobs=-1)
        grid_search = GridSearchCV(
            xgb_model, hyperparams, cv=tscv,
            scoring='neg_mean_absolute_error', n_jobs=-1
        )
        
        grid_search.fit(X_train, y_train)
        best_model = grid_search.best_estimator_
        
        # Validate model
        y_pred = best_model.predict(X_val)
        metrics = evaluate_model(y_val, y_pred, "XGBoost")
        
        # Log to MLflow
        mlflow.log_params(grid_search.best_params_)
        mlflow.log_metrics(metrics)
        mlflow.xgboost.log_model(best_model, "model")
        
        return best_model, metrics

def train_gradient_boosting(X_train, y_train, X_val, y_val, hyperparams):
    """
    Train Gradient Boosting with hyperparameter tuning
    """
    with mlflow.start_run(nested=True, run_name="GradientBoosting_HPTuning"):
        # Time series cross-validation
        tscv = TimeSeriesSplit(n_splits=MODEL_CONFIG['cross_validation_folds'])
        
        gb_model = GradientBoostingRegressor(random_state=42)
        grid_search = GridSearchCV(
            gb_model, hyperparams, cv=tscv,
            scoring='neg_mean_absolute_error', n_jobs=-1
        )
        
        grid_search.fit(X_train, y_train)
        best_model = grid_search.best_estimator_
        
        # Validate model
        y_pred = best_model.predict(X_val)
        metrics = evaluate_model(y_val, y_pred, "GradientBoosting")
        
        # Log to MLflow
        mlflow.log_params(grid_search.best_params_)
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(best_model, "model")
        
        return best_model, metrics

# Train models with hyperparameter tuning
print("Starting model training and hyperparameter tuning...")

trained_models = {}
model_metrics = []

# Train Random Forest
print("Training Random Forest...")
rf_model, rf_metrics = train_random_forest(
    X_train, y_train, X_val, y_val, 
    HYPERPARAMETER_GRIDS['random_forest']
)
trained_models['random_forest'] = rf_model
model_metrics.append(rf_metrics)

# Train XGBoost
print("Training XGBoost...")
xgb_model, xgb_metrics = train_xgboost(
    X_train, y_train, X_val, y_val,
    HYPERPARAMETER_GRIDS['xgboost']
)
trained_models['xgboost'] = xgb_model
model_metrics.append(xgb_metrics)

# Train Gradient Boosting
print("Training Gradient Boosting...")
gb_model, gb_metrics = train_gradient_boosting(
    X_train, y_train, X_val, y_val,
    HYPERPARAMETER_GRIDS['gradient_boosting']
)
trained_models['gradient_boosting'] = gb_model
model_metrics.append(gb_metrics)

# Compare models
metrics_df = pd.DataFrame(model_metrics)
print("\nModel Performance Comparison:")
print(metrics_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Model Selection and Final Evaluation

# COMMAND ----------

def select_best_model(metrics_df, performance_thresholds):
    """
    Select best model based on performance criteria
    """
    # Filter models that meet minimum thresholds
    valid_models = metrics_df[
        (metrics_df['r2'] >= performance_thresholds['min_r2']) &
        (metrics_df['mae'] <= performance_thresholds['max_mae']) &
        (metrics_df['rmse'] <= performance_thresholds['max_rmse'])
    ]
    
    if len(valid_models) == 0:
        print("Warning: No models meet performance thresholds, selecting best available")
        best_model_idx = metrics_df['r2'].idxmax()
    else:
        # Select model with highest R2 among valid models
        best_model_idx = valid_models['r2'].idxmax()
    
    return metrics_df.iloc[best_model_idx]

def perform_backtesting(model, X_data, y_data, features, n_periods=12):
    """
    Perform walk-forward backtesting
    """
    backtest_results = []
    
    for i in range(n_periods):
        # Use expanding window
        train_end = len(X_data) - n_periods + i
        
        X_train_bt = X_data.iloc[:train_end]
        y_train_bt = y_data.iloc[:train_end]
        
        if train_end < len(X_data):
            X_test_bt = X_data.iloc[train_end:train_end+1]
            y_test_bt = y_data.iloc[train_end:train_end+1]
            
            # Retrain model
            model_bt = type(model)(**model.get_params())
            model_bt.fit(X_train_bt, y_train_bt)
            
            # Make prediction
            y_pred_bt = model_bt.predict(X_test_bt)
            
            backtest_results.append({
                'period': i + 1,
                'actual': y_test_bt.iloc[0],
                'predicted': y_pred_bt[0],
                'error': abs(y_test_bt.iloc[0] - y_pred_bt[0])
            })
    
    return pd.DataFrame(backtest_results)

# Select best model
best_model_info = select_best_model(metrics_df, PERFORMANCE_THRESHOLDS)
best_model_name = best_model_info['model_name']
best_model = trained_models[best_model_name.lower().replace(' ', '_')]

print(f"Selected best model: {best_model_name}")
print(f"Performance metrics: R² = {best_model_info['r2']:.4f}, MAE = {best_model_info['mae']:.4f}")

# Final evaluation on test set
with mlflow.start_run(run_name=f"Final_{best_model_name}_Model"):
    # Test set evaluation
    y_test_pred = best_model.predict(X_test)
    test_metrics = evaluate_model(y_test, y_test_pred, f"Final_{best_model_name}")
    
    print(f"\nFinal Test Set Performance:")
    for metric, value in test_metrics.items():
        if metric != 'model_name':
            print(f"{metric}: {value:.4f}")
    
    # Backtesting
    print("\nPerforming backtesting...")
    backtest_df = perform_backtesting(best_model, X_val, y_val, selected_features)
    backtest_mae = backtest_df['error'].mean()
    
    print(f"Backtesting MAE: {backtest_mae:.4f}")
    
    # Log final metrics
    mlflow.log_metrics(test_metrics)
    mlflow.log_metric("backtest_mae", backtest_mae)
    
    # Log model with signature
    signature = infer_signature(X_train, y_train)
    
    if best_model_name == "RandomForest":
        mlflow.sklearn.log_model(best_model, "final_model", signature=signature)
    elif best_model_name == "XGBoost":
        mlflow.xgboost.log_model(best_model, "final_model", signature=signature)
    else:
        mlflow.sklearn.log_model(best_model, "final_model", signature=signature)
    
    # Log artifacts
    mlflow.log_text(str(MODEL_CONFIG), "model_config.txt")
    mlflow.log_text(str(FEATURE_CONFIG), "feature_config.txt")
    
    # Save feature list
    feature_list = '\n'.join(selected_features)
    mlflow.log_text(feature_list, "features.txt")
    
    # Log backtest results
    backtest_df.to_csv("backtest_results.csv", index=False)
    mlflow.log_artifact("backtest_results.csv")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Model Visualization and Analysis

# COMMAND ----------

# Create visualizations
fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# 1. Actual vs Predicted (Test Set)
axes[0, 0].scatter(y_test, y_test_pred, alpha=0.7)
axes[0, 0].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
axes[0, 0].set_xlabel('Actual')
axes[0, 0].set_ylabel('Predicted')
axes[0, 0].set_title('Actual vs Predicted (Test Set)')
axes[0, 0].grid(True)

# 2. Residual Plot
residuals = y_test - y_test_pred
axes[0, 1].scatter(y_test_pred, residuals, alpha=0.7)
axes[0, 1].axhline(y=0, color='r', linestyle='--')
axes[0, 1].set_xlabel('Predicted')
axes[0, 1].set_ylabel('Residuals')
axes[0, 1].set_title('Residual Plot')
axes[0, 1].grid(True)

# 3. Feature Importance (if available)
if hasattr(best_model, 'feature_importances_'):
    feature_importance = pd.DataFrame({
        'feature': selected_features,
        'importance': best_model.feature_importances_
    }).sort_values('importance', ascending=False).head(15)
    
    axes[1, 0].barh(range(len(feature_importance)), feature_importance['importance'])
    axes[1, 0].set_yticks(range(len(feature_importance)))
    axes[1, 0].set_yticklabels(feature_importance['feature'])
    axes[1, 0].set_xlabel('Importance')
    axes[1, 0].set_title('Top 15 Feature Importances')
    axes[1, 0].grid(True)

# 4. Backtesting Results
axes[1, 1].plot(backtest_df['period'], backtest_df['actual'], 'o-', label='Actual', linewidth=2)
axes[1, 1].plot(backtest_df['period'], backtest_df['predicted'], 's-', label='Predicted', linewidth=2)
axes[1, 1].set_xlabel('Backtest Period')
axes[1, 1].set_ylabel('Value')
axes[1, 1].set_title('Backtesting Results')
axes[1, 1].legend()
axes[1, 1].grid(True)

plt.tight_layout()
plt.savefig('model_analysis.png', dpi=300, bbox_inches='tight')
mlflow.log_artifact('model_analysis.png')
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Model Registration and Deployment Preparation

# COMMAND ----------

def register_model_for_production(model_name, model_version, stage="Staging"):
    """
    Register model in MLflow Model Registry
    """
    try:
        # Get the latest run
        experiment = mlflow.get_experiment_by_name("/Workspace/BankCanada/Economic_Forecasting")
        runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id], 
                                 order_by=["start_time DESC"], max_results=1)
        
        if len(runs) > 0:
            run_id = runs.iloc[0]['run_id']
            model_uri = f"runs:/{run_id}/final_model"
            
            # Register model
            registered_model = mlflow.register_model(
                model_uri=model_uri,
                name=model_name,
                tags={
                    "algorithm": best_model_name,
                    "target_indicator": MODEL_CONFIG['target_indicator'],
                    "forecast_horizon": str(MODEL_CONFIG['forecast_horizon']),
                    "performance_r2": str(round(test_metrics['r2'], 4)),
                    "performance_mae": str(round(test_metrics['mae'], 4)),
                    "training_date": datetime.now().strftime("%Y-%m-%d"),
                    "data_version": "v1.0"
                }
            )
            
            print(f"Model registered successfully: {model_name}")
            print(f"Model version: {registered_model.version}")
            
            return registered_model
            
    except Exception as e:
        print(f"Error registering model: {e}")
        return None

# Register the best model
model_name = f"bankcanada_{MODEL_CONFIG['target_indicator']}_forecast"
registered_model = register_model_for_production(model_name, "1")

if registered_model:
    print(f"Model registration successful!")
    print(f"Model name: {registered_model.name}")
    print(f"Version: {registered_model.version}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Model Monitoring Setup

# COMMAND ----------

# Create model monitoring configuration
monitoring_config = {
    "model_name": model_name,
    "model_version": registered_model.version if registered_model else "1",
    "performance_thresholds": PERFORMANCE_THRESHOLDS,
    "monitoring_frequency": "daily",
    "drift_detection": {
        "feature_drift_threshold": 0.1,
        "prediction_drift_threshold": 0.15,
        "performance_degradation_threshold": 0.2
    },
    "alerts": {
        "email_recipients": ["mlops-team@bankcanada.ca"],
        "slack_channel": "#ml-alerts",
        "severity_levels": ["low", "medium", "high", "critical"]
    },
    "retraining_triggers": {
        "performance_degradation": True,
        "data_drift": True,
        "scheduled_interval_days": 30
    }
}

# Save monitoring configuration
import json
with open("monitoring_config.json", "w") as f:
    json.dump(monitoring_config, f, indent=2)

mlflow.log_artifact("monitoring_config.json")

print("Model monitoring configuration created and logged")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Deployment Scripts Generation

# COMMAND ----------

# Generate deployment script
deployment_script = f"""
# Bank of Canada Economic Forecasting Model Deployment Script

import mlflow
import mlflow.sklearn
import pandas as pd
import numpy as np
from datetime import datetime

# Load registered model
model_name = "{model_name}"
model_version = "{registered_model.version if registered_model else '1'}"
model_uri = f"models:/{{model_name}}/{{model_version}}"

# Load model
model = mlflow.sklearn.load_model(model_uri)

# Feature list
FEATURES = {selected_features}

def preprocess_input(input_data):
    \"\"\"
    Preprocess input data for prediction
    \"\"\"
    # Ensure all required features are present
    for feature in FEATURES:
        if feature not in input_data.columns:
            input_data[feature] = 0  # Default value or implement proper handling
    
    # Select only required features in correct order
    processed_data = input_data[FEATURES]
    
    # Handle missing values
    processed_data = processed_data.fillna(method='ffill').fillna(method='bfill')
    
    return processed_data

def make_prediction(input_data):
    \"\"\"
    Make prediction using the deployed model
    \"\"\"
    try:
        # Preprocess input
        processed_input = preprocess_input(input_data)
        
        # Make prediction
        prediction = model.predict(processed_input)
        
        # Get prediction confidence (if available)
        confidence = None
        if hasattr(model, 'predict_proba'):
            # For classifiers
            confidence = np.max(model.predict_proba(processed_input), axis=1)
        elif hasattr(model, 'decision_function'):
            # For some regressors
            confidence = np.abs(model.decision_function(processed_input))
        
        return {{
            "prediction": prediction.tolist(),
            "confidence": confidence.tolist() if confidence is not None else None,
            "model_version": model_version,
            "prediction_timestamp": datetime.now().isoformat()
        }}
        
    except Exception as e:
        return {{
            "error": str(e),
            "prediction_timestamp": datetime.now().isoformat()
        }}

# Example usage
if __name__ == "__main__":
    # Example input data
    example_input = pd.DataFrame({{
        # Add example feature values here
        feature: [0.0] for feature in FEATURES
    }})
    
    result = make_prediction(example_input)
    print("Prediction result:", result)
"""

with open("deployment_script.py", "w") as f:
    f.write(deployment_script)

mlflow.log_artifact("deployment_script.py")

print("Deployment script generated and logged")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Workflow Summary and Results

# COMMAND ----------

# Create comprehensive results summary
results_summary = {
    "experiment_info": {
        "target_indicator": MODEL_CONFIG['target_indicator'],
        "forecast_horizon_months": MODEL_CONFIG['forecast_horizon'],
        "training_samples": len(X_train),
        "validation_samples": len(X_val),
        "test_samples": len(X_test),
        "features_count": len(selected_features)
    },
    "model_performance": {
        "best_model": best_model_name,
        "test_r2": round(test_metrics['r2'], 4),
        "test_mae": round(test_metrics['mae'], 4),
        "test_rmse": round(test_metrics['rmse'], 4),
        "directional_accuracy": round(test_metrics['directional_accuracy'], 4),
        "backtest_mae": round(backtest_mae, 4)
    },
    "model_registration": {
        "model_name": model_name,
        "model_version": registered_model.version if registered_model else "N/A",
        "registration_status": "Success" if registered_model else "Failed"
    },
    "deployment_readiness": {
        "meets_performance_thresholds": all([
            test_metrics['r2'] >= PERFORMANCE_THRESHOLDS['min_r2'],
            test_metrics['mae'] <= PERFORMANCE_THRESHOLDS['max_mae'],
            test_metrics['rmse'] <= PERFORMANCE_THRESHOLDS['max_rmse']
        ]),
        "monitoring_configured": True,
        "deployment_script_generated": True
    },
    "next_steps": [
        "Deploy model to staging environment",
        "Set up automated monitoring pipeline", 
        "Configure prediction API endpoints",
        "Schedule model retraining pipeline",
        "Create business dashboard integration"
    ]
}

print("=" * 80)
print("ECONOMIC FORECASTING MODEL TRAINING - RESULTS SUMMARY")
print("=" * 80)
print(json.dumps(results_summary, indent=2))
print("=" * 80)

# Log final results
mlflow.log_text(json.dumps(results_summary, indent=2), "results_summary.json")

# COMMAND ----------

# Return success status for workflow orchestration
dbutils.notebook.exit(json.dumps({
    "status": "success",
    "message": "Economic forecasting model training completed successfully",
    "model_name": model_name,
    "model_version": registered_model.version if registered_model else "N/A",
    "performance_r2": round(test_metrics['r2'], 4),
    "execution_timestamp": datetime.now().isoformat()
}))
