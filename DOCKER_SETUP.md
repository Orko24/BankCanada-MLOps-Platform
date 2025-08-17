# 🐳 Docker Setup Guide - Bank of Canada MLOps Platform

## Quick Start

### Prerequisites
- Docker Desktop installed and running
- At least 8GB RAM available for Docker
- 10GB free disk space

### One-Command Setup
```bash
# Clone repository and start everything
git clone <repository>
cd BankofCanada_project

# Copy environment template
cp env.example .env

# Start all services
docker-compose up -d

# Watch logs (optional)
docker-compose logs -f
```

### Access Services
- **Economic Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **MLflow Tracking**: http://localhost:5000
- **Database**: localhost:5432 (user: admin, password: secure_password)
- **Redis Cache**: localhost:6379
- **Grafana Monitoring**: http://localhost:3001 (admin/admin)

## Service Overview

| Service | Port | Description |
|---------|------|-------------|
| `postgres` | 5432 | PostgreSQL database with economic data |
| `redis` | 6379 | Redis cache for session management |
| `mlflow` | 5000 | MLflow tracking server with model registry |
| `api` | 8000 | FastAPI backend with economic endpoints |
| `worker` | - | Background worker for data ingestion |
| `web` | 3000 | React dashboard for economic indicators |
| `prometheus` | 9090 | Metrics collection |
| `grafana` | 3001 | Monitoring dashboards |

## Docker Commands

### Basic Operations
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f [service_name]

# Check service status
docker-compose ps
```

### Development Workflow
```bash
# Start with hot reload for development
docker-compose up -d

# Rebuild specific service
docker-compose build api
docker-compose up -d api

# Access service shell
docker-compose exec api bash
docker-compose exec postgres psql -U admin -d bankcanada_mlops
```

### Data Management
```bash
# Reset database (WARNING: destroys data)
docker-compose down -v
docker-compose up -d

# Backup database
docker-compose exec postgres pg_dump -U admin bankcanada_mlops > backup.sql

# Restore database
docker-compose exec -T postgres psql -U admin bankcanada_mlops < backup.sql
```

## Environment Variables

Create `.env` file with required variables:
```bash
# Required for AI agent (optional)
DEEPSEEK_API_KEY=your_deepseek_key_here

# Optional Azure keys for cloud features
AZURE_CLIENT_ID=your_azure_client_id
AZURE_CLIENT_SECRET=your_azure_client_secret
AZURE_TENANT_ID=your_azure_tenant_id

# Database (automatically configured in docker-compose)
DATABASE_URL=postgresql://admin:secure_password@postgres:5432/bankcanada_mlops
REDIS_URL=redis://redis:6379
MLFLOW_TRACKING_URI=http://mlflow:5000
```

## Troubleshooting

### Common Issues

**Services won't start:**
```bash
# Check Docker resources
docker system df
docker system prune -f

# Check logs for errors
docker-compose logs api
docker-compose logs postgres
```

**Database connection issues:**
```bash
# Wait for database to initialize (first startup takes 30-60 seconds)
docker-compose logs postgres

# Test connection
docker-compose exec postgres psql -U admin -d bankcanada_mlops -c "SELECT 1;"
```

**Port conflicts:**
```bash
# Check what's using ports
netstat -an | grep :3000
netstat -an | grep :8000

# Stop conflicting services or change ports in docker-compose.yml
```

**Out of memory:**
```bash
# Increase Docker memory in Docker Desktop settings
# Minimum 8GB recommended

# Check container resource usage
docker stats
```

### Performance Optimization

**For slower machines:**
```bash
# Start services one at a time
docker-compose up -d postgres redis
sleep 30
docker-compose up -d mlflow
sleep 15
docker-compose up -d api worker
sleep 10
docker-compose up -d web
```

**For development:**
```bash
# Use override file for hot reload (already configured)
docker-compose up -d

# Changes to code will automatically reload
```

## Production Considerations

**Security:**
- Change default passwords in production
- Use proper SSL certificates
- Configure firewall rules
- Set up proper secret management

**Scaling:**
- Use multiple API replicas
- Set up database connection pooling
- Configure Redis clustering
- Implement proper logging aggregation

**Monitoring:**
- Configure alerting rules in Grafana
- Set up log aggregation
- Monitor resource usage
- Set up backup strategies

## Health Checks

All services include health checks that can be monitored:
```bash
# Check service health
docker-compose ps

# Manual health check
curl http://localhost:8000/health
curl http://localhost:3000/health
```

## Success Indicators

When everything is working correctly:
- ✅ All 8 services show "Up" status in `docker-compose ps`
- ✅ Web dashboard loads at http://localhost:3000
- ✅ API docs accessible at http://localhost:8000/docs
- ✅ MLflow UI shows at http://localhost:5000
- ✅ No error messages in `docker-compose logs`
- ✅ Economic data appears in dashboard (after worker processes data)

**Total setup time: 5-10 minutes on first run, 2-3 minutes on subsequent runs.**
