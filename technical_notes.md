# Azure, Databricks & MLflow Technical Interview Guide

## 🔵 AZURE FUNDAMENTALS

### Core Azure Services

#### **Azure Resource Groups**
- Logical containers for Azure resources
- All resources must belong to exactly one resource group
- Used for access control, billing, and lifecycle management
- Best practice: Group resources by environment (dev/staging/prod) or application

#### **Azure Virtual Networks (VNet)**
- Private network in Azure cloud
- Enables secure communication between Azure resources
- Supports subnets, network security groups (NSGs)
- Required for AKS clusters and secure Databricks deployments

#### **Azure Storage Account**
- Blob Storage: Object storage for unstructured data (files, images, backups)
- Table Storage: NoSQL key-value store
- Queue Storage: Message queuing service
- File Storage: Managed file shares

#### **Azure Key Vault**
- Centralized secrets management
- Store API keys, connection strings, certificates
- Integration with all Azure services
- Hardware Security Module (HSM) backing available

### Azure AI/ML Services

#### **Azure Machine Learning**
- End-to-end ML lifecycle management
- Automated ML (AutoML) capabilities
- Model deployment and monitoring
- Integration with popular ML frameworks
- Compute instances and clusters for training

#### **Azure Cognitive Services**
- Pre-built AI models as APIs
- Computer Vision, Speech, Language, Decision services
- No ML expertise required for common AI tasks
- Pay-per-use pricing model

#### **Azure OpenAI Service**
- Access to OpenAI models (GPT-4, DALL-E, Codex)
- Enterprise-grade security and compliance
- Fine-tuning capabilities
- Integration with Azure ecosystem

### Azure DevOps & CI/CD

#### **Azure DevOps Services**
- **Azure Repos**: Git repositories with branch policies
- **Azure Pipelines**: CI/CD pipelines with YAML or classic editor
- **Azure Boards**: Work item tracking and project management
- **Azure Test Plans**: Manual and automated testing
- **Azure Artifacts**: Package management

#### **Azure Pipelines Key Concepts**
```yaml
# Example pipeline structure
trigger:
  branches:
    include:
    - main

stages:
- stage: Build
  jobs:
  - job: BuildJob
    steps:
    - task: UsePythonVersion@0
    - script: pip install -r requirements.txt
    - task: PublishTestResults@2

- stage: Deploy
  dependsOn: Build
  jobs:
  - deployment: DeployJob
    environment: 'production'
```

#### **Azure Functions**
- Serverless compute service
- Event-driven execution
- Multiple triggers: HTTP, Timer, Blob, Queue, Event Hub
- Consumption, Premium, and Dedicated hosting plans
- Perfect for ML model inference endpoints

### Azure Security & Compliance

#### **Azure Active Directory (Azure AD)**
- Identity and access management service
- Single sign-on (SSO) capabilities
- Multi-factor authentication (MFA)
- Role-based access control (RBAC)

#### **Azure RBAC Roles**
- **Reader**: View resources only
- **Contributor**: Manage resources (no access management)
- **Owner**: Full access including access management
- Custom roles for specific needs

---

## ⚓ AZURE KUBERNETES SERVICE (AKS)

### AKS Fundamentals

#### **What is AKS?**
- Managed Kubernetes service in Azure
- Azure handles master nodes (control plane)
- You manage worker nodes and applications
- Automatic updates and scaling capabilities

#### **Key AKS Components**
- **Cluster**: Complete Kubernetes environment
- **Node Pool**: Group of VMs with same configuration
- **Pod**: Smallest deployable unit (one or more containers)
- **Service**: Network endpoint for pod access
- **Ingress**: HTTP/HTTPS routing to services

### AKS Architecture

#### **Control Plane (Azure Managed)**
- API Server: Kubernetes API endpoint
- etcd: Key-value store for cluster state
- Scheduler: Assigns pods to nodes
- Controller Manager: Manages cluster state

#### **Worker Nodes (Your Responsibility)**
- kubelet: Node agent communicating with control plane
- kube-proxy: Network proxy for services
- Container Runtime: Docker or containerd

### AKS Networking

#### **Network Models**
- **Kubenet**: Basic networking, Azure manages routing
- **Azure CNI**: Advanced networking, pods get VNet IPs
- **Azure CNI Overlay**: Hybrid approach for IP conservation

#### **Load Balancing**
- **Azure Load Balancer**: Layer 4 load balancing
- **Application Gateway**: Layer 7 with WAF capabilities
- **Ingress Controllers**: NGINX, Application Gateway Ingress Controller

### AKS Security

#### **Authentication & Authorization**
- Azure AD integration for cluster access
- Kubernetes RBAC for fine-grained permissions
- Pod Security Standards for runtime security

#### **Network Security**
- Network Security Groups (NSGs)
- Azure Firewall for egress filtering
- Private clusters (no public API endpoint)

