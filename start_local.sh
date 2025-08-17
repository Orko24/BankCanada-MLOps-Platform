#!/bin/bash

# 🚀 Bank of Canada MLOps Platform - Local Startup Script
# This script sets up and starts the entire platform locally

echo "🏦 Bank of Canada MLOps Platform - Local Setup"
echo "=============================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker Desktop first."
    exit 1
fi

echo "✅ Docker is running"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "✅ .env file created with default settings"
    echo "   PostgreSQL password: pass"
    echo "   You can edit .env to customize settings"
else
    echo "✅ .env file already exists"
fi

# Stop any existing containers
echo "🛑 Stopping any existing containers..."
docker-compose down --remove-orphans

# Build all images
echo "🏗️  Building Docker images..."
docker-compose build

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to build Docker images"
    exit 1
fi

echo "✅ Docker images built successfully"

# Start all services
echo "🚀 Starting all services..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to start services"
    exit 1
fi

echo "✅ All services started successfully"

# Wait a moment for services to initialize
echo "⏳ Waiting for services to initialize..."
sleep 10

# Check service status
echo "🔍 Checking service status..."
docker-compose ps

echo ""
echo "🎉 Setup Complete! Access your services:"
echo "=============================================="
echo "📊 Economic Dashboard:    http://localhost:3000"
echo "🔧 API Documentation:    http://localhost:8000/docs"
echo "📈 MLflow Tracking:       http://localhost:5000"
echo "🗄️  Database:             localhost:5432 (admin/pass)"
echo "💾 Redis Cache:           localhost:6379"
echo ""
echo "🤖 AI Research Assistant:"
echo "   Go to http://localhost:3000 → AI Research Assistant tab"
echo "   Click 'Settings' to add your DeepSeek API key"
echo ""
echo "📋 Quick Commands:"
echo "   View logs:        docker-compose logs -f"
echo "   Stop services:    docker-compose down"
echo "   Restart:          docker-compose restart"
echo ""
echo "🎯 Ready for your Bank of Canada interview demo!"
