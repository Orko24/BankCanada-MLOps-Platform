# 🏦 Bank of Canada MLOps Platform

[![CI](https://github.com/yourusername/BankofCanada_project/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/BankofCanada_project/actions/workflows/ci.yml)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://docker.com)
[![Azure](https://img.shields.io/badge/Azure-MLOps-0078d4)](https://azure.microsoft.com)
[![Databricks](https://img.shields.io/badge/Databricks-Ready-ff6b35)](https://databricks.com)

> **Enterprise MLOps platform for economic forecasting and policy analysis** - Built for Bank of Canada technical interview demonstration.

## 🚀 **Quick Demo Setup**

### **Option 1: Docker (Recommended - 2 minutes)**
```bash
git clone https://github.com/yourusername/BankofCanada_project.git
cd BankofCanada_project
cp env.example .env
docker-compose up -d
```

**Access:**
- 🌐 **Dashboard**: http://localhost:3000
- 🔧 **API Docs**: http://localhost:8000/docs
- 📊 **MLflow**: http://localhost:5000

### **Option 2: Cloud Setup**
See [`docs/INTERVIEW_GUIDE.md`](docs/INTERVIEW_GUIDE.md) for Azure and Databricks integration.

## 📊 **What This Demonstrates**

| **Technology** | **Implementation** | **Use Case** |
|---|---|---|
| **Databricks** | Economic data processing with Delta Lake | Real Bank of Canada API integration |
| **MLflow** | Complete model lifecycle management | Automated training and deployment |
| **Azure DevOps** | CI/CD pipeline with security scanning | Production deployment automation |
| **FastAPI** | RESTful API with authentication | Economic data and ML endpoints |
| **React** | Professional economic dashboard | Real-time data visualization |
| **LangChain** | AI agents for economic research | Policy document analysis with RAG |
| **Docker** | Containerized microservices | Production-ready architecture |
| **Kubernetes** | AKS deployment manifests | Enterprise scalability |

## 🎯 **Interview Ready Features**

### **✅ Technical Depth**
- **End-to-end MLOps** from data ingestion to production deployment
- **Real economic data** processing with Bank of Canada APIs
- **Enterprise security** with RBAC, secret management, and audit trails
- **Advanced AI capabilities** beyond traditional ML models

### **✅ Business Understanding** 
- **Central banking domain** knowledge and use cases
- **Policy analysis** and economic forecasting applications
- **Risk management** and monitoring capabilities
- **Scalable architecture** for institutional requirements

### **✅ Production Excellence**
- **Infrastructure as Code** with Azure Bicep templates
- **Automated testing** and security scanning in CI/CD
- **Monitoring and alerting** with Prometheus and Grafana
- **Documentation** and deployment guides

## 📁 **Repository Structure**

```
├── 📊 databricks/          # Economic data processing & ML training
├── 🔧 api/                 # FastAPI backend services  
├── 🎨 web/                 # React economic dashboard
├── 🤖 agents/              # LangChain AI research agents
├── ☁️ azure/               # Cloud deployment & CI/CD
├── 🐳 docker-compose.yml   # Local development environment
├── 📚 docs/                # Interview guide & documentation
└── 🚀 scripts/             # Setup automation
```

## 🛠️ **Development**

### **Prerequisites**
- Docker Desktop
- Python 3.9+
- Node.js 18+
- Azure account (free tier)
- Databricks account (community edition)

### **Local Development**
```bash
# Start development environment
docker-compose up -d

# View logs
docker-compose logs -f

# Run tests
pytest tests/

# Code formatting
black api/
```

### **Environment Variables**
Copy `env.example` to `.env` and configure:
```bash
# Required for AI agent
ANTHROPIC_API_KEY=your_key

# Optional for cloud features  
AZURE_CLIENT_ID=your_id
DATABRICKS_TOKEN=your_token
```

## 📖 **Documentation**

| **Document** | **Purpose** |
|---|---|
| [`docs/INTERVIEW_GUIDE.md`](docs/INTERVIEW_GUIDE.md) | Complete interview preparation |
| [`DOCKER_SETUP.md`](DOCKER_SETUP.md) | Docker development guide |
| [`api/README.md`](api/README.md) | API documentation |
| [`PROJECT_SUMMARY.md`](PROJECT_SUMMARY.md) | Executive overview |

## 🎬 **Demo Scenarios**

### **5-Minute Technical Demo**
1. **Architecture Overview** - Explain microservices design
2. **Live Data Processing** - Show Databricks notebook execution
3. **ML Pipeline** - Demonstrate MLflow experiment tracking
4. **Production API** - Interactive API documentation
5. **Economic Dashboard** - Real-time data visualization

### **Deep Technical Discussion**
- **Databricks implementation** with medallion architecture
- **MLOps best practices** with automated deployment
- **Azure cloud architecture** and scalability design
- **Security considerations** for financial services
- **AI agent capabilities** for economic research

## 🏆 **Interview Advantages**

### **Beyond Typical Candidates**
- ✅ **Working platform** vs. theoretical knowledge
- ✅ **Domain expertise** in central banking
- ✅ **Production architecture** vs. toy examples
- ✅ **Complete technology stack** alignment
- ✅ **Advanced AI integration** beyond basic ML

### **Conversation Starters**
- *"I built this specifically for Bank of Canada's requirements..."*
- *"Let me show you how the economic forecasting pipeline works..."*
- *"The AI agent can analyze policy documents and integrate with our models..."*
- *"This architecture could scale to handle the Bank's full data volume..."*

## 📞 **Support**

For interview preparation questions, see the comprehensive guide at [`docs/INTERVIEW_GUIDE.md`](docs/INTERVIEW_GUIDE.md).

---

**Built to demonstrate enterprise-grade MLOps capabilities for Bank of Canada technical assessment.**
