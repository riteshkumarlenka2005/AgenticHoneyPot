#!/bin/bash
echo "🚀 Starting Agentic HoneyPot..."

# Check if Docker is available
if command -v docker-compose &> /dev/null; then
    echo "Using Docker..."
    docker-compose up -d
    echo "✅ Services starting..."
    echo "Frontend: http://localhost:3000"
    echo "Backend:  http://localhost:8000"
    echo "API Docs: http://localhost:8000/docs"
else
    echo "Docker not found. Starting manually..."
    
    # Start backend in background
    cd backend
    source venv/bin/activate
    uvicorn app.main:app --reload --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    # Start frontend
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    echo "✅ Services started!"
    echo "Backend PID: $BACKEND_PID"
    echo "Frontend PID: $FRONTEND_PID"
fi