### AKS for ML Workloads

#### **GPU Node Pools**
```bash
# Create GPU-enabled node pool
az aks nodepool add \
    --resource-group myResourceGroup \
    --cluster-name myAKSCluster \
    --name gpunodepool \
    --node-count 1 \
    --node-vm-size Standard_NC6s_v3 \
    --enable-cluster-autoscaler \
    --min-count 1 \
    --max-count 3
```

#### **ML Deployment Patterns**
- **Batch Jobs**: Kubernetes Jobs for training
- **Real-time Inference**: Deployments with autoscaling
- **Model Serving**: Multiple models with canary deployments

---

## 🧱 DATABRICKS COMPREHENSIVE GUIDE

### Databricks Architecture

#### **Core Components**
- **Control Plane**: Databricks-managed services (web UI, job scheduler, notebook server)
- **Data Plane**: Your cloud account (compute, storage)
- **Workspace**: Collaborative environment for teams
- **Clusters**: Managed Spark clusters for computation

#### **Databricks Runtime**
- Optimized Apache Spark distribution
- Pre-installed libraries (ML, deep learning, visualization)
- Delta Lake included by default
- Automatic optimization features

### Databricks Compute

#### **Cluster Types**
- **All-Purpose Clusters**: Interactive development and ad-hoc analysis
- **Job Clusters**: Automated workloads, automatically terminated
- **SQL Warehouses**: Optimized for SQL analytics
- **Machine Learning Clusters**: Pre-configured for ML workloads

#### **Autoscaling & Optimization**
- **Cluster Autoscaling**: Automatic worker node adjustment
- **Auto Termination**: Automatic cluster shutdown when idle
- **Spot Instances**: Cost optimization with preemptible VMs
- **Photon Engine**: Vectorized query engine for 2-5x speedup

### Delta Lake

#### **What is Delta Lake?**
- Open-source storage layer for data lakes
- ACID transactions on data lakes
- Schema enforcement and evolution
- Time travel (data versioning)
- Unified batch and streaming

#### **Key Features**
```python
# Schema enforcement
df.write.format("delta").option("mergeSchema", "true").save("/path/to/table")

# Time travel
df = spark.read.format("delta").option("timestampAsOf", "2023-01-01").load("/path/to/table")
df = spark.read.format("delta").option("versionAsOf", "1").load("/path/to/table")

# MERGE operations (upserts)
from delta.tables import DeltaTable
deltaTable = DeltaTable.forPath(spark, "/path/to/table")
deltaTable.alias("target").merge(
    source.alias("source"),
    "target.id = source.id"
).whenMatchedUpdate(set = {"value": "source.value"}).execute()
```

### Databricks Notebooks

#### **Notebook Features**
- **Multiple Languages**: Python, Scala, SQL, R in same notebook
- **Magic Commands**: `%sql`, `%python`, `%scala`, `%r`, `%sh`
- **Visualization**: Built-in charts and graphs
- **Collaboration**: Real-time collaboration, comments, version control

#### **Advanced Notebook Patterns**
```python
# Parameterized notebooks
dbutils.widgets.text("database", "default", "Database name")
database = dbutils.widgets.get("database")

# Cross-language data sharing
# Python cell
temp_df = spark.createDataFrame([(1, "John"), (2, "Jane")], ["id", "name"])
temp_df.createOrReplaceTempView("temp_table")

# SQL cell
%sql
SELECT * FROM temp_table WHERE id = 1
```

### Databricks Jobs & Workflows

#### **Job Types**
- **Notebook Jobs**: Execute notebooks with parameters
- **JAR Jobs**: Run Scala/Java applications
- **Python Wheel Jobs**: Run Python packages
- **Delta Live Tables**: Declarative ETL pipelines

#### **Workflow Orchestration**
```json
{
  "name": "ML_Pipeline",
  "tasks": [
    {
      "task_key": "data_prep",
      "notebook_task": {
        "notebook_path": "/Shared/data_preparation",
        "base_parameters": {"input_path": "/data/raw"}
      }
    },
    {
      "task_key": "model_training",
      "depends_on": [{"task_key": "data_prep"}],
      "notebook_task": {
        "notebook_path": "/Shared/model_training"
      }
    }
  ]
}
```

### Databricks SQL

#### **SQL Warehouses**
- Serverless or classic SQL warehouses
- Auto-scaling and auto-suspend
- BI tool integration (Power BI, Tableau)
- Query history and performance optimization

#### **Advanced SQL Features**
```sql
-- Delta Lake specific functions
SELECT * FROM table_name VERSION AS OF 1;
SELECT * FROM table_name TIMESTAMP AS OF '2023-01-01';

-- Optimization commands
OPTIMIZE table_name;
OPTIMIZE table_name ZORDER BY (column1, column2);

-- Vacuum old files
VACUUM table_name RETAIN 168 HOURS;
```

