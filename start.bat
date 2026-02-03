@echo off
echo Starting Agentic HoneyPot...

docker-compose --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Using Docker...
    docker-compose up -d
    echo Services starting...
    echo Frontend: http://localhost:3000
    echo Backend:  http://localhost:8000
    echo API Docs: http://localhost:8000/docs
) else (
    echo Docker not found. Please install Docker or run manually.
    echo.
    echo Manual steps:
    echo 1. Open terminal 1: cd backend ^&^& venv\Scripts\activate ^&^& uvicorn app.main:app --reload --port 8000
    echo 2. Open terminal 2: cd frontend ^&^& npm run dev
)
pause
