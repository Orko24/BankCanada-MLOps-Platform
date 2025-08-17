@echo off
REM 🚀 Bank of Canada MLOps Platform - Local Startup Script (Windows)
REM This script sets up and starts the entire platform locally

echo 🏦 Bank of Canada MLOps Platform - Local Setup
echo ==============================================

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo ✅ Docker is running

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file from template...
    copy env.example .env >nul
    echo ✅ .env file created with default settings
    echo    PostgreSQL password: pass
    echo    You can edit .env to customize settings
) else (
    echo ✅ .env file already exists
)

REM Stop any existing containers
echo 🛑 Stopping any existing containers...
docker-compose down --remove-orphans

REM Build all images
echo 🏗️  Building Docker images...
docker-compose build

if %errorlevel% neq 0 (
    echo ❌ Error: Failed to build Docker images
    pause
    exit /b 1
)

echo ✅ Docker images built successfully

REM Start all services
echo 🚀 Starting all services...
docker-compose up -d

if %errorlevel% neq 0 (
    echo ❌ Error: Failed to start services
    pause
    exit /b 1
)

echo ✅ All services started successfully

REM Wait a moment for services to initialize
echo ⏳ Waiting for services to initialize...
timeout /t 10 /nobreak >nul

REM Check service status
echo 🔍 Checking service status...
docker-compose ps

echo.
echo 🎉 Setup Complete! Access your services:
echo ==============================================
echo 📊 Economic Dashboard:    http://localhost:3000
echo 🔧 API Documentation:    http://localhost:8000/docs
echo 📈 MLflow Tracking:       http://localhost:5000
echo 🗄️  Database:             localhost:5432 (admin/pass)
echo 💾 Redis Cache:           localhost:6379
echo.
echo 🤖 AI Research Assistant:
echo    Go to http://localhost:3000 → AI Research Assistant tab
echo    Click 'Settings' to add your DeepSeek API key
echo.
echo 📋 Quick Commands:
echo    View logs:        docker-compose logs -f
echo    Stop services:    docker-compose down
echo    Restart:          docker-compose restart
echo.
echo 🎯 Ready for your Bank of Canada interview demo!
echo.
pause