### Databricks Security

#### **Access Control**
- **Workspace Access Control**: User and group permissions
- **Table Access Control**: Fine-grained data permissions
- **Cluster Access Control**: Who can use which clusters
- **Secret Management**: Integration with Azure Key Vault

#### **Data Governance**
- **Unity Catalog**: Centralized metadata and governance
- **Lineage Tracking**: Data and ML model lineage
- **Audit Logging**: Comprehensive activity logging
- **Compliance**: GDPR, HIPAA, SOX support

---

## 🤖 MLFLOW COMPREHENSIVE GUIDE

### MLflow Components

#### **MLflow Tracking**
- **Experiments**: Group related runs
- **Runs**: Individual model training execution
- **Metrics**: Numerical values (accuracy, loss)
- **Parameters**: Input values (learning_rate, batch_size)
- **Artifacts**: Files (models, plots, data)

```python
import mlflow
import mlflow.sklearn

# Start MLflow run
with mlflow.start_run():
    # Log parameters
    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("max_depth", 6)
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, max_depth=6)
    model.fit(X_train, y_train)
    
    # Log metrics
    accuracy = model.score(X_test, y_test)
    mlflow.log_metric("accuracy", accuracy)
    
    # Log model
    mlflow.sklearn.log_model(model, "random_forest_model")
```

#### **MLflow Projects**
- Packaging ML code for reproducible runs
- Conda/Docker environment specification
- Parameters and entry points definition

```yaml
# MLproject file
name: my_project
conda_env: conda.yaml

entry_points:
  main:
    parameters:
      alpha: {type: float, default: 0.5}
      l1_ratio: {type: float, default: 0.1}
    command: "python train.py --alpha {alpha} --l1-ratio {l1_ratio}"
```

#### **MLflow Models**
- Standard format for ML models
- Multiple "flavors" (sklearn, pytorch, tensorflow)
- Local and remote deployment options

```python
# Register model
mlflow.register_model(
    model_uri="runs:/{}/model".format(run_id),
    name="ProductionModel"
)

# Load model for inference
model = mlflow.pyfunc.load_model(
    model_uri="models:/ProductionModel/1"
)
predictions = model.predict(new_data)
```

#### **MLflow Model Registry**
- Centralized model repository
- Model versioning and stage management
- Model annotations and descriptions

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Transition model to production
client.transition_model_version_stage(
    name="ProductionModel",
    version=1,
    stage="Production"
)

# Add model description
client.update_model_version(
    name="ProductionModel",
    version=1,
    description="Random Forest model with 95% accuracy"
)
```

### MLflow in Databricks

#### **Managed MLflow**
- Automatic experiment tracking
- Integrated with Databricks notebooks
- Centralized model registry
- Enterprise security and access control

#### **AutoML Integration**
```python
from databricks import automl

# Automatic ML with MLflow tracking
summary = automl.classify(
    dataset=df,
    target_col="target",
    timeout_minutes=30
)

# Best model automatically logged to MLflow
best_trial = summary.best_trial
model_uri = best_trial.model_path
```

### Advanced MLflow Patterns

#### **Model Monitoring & Drift Detection**
```python
import mlflow
from evidently.dashboard import Dashboard
from evidently.tabs import DataDriftTab

# Log baseline data
with mlflow.start_run():
    mlflow.log_artifact("baseline_data.csv")
    
    # Create drift report
    drift_dashboard = Dashboard(tabs=[DataDriftTab()])
    drift_dashboard.calculate(reference_data, current_data)
    drift_dashboard.save("drift_report.html")
    
    mlflow.log_artifact("drift_report.html")
```

#### **A/B Testing Framework**
```python
# Model A/B testing
def get_model_for_experiment(user_id):
    if hash(user_id) % 2 == 0:
        return mlflow.pyfunc.load_model("models:/ModelA/Production")
    else:
        return mlflow.pyfunc.load_model("models:/ModelB/Production")

# Log experiment results
with mlflow.start_run(experiment_id="ab_test_experiment"):
    mlflow.log_metric("conversion_rate_a", 0.12)
    mlflow.log_metric("conversion_rate_b", 0.15)
    mlflow.log_metric("p_value", 0.03)
```

---

## 🎯 INTERVIEW-SPECIFIC TECHNICAL SCENARIOS

### Bank of Canada Use Cases

#### **Economic Forecasting Pipeline**
```python
# Databricks notebook workflow
import mlflow
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import RandomForestRegressor

# 1. Data ingestion from multiple sources
economic_data = (spark.read
                 .format("delta")
                 .load("/mnt/economic_indicators")
                 .filter("date >= '2020-01-01'"))

