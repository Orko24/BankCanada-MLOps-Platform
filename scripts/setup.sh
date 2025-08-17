#!/bin/bash

# Bank of Canada MLOps Platform - Setup Script
# Automated environment setup for local development and demonstration

set -e  # Exit on any error

echo "🏦 Bank of Canada MLOps Platform Setup"
echo "======================================="
echo ""
echo "🐳 RECOMMENDED: Use Docker for easiest setup!"
echo "   See DOCKER_SETUP.md for simple docker-compose instructions"
echo ""
echo "This script sets up the platform for local development without Docker."
echo "Press Ctrl+C to cancel and use Docker instead, or continue for native setup."
echo ""
sleep 3

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    print_status "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker Desktop."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker Desktop."
        exit 1
    fi
    
    print_success "Docker is installed and running"
}

# Check if Python is installed
check_python() {
    print_status "Checking Python installation..."
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.9 or higher."
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2)
    print_success "Python $python_version is installed"
}

# Check if Node.js is installed
check_node() {
    print_status "Checking Node.js installation..."
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18 or higher."
        exit 1
    fi
    
    node_version=$(node --version)
    print_success "Node.js $node_version is installed"
}

# Create Python virtual environment
setup_python_env() {
    print_status "Setting up Python virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install Python dependencies
    print_status "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    print_success "Python dependencies installed"
}

# Setup Node.js environment
setup_node_env() {
    print_status "Setting up Node.js environment..."
    
    cd web
    npm install
    print_success "Node.js dependencies installed"
    cd ..
}

# Create environment configuration
setup_env_config() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        cp env.example .env
        print_warning "Created .env file from template. Please update with your API keys."
        print_warning "Required: ANTHROPIC_API_KEY (for AI agent functionality)"
    else
        print_warning ".env file already exists"
    fi
    
    # Create data directories
    mkdir -p data/raw data/processed data/models
    mkdir -p logs
    
    print_success "Environment configuration completed"
}

# Initialize databases
setup_databases() {
    print_status "Setting up databases with Docker Compose..."
    
    # Start only the database services first
    docker-compose up -d postgres redis
    
    # Wait for databases to be ready
    print_status "Waiting for databases to initialize..."
    sleep 10
    
    # Run database migrations (if they exist)
    if [ -f "alembic.ini" ]; then
        source venv/bin/activate
        alembic upgrade head
        print_success "Database migrations completed"
    fi
    
    print_success "Databases are ready"
}

# Start all services
start_services() {
    print_status "Starting all services..."
    
    # Start all services with Docker Compose
    docker-compose up -d
    
    # Wait for services to be ready
    print_status "Waiting for services to start..."
    sleep 15
    
    # Check service health
    check_service_health
}

# Check service health
check_service_health() {
    print_status "Checking service health..."
    
    services=(
        "http://localhost:5432:PostgreSQL Database"
        "http://localhost:6379:Redis Cache"
        "http://localhost:5000:MLflow Tracking"
        "http://localhost:8000:FastAPI Backend"
        "http://localhost:3000:React Frontend"
    )
    
    for service in "${services[@]}"; do
        url=$(echo $service | cut -d':' -f1-2)
        name=$(echo $service | cut -d':' -f3)
        
        # Simple health check (adjust based on actual endpoints)
        if curl -s "$url" &> /dev/null || nc -z localhost $(echo $url | cut -d':' -f3) &> /dev/null; then
            print_success "$name is healthy"
        else
            print_warning "$name may not be ready yet"
        fi
    done
}

# Setup demo data
setup_demo_data() {
    print_status "Setting up demo data..."
    
    source venv/bin/activate
    
    # Run data ingestion script (if it exists)
    if [ -f "scripts/ingest_demo_data.py" ]; then
        python scripts/ingest_demo_data.py
        print_success "Demo data loaded"
    else
        print_warning "Demo data script not found - you'll need to populate data manually"
    fi
}

# Display access information
show_access_info() {
    echo ""
    echo "🎉 Setup Complete!"
    echo "=================="
    echo ""
    echo "Access your Bank of Canada MLOps Platform:"
    echo ""
    echo "🌐 Web Dashboard:     http://localhost:3000"
    echo "🔧 API Documentation: http://localhost:8000/docs"
    echo "📊 MLflow UI:         http://localhost:5000"
    echo "📈 Grafana Monitoring: http://localhost:3001 (admin/admin)"
    echo ""
    echo "🔑 Default Credentials:"
    echo "   Username: admin@bankcanada.ca"
    echo "   Password: admin123"
    echo ""
    echo "📚 Documentation:"
    echo "   - Interview Guide: docs/INTERVIEW_GUIDE.md"
    echo "   - API Docs: http://localhost:8000/docs"
    echo "   - Architecture: docs/ARCHITECTURE.md"
    echo ""
    echo "🛑 To stop all services: docker-compose down"
    echo "🔄 To restart services: docker-compose restart"
    echo ""
}

# Cleanup function for errors
cleanup() {
    print_error "Setup failed. Cleaning up..."
    docker-compose down
    exit 1
}

# Main setup process
main() {
    echo "Starting automated setup process..."
    echo ""
    
    # Set up error handling
    trap cleanup ERR
    
    # Check prerequisites
    check_docker
    check_python
    check_node
    
    # Setup environments
    setup_env_config
    setup_python_env
    setup_node_env
    
    # Setup and start services
    setup_databases
    start_services
    
    # Setup demo data
    setup_demo_data
    
    # Show access information
    show_access_info
    
    print_success "Bank of Canada MLOps Platform is ready for demonstration!"
}

# Handle command line arguments
case "${1:-setup}" in
    "setup")
        main
        ;;
    "start")
        print_status "Starting services..."
        docker-compose up -d
        check_service_health
        show_access_info
        ;;
    "stop")
        print_status "Stopping services..."
        docker-compose down
        print_success "All services stopped"
        ;;
    "restart")
        print_status "Restarting services..."
        docker-compose restart
        check_service_health
        print_success "Services restarted"
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "clean")
        print_warning "This will remove all data and containers. Are you sure? (y/N)"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            docker-compose down -v --remove-orphans
            docker system prune -f
            rm -rf venv
            print_success "Environment cleaned"
        fi
        ;;
    "help")
        echo "Bank of Canada MLOps Platform Setup Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  setup     Complete setup (default)"
        echo "  start     Start all services"
        echo "  stop      Stop all services"
        echo "  restart   Restart all services"
        echo "  logs      Show service logs"
        echo "  clean     Clean all data and containers"
        echo "  help      Show this help message"
        ;;
    *)
        print_error "Unknown command: $1"
        print_warning "Use '$0 help' for available commands"
        exit 1
        ;;
esac
