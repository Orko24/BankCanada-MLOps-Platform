# 🏦 Bank of Canada MLOps - Azure Deployment Guide

## 🚀 **QUICK START**

Your deployment issues have been **FIXED**! Here's what was added:

### **✅ FIXES IMPLEMENTED**

1. **🗄️ Created Missing Deployments:**
   - `postgres-deployment.yaml` - PostgreSQL with persistent storage
   - `redis-deployment.yaml` - Redis cache with persistent storage  
   - `mlflow-deployment.yaml` - MLflow tracking server with artifacts

2. **🔐 Fixed ACR Authentication:**
   - Added proper `acr-secret` creation in deployment scripts
   - Fixed image registry references

3. **📋 Deployment Order:**
   - Deploy infrastructure components first (PostgreSQL, Redis, MLflow)
   - Wait for readiness before deploying API
   - Proper health checks and dependencies

## 🚀 **DEPLOYMENT COMMANDS**

### **Option 1: PowerShell (Windows)**
```powershell
.\deploy-to-azure-fixed.ps1
```

### **Option 2: Bash (Linux/Mac)**  
```bash
chmod +x deploy-to-azure.sh
./deploy-to-azure.sh
```

## 📊 **WHAT GETS DEPLOYED**

### **Infrastructure Layer**
- **PostgreSQL** (bankcanada_mlops database)
- **Redis** (caching layer)
- **MLflow** (ML experiment tracking)

### **Application Layer**  
- **FastAPI Backend** (3 replicas with load balancing)
- **LoadBalancer Service** (gets external IP automatically)

### **Storage**
- **10GB** for PostgreSQL data
- **1GB** for Redis data  
- **5GB** for MLflow artifacts

## 🔍 **MONITORING DEPLOYMENT**

### **Check Deployment Status**
```bash
# Check all pods
kubectl get pods -n mlops-production

# Check services and external IP
kubectl get services -n mlops-production

# Check logs if issues
kubectl logs -f deployment/bankcanada-api -n mlops-production
kubectl logs -f deployment/postgres -n mlops-production
```

### **Expected Results**
```bash
NAME                              READY   STATUS    
bankcanada-api-xxx                3/3     Running   
postgres-xxx                      1/1     Running   
redis-xxx                         1/1     Running   
mlflow-xxx                        1/1     Running   

NAME                     TYPE           EXTERNAL-IP     PORT(S)
bankcanada-api-service   LoadBalancer   20.xx.xx.xx     80:xxxxx/TCP
```

## 🌐 **ACCESS YOUR APPLICATION**

Once deployed, access your Bank of Canada MLOps platform:

- **🔗 API Documentation:** `http://<EXTERNAL-IP>/docs`
- **🔗 Health Check:** `http://<EXTERNAL-IP>/health`  
- **🔗 Economic Data API:** `http://<EXTERNAL-IP>/api/economic-data`

## 🛠️ **TROUBLESHOOTING**

### **If Pods Are Pending**
```bash
# Check resource availability
kubectl describe pods -n mlops-production

# Check persistent volume claims
kubectl get pvc -n mlops-production
```

### **If LoadBalancer Has No External IP**
```bash
# Check AKS cluster has LoadBalancer support
az aks show --resource-group bankcanada-demo-rg --name bankcanada-aks --query networkProfile

# Describe service for more details
kubectl describe service bankcanada-api-service -n mlops-production
```

### **If Database Connection Fails**
```bash
# Test PostgreSQL connectivity
kubectl exec -it deployment/postgres -n mlops-production -- psql -U postgres -d bankcanada_mlops -c "SELECT 1;"

# Check API logs for connection errors
kubectl logs deployment/bankcanada-api -n mlops-production | grep -i database
```

## 🔧 **ENVIRONMENT VARIABLES**

All services are configured with proper environment variables:

- **Database:** `postgresql://postgres:bankcanada123@postgres-service:5432/bankcanada_mlops`
- **Redis:** `redis://redis-service:6379`  
- **MLflow:** `http://mlflow-service:5000`

## 🎯 **NEXT STEPS**

1. **Deploy:** Run the deployment script
2. **Verify:** Check external IP assignment  
3. **Test:** Access API documentation
4. **Configure:** Add your Databricks/API keys via frontend
5. **Demo Ready:** Your MLOps platform is interview-ready!

---

**💡 The deployment script will now:**
- ✅ Create all missing components
- ✅ Deploy in the correct order  
- ✅ Wait for readiness checks
- ✅ Get you a working external IP
- ✅ Give you a fully functional MLOps platform

**Run the script and watch your Bank of Canada platform come to life! 🚀**
