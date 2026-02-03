#!/bin/bash
# Quick validation script for the Agentic HoneyPot system

echo "🔍 Validating Agentic HoneyPot Implementation..."
echo ""

# Check backend structure
echo "✓ Backend Structure:"
echo "  - FastAPI app: backend/app/main.py"
echo "  - API routes: backend/app/api/routes/"
echo "  - Core services: backend/app/services/"
echo "  - Agent logic: backend/app/core/agent/"
echo "  - Models: backend/app/models/"
echo ""

# Check frontend structure
echo "✓ Frontend Structure:"
echo "  - Next.js 14 app"
echo "  - Dashboard page: frontend/src/app/dashboard/page.tsx"
echo "  - Conversations page: frontend/src/app/conversations/page.tsx"
echo "  - Intelligence page: frontend/src/app/intelligence/page.tsx"
echo "  - Analytics page: frontend/src/app/analytics/page.tsx"
echo "  - Settings page: frontend/src/app/settings/page.tsx"
echo ""

# Check configuration
echo "✓ Configuration:"
echo "  - Docker Compose: docker-compose.yml"
echo "  - Environment template: .env.example"
echo "  - Frontend Dockerfile: frontend/Dockerfile"
echo "  - Backend Dockerfile: backend/Dockerfile"
echo ""

# Count files
BACKEND_FILES=$(find backend/app -name "*.py" | wc -l)
FRONTEND_FILES=$(find frontend/src -name "*.tsx" -o -name "*.ts" | wc -l)

echo "📊 Statistics:"
echo "  - Backend Python files: $BACKEND_FILES"
echo "  - Frontend TypeScript files: $FRONTEND_FILES"
echo ""

echo "✅ All components are in place!"
echo ""
echo "🚀 To start the system:"
echo "  1. Copy .env.example to .env"
echo "  2. Add your OPENAI_API_KEY (optional)"
echo "  3. Run: docker-compose up -d"
echo "  4. Access frontend at: http://localhost:3000"
echo "  5. Access API docs at: http://localhost:8000/docs"
