#!/bin/bash

# Quick Start Script for Agentic HoneyPot

set -e

echo "=================================="
echo "Agentic HoneyPot - Quick Start"
echo "=================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ .env file created"
    echo "⚠️  Please edit .env file with your configuration"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🚀 Starting services with Docker Compose..."
echo ""

# Start services
docker-compose up -d db redis

echo "⏳ Waiting for database to be ready..."
sleep 5

docker-compose up -d backend

echo "⏳ Waiting for backend to be ready..."
sleep 5

docker-compose up -d frontend

echo ""
echo "=================================="
echo "✅ Services Started Successfully!"
echo "=================================="
echo ""
echo "Access the application at:"
echo "  🌐 Frontend:  http://localhost:3000"
echo "  🔧 Backend:   http://localhost:8000"
echo "  📚 API Docs:  http://localhost:8000/docs"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop services:"
echo "  docker-compose down"
echo ""
echo "=================================="
