# Bank of Canada MLOps - Azure Deployment Script
# Clean PowerShell version

$RESOURCE_GROUP = "bankcanada-demo-rg"
$LOCATION = "canadacentral"
$ACR_NAME = "bankcanadademo"
$AKS_NAME = "bankcanada-aks"
$NAMESPACE = "mlops-production"

Write-Host "🏦 Bank of Canada MLOps - Azure Deployment" -ForegroundColor Green
Write-Host "==========================================="

# Check Azure CLI
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Azure CLI not found!" -ForegroundColor Red
    exit 1
}

# Login to Azure
Write-Host "🔐 Logging into Azure..." -ForegroundColor Yellow
az login

# Create Resource Group
Write-Host "📦 Creating resource group..." -ForegroundColor Yellow
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Container Registry
Write-Host "🐳 Creating Azure Container Registry..." -ForegroundColor Yellow
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true

# Get ACR server
$ACR_SERVER = az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query loginServer --output tsv
Write-Host "📍 ACR Server: $ACR_SERVER" -ForegroundColor Cyan

# Build Docker images
Write-Host "🔨 Building Docker images..." -ForegroundColor Yellow
docker build -t "$ACR_SERVER/bankcanada-api:latest" ./api/
docker build -t "$ACR_SERVER/bankcanada-web:latest" ./web/

# Login to ACR and push
Write-Host "🔐 Logging into Container Registry..." -ForegroundColor Yellow
az acr login --name $ACR_NAME

Write-Host "⬆️ Pushing images..." -ForegroundColor Yellow
docker push "$ACR_SERVER/bankcanada-api:latest"
docker push "$ACR_SERVER/bankcanada-web:latest"

# Create AKS cluster
Write-Host "☸️ Creating AKS cluster..." -ForegroundColor Yellow
az aks create --resource-group $RESOURCE_GROUP --name $AKS_NAME --node-count 3 --node-vm-size Standard_D2s_v3 --attach-acr $ACR_NAME --enable-managed-identity --generate-ssh-keys

# Get AKS credentials
Write-Host "🔑 Getting AKS credentials..." -ForegroundColor Yellow
az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_NAME

# Create namespace
Write-Host "📁 Creating Kubernetes namespace..." -ForegroundColor Yellow
kubectl apply -f azure/kubernetes/namespace.yaml

# Update deployment manifest
Write-Host "🔄 Updating deployment manifest..." -ForegroundColor Yellow
$deploymentContent = Get-Content azure/kubernetes/api-deployment.yaml -Raw
$deploymentContent = $deploymentContent -replace "bankcanadamlops.azurecr.io", $ACR_SERVER
Set-Content azure/kubernetes/api-deployment.yaml $deploymentContent

# Deploy application
Write-Host "🚀 Deploying application..." -ForegroundColor Green
kubectl apply -f azure/kubernetes/api-deployment.yaml
kubectl apply -f azure/kubernetes/api-service.yaml
kubectl apply -f azure/kubernetes/api-ingress.yaml

# Wait for deployment
Write-Host "⏳ Waiting for deployment..." -ForegroundColor Yellow
kubectl wait --for=condition=available --timeout=300s deployment/bankcanada-api -n $NAMESPACE

# Get service info
Write-Host "📊 Getting service information..." -ForegroundColor Cyan
kubectl get services -n $NAMESPACE
kubectl get pods -n $NAMESPACE

Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "🎯 Your MLOps platform is ready!" -ForegroundColor Green
