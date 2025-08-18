#!/bin/bash

# Bank of Canada MLOps - Azure Deployment Script
# Quick deployment for demo/interview purposes

set -e

# Configuration
RESOURCE_GROUP="bankcanada-demo-rg"
LOCATION="canadacentral"
ACR_NAME="bankcanadademo"
AKS_NAME="bankcanada-aks"
NAMESPACE="mlops-production"

echo "🏦 Bank of Canada MLOps - Azure Deployment"
echo "==========================================="

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found. Please install: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Login to Azure
echo "🔐 Logging into Azure..."
az login

# Create Resource Group
echo "📦 Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure Container Registry
echo "🐳 Creating Azure Container Registry..."
az acr create --resource-group $RESOURCE_GROUP \
              --name $ACR_NAME \
              --sku Basic \
              --admin-enabled true

# Get ACR login server
ACR_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query loginServer --output tsv)
echo "📍 ACR Server: $ACR_SERVER"

# Build and push Docker images
echo "🔨 Building and pushing Docker images..."

# Build API image
echo "  📦 Building API image..."
docker build -t $ACR_SERVER/bankcanada-api:latest ./api/

# Build Web image  
echo "  📦 Building Web image..."
docker build -t $ACR_SERVER/bankcanada-web:latest ./web/

# Login to ACR
echo "🔐 Logging into Azure Container Registry..."
az acr login --name $ACR_NAME

# Push images
echo "⬆️  Pushing images to ACR..."
docker push $ACR_SERVER/bankcanada-api:latest
docker push $ACR_SERVER/bankcanada-web:latest

# Create AKS cluster
echo "☸️  Creating AKS cluster..."
az aks create \
    --resource-group $RESOURCE_GROUP \
    --name $AKS_NAME \
    --node-count 3 \
    --node-vm-size Standard_D2s_v3 \
    --attach-acr $ACR_NAME \
    --enable-managed-identity \
    --generate-ssh-keys

# Get AKS credentials
echo "🔑 Getting AKS credentials..."
az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_NAME

# Create namespace
echo "📁 Creating Kubernetes namespace..."
kubectl apply -f azure/kubernetes/namespace.yaml

# Update image references in deployment files
echo "🔄 Updating deployment manifests..."
sed -i "s|bankcanadamlops.azurecr.io|$ACR_SERVER|g" azure/kubernetes/api-deployment.yaml

# Deploy application
echo "🚀 Deploying application to AKS..."
kubectl apply -f azure/kubernetes/api-deployment.yaml
kubectl apply -f azure/kubernetes/api-service.yaml
kubectl apply -f azure/kubernetes/api-ingress.yaml

# Wait for deployment
echo "⏳ Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/bankcanada-api -n $NAMESPACE

# Get service details
echo "📊 Getting service information..."
kubectl get services -n $NAMESPACE
kubectl get pods -n $NAMESPACE

# Get external IP
echo "🌐 Getting external access information..."
EXTERNAL_IP=$(kubectl get service bankcanada-api-service -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

if [ -z "$EXTERNAL_IP" ]; then
    echo "⏳ External IP not yet assigned. Getting service details:"
    kubectl describe service bankcanada-api-service -n $NAMESPACE
else
    echo "✅ Application deployed successfully!"
    echo "🔗 API URL: http://$EXTERNAL_IP:8000"
    echo "🔗 Health Check: http://$EXTERNAL_IP:8000/health"
    echo "🔗 API Docs: http://$EXTERNAL_IP:8000/docs"
fi

echo ""
echo "📋 Interview Demo Commands:"
echo "=========================="
echo "kubectl get pods -n $NAMESPACE"
echo "kubectl get services -n $NAMESPACE"  
echo "kubectl logs -f deployment/bankcanada-api -n $NAMESPACE"
echo "kubectl describe deployment bankcanada-api -n $NAMESPACE"
echo ""
echo "🎯 Your cloud-native MLOps platform is ready for the interview!"
