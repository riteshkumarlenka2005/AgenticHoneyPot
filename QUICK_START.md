# Quick Start Guide - Agentic HoneyPot

## ✅ Project is Complete and Ready!

All features have been implemented and tested. This guide will help you get started.

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+

---

## Quick Setup

### 1. Clone and Navigate
```bash
cd /path/to/AgenticHoneyPot
git checkout copilot/implement-pending-features
```

### 2. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp ../.env.example .env
# Edit .env with your database and API keys

# Run migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start frontend
npm run dev
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## Using Docker (Alternative)

```bash
# Start all services
docker-compose up -d

# Access at http://localhost:3000
```

---

## Feature Overview

### 🤖 AI Services

**HMM Stage Prediction**
```python
from app.services.ai.hmm_stages import HMMStagePredictor

predictor = HMMStagePredictor()
stage, confidence, probs = predictor.predict_stage(messages)
```

**Metrics Calculation**
```python
from app.services.ai.idr_metrics import IDRMetricsCalculator

calc = IDRMetricsCalculator()
metrics = calc.calculate_all_metrics(conversation_data)
```

**Multi-Agent Analysis**
```python
from app.services.ai.multi_agent import MultiAgentOrchestrator

orchestrator = MultiAgentOrchestrator()
result = await orchestrator.analyze_message(message, messages, intelligence)
```

### 🔒 Security

**Prompt Injection Detection**
```python
from app.core.prompt_injection import input_validator

is_valid, sanitized, attacks = input_validator.validate_and_sanitize(user_input)
```

**Instruction Hierarchy**
```python
from app.core.security import instruction_hierarchy

prompt = instruction_hierarchy.get_system_prompt(persona_context)
```

### 📊 Export & Monitoring

**STIX Export**
```python
from app.services.export.stix_exporter import stix_exporter

bundle = stix_exporter.export_conversation(conversation, intelligence)
json_output = stix_exporter.export_to_json(bundle, pretty=True)
```

**HITL Approval**
```python
from app.services.hitl.approval_queue import approval_queue

request = approval_queue.create_request(
    request_type="response",
    data={"message": "Proposed response"},
    priority="high"
)
```

---

## API Endpoints

### Core
- `GET /` - Root endpoint
- `GET /health` - Health check

### Conversations
- `GET /api/v1/conversations` - List all conversations
- `GET /api/v1/conversations/{id}` - Get conversation details

### Intelligence
- `GET /api/v1/intelligence` - List intelligence artifacts
- `GET /api/v1/intelligence/export` - Export intelligence

### Analytics
- `GET /api/v1/analytics/overview` - System overview
- `GET /api/v1/analytics/scam-types` - Scam type distribution
- `GET /api/v1/analytics/timeline` - Timeline data

### HITL (Human-in-the-Loop)
- `GET /api/v1/hitl/requests` - List pending requests
- `POST /api/v1/hitl/requests` - Create approval request
- `POST /api/v1/hitl/requests/{id}/approve` - Approve request
- `POST /api/v1/hitl/requests/{id}/reject` - Reject request
- `GET /api/v1/hitl/statistics` - Queue statistics

---

## Frontend Pages

### Main Pages
- `/` - Dashboard overview
- `/conversations` - List all conversations
- `/conversations/{id}` - Conversation detail with message thread
- `/intelligence` - Intelligence artifacts
- `/analytics` - Analytics and charts
- `/settings/personas` - Persona management

### Components
- `<PieChart />` - Scam type distribution
- `<LineChart />` - Timeline charts
- `<BarChart />` - Comparison metrics

---

## Testing

### Backend Tests
```bash
cd backend

# Test module imports
python3 -c "from app.services.ai.hmm_stages import HMMStagePredictor; print('✅ OK')"

# Run functional tests
python3 tests/test_functionality.py
```

### Frontend Tests
```bash
cd frontend

# TypeScript compilation
npx tsc --noEmit

# Build test
npm run build

# Lint
npm run lint
```

---

## Configuration

### Environment Variables

**Backend (.env)**
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/honeypot
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
SECRET_KEY=your-secret-key
```

**Frontend (.env.local)**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Troubleshooting

### Backend Issues

**Import Errors**
```bash
pip install -r requirements.txt
```

**Database Connection Failed**
```bash
# Check PostgreSQL is running
pg_isready

# Verify connection string in .env
```

**Redis Connection Failed**
```bash
# Check Redis is running
redis-cli ping
```

### Frontend Issues

**Build Failures**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**TypeScript Errors**
```bash
# Check for compilation errors
npx tsc --noEmit
```

---

## Performance Tips

1. **Enable Redis Caching**: Set REDIS_URL for better performance
2. **Use Connection Pooling**: SQLAlchemy manages connections automatically
3. **Enable Production Mode**: Set DEBUG=False in production
4. **Use CDN**: Serve static assets from CDN in production

---

## Security Checklist

- [ ] Change SECRET_KEY in production
- [ ] Set DEBUG=False
- [ ] Use HTTPS in production
- [ ] Configure CORS_ORIGINS properly
- [ ] Rotate API keys regularly
- [ ] Enable rate limiting
- [ ] Set up monitoring and alerts

---

## What's Implemented

### ✅ Phase 1: Database & Infrastructure
- Alembic migrations
- Async database operations
- Redis caching

### ✅ Phase 2: AI Features
- HMM scam stage prediction
- IDR/IDS/HAR metrics
- Multi-agent orchestration
- Model drift detection

### ✅ Phase 3: Security
- Prompt injection protection (15+ patterns)
- Instruction hierarchy
- Input sanitization

### ✅ Phase 4: Integrations
- RAG policy retrieval
- WHOIS domain analysis
- URL expansion
- Google Gemini LLM
- LLM factory with failover

### ✅ Phase 5: Export & Monitoring
- STIX 2.1 threat intelligence export
- HITL approval queue
- Auto-approval based on confidence

### ✅ Phase 6: Frontend
- Chart components (Pie, Line, Bar)
- WebSocket real-time updates
- Conversation detail view
- Persona management UI

---

## Next Steps

1. **Test the System**: Run through the quick start above
2. **Configure Production**: Set up production environment
3. **Security Audit**: Review security settings
4. **Load Testing**: Test under realistic load
5. **Deploy**: Deploy to staging then production

---

## Support

For issues or questions:
1. Check IMPLEMENTATION_SUMMARY.md for detailed documentation
2. Check PROJECT_VERIFICATION.md for verification details
3. Review API_EXAMPLES.md for API usage examples

---

**Status**: ✅ Complete and Ready  
**Version**: 1.0.0  
**Last Updated**: 2024-02-04