# 2. Feature engineering
assembler = VectorAssembler(
    inputCols=["gdp_growth", "unemployment", "inflation"],
    outputCol="features"
)

# 3. Model training with MLflow
with mlflow.start_run():
    rf = RandomForestRegressor(featuresCol="features", labelCol="interest_rate")
    model = rf.fit(features_df)
    
    # Log model and metrics
    mlflow.spark.log_model(model, "interest_rate_model")
    mlflow.log_metric("rmse", evaluator.evaluate(predictions))
```

#### **Real-time Model Serving on AKS**
```yaml
# Kubernetes deployment for model serving
apiVersion: apps/v1
kind: Deployment
metadata:
  name: economic-model-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: economic-model
  template:
    metadata:
      labels:
        app: economic-model
    spec:
      containers:
      - name: model-server
        image: myregistry.azurecr.io/economic-model:latest
        ports:
        - containerPort: 8080
        env:
        - name: MLFLOW_TRACKING_URI
          value: "https://databricks-instance.cloud.databricks.com"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1"
```

#### **Automated Model Retraining Pipeline**
```yaml
# Azure DevOps pipeline for MLOps
trigger:
  schedules:
  - cron: "0 2 * * 1"  # Weekly on Monday 2 AM
    displayName: Weekly model retraining
    branches:
      include:
      - main

stages:
- stage: DataValidation
  jobs:
  - job: ValidateData
    steps:
    - task: AzureCLI@2
      inputs:
        azureSubscription: 'databricks-connection'
        scriptType: 'bash'
        scriptLocation: 'inlineScript'
        inlineScript: |
          databricks jobs run-now --job-id 123  # Data quality job

- stage: ModelTraining
  dependsOn: DataValidation
  jobs:
  - job: TrainModel
    steps:
    - task: AzureCLI@2
      inputs:
        scriptLocation: 'inlineScript'
        inlineScript: |
          # Trigger Databricks job for model training
          run_id=$(databricks jobs run-now --job-id 456 --notebook-params '{"retrain": "true"}')
          echo "Training job started: $run_id"

- stage: ModelValidation
  dependsOn: ModelTraining
  jobs:
  - job: ValidateModel
    steps:
    - script: |
        # Model validation logic
        python validate_model.py --model-version latest
```

### Common Interview Questions & Answers

#### **"How would you implement model drift detection?"**
```python
# Comprehensive drift detection
import mlflow
from evidently.dashboard import Dashboard
from evidently.tabs import DataDriftTab, CatTargetDriftTab

def detect_model_drift(reference_data, current_data, model_name):
    with mlflow.start_run():
        # Data drift detection
        drift_report = Dashboard(tabs=[DataDriftTab()])
        drift_report.calculate(reference_data, current_data)
        
        # Model performance drift
        model = mlflow.pyfunc.load_model(f"models:/{model_name}/Production")
        current_predictions = model.predict(current_data)
        
        # Log drift metrics
        drift_score = calculate_drift_score(reference_data, current_data)
        mlflow.log_metric("data_drift_score", drift_score)
        
        # Trigger retraining if drift detected
        if drift_score > 0.3:
            trigger_retraining_pipeline(model_name)
```

#### **"How do you ensure security in your ML pipeline?"**
- **Data Encryption**: At rest (Delta Lake) and in transit (TLS)
- **Access Control**: Azure AD integration with Databricks
- **Secret Management**: Azure Key Vault for credentials
- **Network Security**: Private endpoints, NSGs, VNet integration
- **Audit Logging**: Complete audit trail in Azure Monitor
- **Code Security**: DevSecOps with automated security scanning

#### **"Explain your MLOps maturity model"**
**Level 0**: Manual, script-driven process
**Level 1**: ML pipeline automation
**Level 2**: CI/CD pipeline automation
**Level 3**: Automated model monitoring and retraining

---

## 🔑 KEY INTERVIEW TALKING POINTS

### Architecture Decisions
- **Why Databricks over EMR?** Better integration with Azure, managed MLflow, collaborative notebooks
- **Why AKS over Azure Container Instances?** Better scaling, networking control, enterprise features
- **Why Delta Lake over Parquet?** ACID transactions, schema evolution, time travel

### Performance Optimization
- **Databricks**: Photon engine, Delta optimization, cluster autoscaling
- **AKS**: Horizontal Pod Autoscaler, Vertical Pod Autoscaler, node pool scaling
- **MLflow**: Model artifact compression, lazy loading, caching strategies

### Cost Management
- **Spot instances** for non-critical workloads
- **Auto-termination** for idle clusters
- **Reserved instances** for predictable workloads
- **Resource quotas** and **budgets** for cost control

### Disaster Recovery
- **Multi-region** deployments
- **Automated backups** for Delta tables
- **GitOps** for infrastructure and model versioning
- **Blue-green deployments** for zero-downtime updates