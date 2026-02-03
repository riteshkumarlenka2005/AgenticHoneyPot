# Testing Guide

## Component Tests

Run individual component tests:

```bash
cd backend
python tests/test_components.py
```

This tests:
- Scam Detection Service
- Persona Generation
- Intelligence Extraction
- Mock Scammer Simulator
- Safety Guardrails

## End-to-End Demo

Run a full conversation demo:

```bash
cd backend
python tests/demo_conversation.py
```

This demonstrates:
- Complete honeypot-scammer conversation
- Agent decision making
- Intelligence extraction
- Structured JSON output

## Manual API Testing

### 1. Start the Backend

```bash
# With Docker
docker-compose up backend db redis

# Without Docker
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 2. Test Mock Scammer API

```bash
# Start a lottery scam session
curl -X POST http://localhost:8000/api/v1/mock-scammer/start \
  -H "Content-Type: application/json" \
  -d '{"scenario": "lottery_prize"}'

# Get scammer response
curl -X POST http://localhost:8000/api/v1/mock-scammer/respond \
  -H "Content-Type: application/json" \
  -d '{"session_id": "YOUR_SESSION_ID", "message": "Really? Tell me more!"}'
```

### 3. Test Honeypot Conversation

```bash
# Send a scam message to honeypot
curl -X POST http://localhost:8000/api/v1/conversations/incoming \
  -H "Content-Type: application/json" \
  -d '{
    "scammer_identifier": "test-scammer-001",
    "content": "Congratulations! You won $1,000,000 in our lottery!"
  }'

# List all conversations
curl http://localhost:8000/api/v1/conversations

# Get conversation details
curl http://localhost:8000/api/v1/conversations/CONVERSATION_ID
```

### 4. Test Analytics

```bash
# Get dashboard overview
curl http://localhost:8000/api/v1/analytics/overview

# Get scam type distribution
curl http://localhost:8000/api/v1/analytics/scam-types

# Get intelligence summary
curl http://localhost:8000/api/v1/intelligence/summary
```

## Frontend Testing

### 1. Start Frontend

```bash
# With Docker
docker-compose up frontend

# Without Docker
cd frontend
npm install
npm run dev
```

### 2. Access Pages

- Dashboard: http://localhost:3000/dashboard
- Conversations: http://localhost:3000/conversations
- Intelligence: http://localhost:3000/intelligence
- Analytics: http://localhost:3000/analytics
- Settings: http://localhost:3000/settings

### 3. Interactive Testing Flow

1. Start mock scammer session via API
2. Send scammer messages to honeypot
3. Watch real-time updates on dashboard
4. View conversation details
5. Check extracted intelligence
6. Review analytics

## Expected Results

### Successful Scam Detection

```json
{
  "is_scam": true,
  "confidence": 0.85,
  "scam_type": "lottery",
  "detection_method": "rule_based"
}
```

### Extracted Intelligence

```json
{
  "upi_ids": ["scammer@paytm"],
  "bank_accounts": ["1234567890"],
  "ifsc_codes": ["SBIN0001234"],
  "phone_numbers": ["+91-9876543210"]
}
```

### Safety Validation

All honeypot responses should:
- ✅ Never commit to actual money transfer
- ✅ Never provide real personal data
- ✅ Never click external links
- ✅ Stay within safety guardrails

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Check connection
docker-compose logs db
```

### Import Errors

Make sure all `__init__.py` files exist:
```bash
find backend/app -type d -exec touch {}/__init__.py \;
```

### Frontend Build Issues

```bash
cd frontend
rm -rf node_modules .next
npm install
npm run build
```

## Performance Benchmarks

Expected performance:
- Scam detection: < 100ms
- Response generation: < 500ms
- API endpoint response: < 1s
- Frontend page load: < 2s

## CI/CD Testing

Run all tests before committing:

```bash
# Backend tests
cd backend
python tests/test_components.py
python tests/demo_conversation.py

# Frontend type checking
cd frontend
npm run build
```
