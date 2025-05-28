#!/bin/bash

# Forsit API Setup and Run Script
# This script helps you set up and run the Forsit e-commerce API

set -e

echo "🚀 Forsit E-commerce API Setup Script"
echo "======================================"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."
if ! command_exists docker; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command_exists docker-compose; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Prerequisites check passed!"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating one with default values..."
    cat > .env << EOF
# PostgreSQL Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/forsit_db

# Security
SECRET_KEY=8d5f19e991cce72e3ff07d0a774aa8d08bb5f3347f65c933d61d22e98b3898f3
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Settings
PROJECT_NAME=Forsit API
API_V1_STR=/api/v1
DEBUG=True

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:8000", "http://localhost:3000", "http://localhost:5173"]

# Superuser Configuration
FIRST_SUPERUSER_USERNAME=admin
FIRST_SUPERUSER_EMAIL=admin@forsit.com
FIRST_SUPERUSER_PASSWORD=admin123

# PostgreSQL Settings for Docker
POSTGRES_SERVER=postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=forsit_db
EOF
    echo "✅ Created .env file with default settings"
fi

# Function to show menu
show_menu() {
    echo ""
    echo "🎯 What would you like to do?"
    echo "1) Start with Docker (Recommended)"
    echo "2) Start PostgreSQL only"
    echo "3) Setup local development"
    echo "4) Run tests"
    echo "5) View logs"
    echo "6) Stop all services"
    echo "7) Clean up (remove containers and volumes)"
    echo "8) Exit"
    echo ""
}

# Function to start with Docker
start_docker() {
    echo "🐳 Starting services with Docker..."
    docker-compose up -d
    
    echo "⏳ Waiting for services to be ready..."
    sleep 10
    
    echo "📊 Checking service status..."
    docker-compose ps
    
    echo ""
    echo "🎉 Services are running!"
    echo "📚 API Documentation: http://localhost:8000/docs"
    echo "🔧 PgAdmin: http://localhost:5050 (admin@forsit.com / admin)"
    echo "🌐 API Base URL: http://localhost:8000"
    echo ""
    echo "🔑 Default superuser credentials:"
    echo "   Username: admin"
    echo "   Email: admin@forsit.com"
    echo "   Password: admin123"
}

# Function to start PostgreSQL only
start_postgres_only() {
    echo "🐘 Starting PostgreSQL only..."
    docker-compose up -d postgres pgadmin
    echo "✅ PostgreSQL and PgAdmin are running"
    echo "🔧 PgAdmin: http://localhost:5050"
}

# Function to setup local development
setup_local() {
    echo "💻 Setting up local development environment..."
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
    
    echo "📚 Installing dependencies..."
    pip install -r requirements.txt
    
    echo "🐘 Make sure PostgreSQL is running..."
    docker-compose up -d postgres
    
    echo "⏳ Waiting for PostgreSQL..."
    sleep 5
    
    echo "🗃️  Running migrations..."
    alembic upgrade head
    
    echo "👤 Creating superuser..."
    python scripts/create_superuser.py
    
    echo "🚀 Starting development server..."
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
}

# Function to run tests
run_tests() {
    echo "🧪 Running tests..."
    if [ -f "tests/test_main.py" ]; then
        python -m pytest tests/ -v
    else
        echo "⚠️  No tests found. You can create tests in the tests/ directory."
    fi
}

# Function to view logs
view_logs() {
    echo "📋 Viewing application logs..."
    docker-compose logs -f api
}

# Function to stop services
stop_services() {
    echo "⏹️  Stopping all services..."
    docker-compose down
    echo "✅ All services stopped"
}

# Function to clean up
cleanup() {
    echo "🧹 Cleaning up containers and volumes..."
    read -p "Are you sure? This will remove all data! (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v
        docker system prune -f
        echo "✅ Cleanup completed"
    else
        echo "❌ Cleanup cancelled"
    fi
}

# Main menu loop
while true; do
    show_menu
    read -p "Enter your choice (1-8): " choice
    
    case $choice in
        1)
            start_docker
            ;;
        2)
            start_postgres_only
            ;;
        3)
            setup_local
            ;;
        4)
            run_tests
            ;;
        5)
            view_logs
            ;;
        6)
            stop_services
            ;;
        7)
            cleanup
            ;;
        8)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid option. Please try again."
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
done
