# Bank of Canada MLOps - Azure Deployment Script (PowerShell)
# Quick deployment for demo/interview purposes

# Configuration
$RESOURCE_GROUP = "bankcanada-demo-rg"
$LOCATION = "canadacentral"
$ACR_NAME = "bankcanadademo"
$AKS_NAME = "bankcanada-aks"
$NAMESPACE = "mlops-production"

Write-Host "🏦 Bank of Canada MLOps - Azure Deployment" -ForegroundColor Green
Write-Host "==========================================="

# Check if Azure CLI is installed
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Azure CLI not found. Please install: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli" -ForegroundColor Red
    exit 1
}

# Login to Azure
Write-Host "🔐 Logging into Azure..." -ForegroundColor Yellow
az login

# Create Resource Group
Write-Host "📦 Creating resource group..." -ForegroundColor Yellow
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure Container Registry
Write-Host "🐳 Creating Azure Container Registry..." -ForegroundColor Yellow
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true

# Get ACR login server
$ACR_SERVER = az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query loginServer --output tsv
Write-Host "📍 ACR Server: $ACR_SERVER" -ForegroundColor Cyan

# Build and push Docker images
Write-Host "🔨 Building and pushing Docker images..." -ForegroundColor Yellow

# Build API image
Write-Host "  📦 Building API image..." -ForegroundColor Blue
docker build -t "$ACR_SERVER/bankcanada-api:latest" ./api/

# Build Web image  
Write-Host "  📦 Building Web image..." -ForegroundColor Blue
docker build -t "$ACR_SERVER/bankcanada-web:latest" ./web/

# Login to ACR
Write-Host "🔐 Logging into Azure Container Registry..." -ForegroundColor Yellow
az acr login --name $ACR_NAME

# Push images
Write-Host "⬆️  Pushing images to ACR..." -ForegroundColor Yellow
docker push "$ACR_SERVER/bankcanada-api:latest"
docker push "$ACR_SERVER/bankcanada-web:latest"

# Create AKS cluster
Write-Host "☸️  Creating AKS cluster..." -ForegroundColor Yellow
az aks create --resource-group $RESOURCE_GROUP --name $AKS_NAME --node-count 3 --node-vm-size Standard_D2s_v3 --attach-acr $ACR_NAME --enable-managed-identity --generate-ssh-keys

# Get AKS credentials
Write-Host "🔑 Getting AKS credentials..." -ForegroundColor Yellow
az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_NAME

# Create namespace
Write-Host "📁 Creating Kubernetes namespace..." -ForegroundColor Yellow
kubectl apply -f azure/kubernetes/namespace.yaml

# Update image references in deployment files
Write-Host "🔄 Updating deployment manifests..." -ForegroundColor Yellow
$deploymentContent = Get-Content azure/kubernetes/api-deployment.yaml -Raw
$deploymentContent = $deploymentContent -replace "bankcanadamlops.azurecr.io", $ACR_SERVER
Set-Content azure/kubernetes/api-deployment.yaml $deploymentContent

# Deploy application
Write-Host "🚀 Deploying application to AKS..." -ForegroundColor Green
kubectl apply -f azure/kubernetes/api-deployment.yaml
kubectl apply -f azure/kubernetes/api-service.yaml
kubectl apply -f azure/kubernetes/api-ingress.yaml

# Wait for deployment
Write-Host "⏳ Waiting for deployment to be ready..." -ForegroundColor Yellow
kubectl wait --for=condition=available --timeout=300s deployment/bankcanada-api -n $NAMESPACE

# Get service details
Write-Host "📊 Getting service information..." -ForegroundColor Cyan
kubectl get services -n $NAMESPACE
kubectl get pods -n $NAMESPACE

# Get external IP
Write-Host "🌐 Getting external access information..." -ForegroundColor Yellow
$EXTERNAL_IP = kubectl get service bankcanada-api-service -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

if ([string]::IsNullOrEmpty($EXTERNAL_IP)) {
    Write-Host "⏳ External IP not yet assigned. Getting service details:" -ForegroundColor Yellow
    kubectl describe service bankcanada-api-service -n $NAMESPACE
} 
else {
    Write-Host "✅ Application deployed successfully!" -ForegroundColor Green
    Write-Host "🔗 API URL: http://$EXTERNAL_IP:8000" -ForegroundColor Cyan
    Write-Host "🔗 Health Check: http://$EXTERNAL_IP:8000/health" -ForegroundColor Cyan
    Write-Host "🔗 API Docs: http://$EXTERNAL_IP:8000/docs" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "📋 Interview Demo Commands:" -ForegroundColor Green
Write-Host "=========================="
Write-Host "kubectl get pods -n $NAMESPACE"
Write-Host "kubectl get services -n $NAMESPACE"  
Write-Host "kubectl logs -f deployment/bankcanada-api -n $NAMESPACE"
Write-Host "kubectl describe deployment bankcanada-api -n $NAMESPACE"
Write-Host ""
Write-Host "🎯 Your cloud-native MLOps platform is ready for the interview!" -ForegroundColor Green
