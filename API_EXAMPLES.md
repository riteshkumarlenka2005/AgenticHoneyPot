# API Usage Examples

This document provides practical examples for using the Agentic HoneyPot API.

## Table of Contents

- [Getting Started](#getting-started)
- [Mock Scammer Testing](#mock-scammer-testing)
- [Message Processing](#message-processing)
- [Viewing Intelligence](#viewing-intelligence)
- [Analytics](#analytics)

## Getting Started

Base URL: `http://localhost:8000`

All API endpoints are prefixed with `/api/v1/`

## Mock Scammer Testing

### 1. Start a Mock Scam Session

Start a lottery prize scam simulation:

```bash
curl -X POST http://localhost:8000/api/v1/mock-scammer/start \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "lottery_prize"
  }'
```

Response:
```json
{
  "session_id": "abc-123-def-456",
  "initial_message": "Congratulations! You have won Rs 25,00,000 in the KBC Lucky Draw...",
  "scenario": "lottery_prize"
}
```

### 2. List Available Scenarios

```bash
curl http://localhost:8000/api/v1/mock-scammer/scenarios
```

Response:
```json
{
  "scenarios": [
    {
      "id": "lottery_prize",
      "name": "Lottery Prize",
      "description": "Simulates a lottery prize scam"
    },
    {
      "id": "bank_kyc_fraud",
      "name": "Bank Kyc Fraud",
      "description": "Simulates a bank kyc fraud scam"
    }
    // ... more scenarios
  ]
}
```

## Message Processing

### Send Scammer Message to Honeypot

```bash
curl -X POST http://localhost:8000/api/v1/messages/incoming \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Congratulations! You have won Rs 25,00,000 in the KBC Lucky Draw. To claim, send verification fee of Rs 5,000.",
    "scammer_identifier": "scammer-phone-123"
  }'
```

Response:
```json
{
  "conversation_id": "conv-uuid-here",
  "honeypot_response": "Oh my! This is wonderful news! I've never won anything before. What do I need to do to claim my prize?",
  "scam_detected": true,
  "confidence": 0.95,
  "scam_type": "lottery_prize",
  "engagement_phase": "engaging"
}
```

### Continue Conversation

Use the same endpoint with the `conversation_id`:

```bash
curl -X POST http://localhost:8000/api/v1/messages/incoming \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Please send Rs 5,000 to UPI ID: scammer@upi",
    "scammer_identifier": "scammer-phone-123",
    "conversation_id": "conv-uuid-here"
  }'
```

## Viewing Conversations

### List All Conversations

```bash
curl http://localhost:8000/api/v1/conversations
```

### Get Specific Conversation

```bash
curl http://localhost:8000/api/v1/conversations/conv-uuid-here
```

Response:
```json
{
  "id": "conv-uuid-here",
  "scammer_identifier": "scammer-phone-123",
  "status": "active",
  "scam_type": "lottery_prize",
  "detection_confidence": 0.95,
  "started_at": "2024-01-15T10:30:00Z",
  "last_activity": "2024-01-15T10:35:00Z",
  "message_count": 6,
  "duration_seconds": 300,
  "persona": {
    "name": "Ramesh Kumar",
    "age": 58,
    "occupation": "Retired Government Clerk"
  },
  "messages": [
    {
      "id": "msg-1",
      "sender_type": "scammer",
      "content": "Congratulations! You won...",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "id": "msg-2",
      "sender_type": "honeypot",
      "content": "Oh my! This is wonderful...",
      "timestamp": "2024-01-15T10:31:00Z"
    }
  ],
  "intelligence_extracted": {
    "upi_ids": ["scammer@upi"],
    "bank_accounts": [],
    "phone_numbers": [],
    "urls": []
  },
  "manipulation_tactics": ["urgency", "greed"]
}
```

## Viewing Intelligence

### Get All Extracted Intelligence

```bash
curl http://localhost:8000/api/v1/intelligence
```

### Filter by Type

```bash
curl "http://localhost:8000/api/v1/intelligence?artifact_type=upi_id"
```

### Filter by Confidence

```bash
curl "http://localhost:8000/api/v1/intelligence?min_confidence=0.8"
```

Response:
```json
[
  {
    "id": "intel-1",
    "conversation_id": "conv-uuid",
    "artifact_type": "upi_id",
    "value": "scammer@upi",
    "confidence": 0.85,
    "extracted_at": "2024-01-15T10:35:00Z"
  },
  {
    "id": "intel-2",
    "conversation_id": "conv-uuid",
    "artifact_type": "bank_account",
    "value": "1234567890123",
    "confidence": 0.75,
    "extracted_at": "2024-01-15T10:40:00Z"
  }
]
```

### Export Intelligence

Export as JSON:
```bash
curl http://localhost:8000/api/v1/intelligence/export?format=json > intelligence.json
```

Export as CSV:
```bash
curl http://localhost:8000/api/v1/intelligence/export?format=csv > intelligence.csv
```

## Analytics

### Dashboard Overview

```bash
curl http://localhost:8000/api/v1/analytics/overview
```

Response:
```json
{
  "active_conversations": 3,
  "scams_detected": 15,
  "intelligence_extracted": 42,
  "time_wasted_seconds": 7200
}
```

### Scam Type Distribution

```bash
curl http://localhost:8000/api/v1/analytics/scam-types
```

Response:
```json
[
  {
    "scam_type": "lottery_prize",
    "count": 8,
    "percentage": 53.33
  },
  {
    "scam_type": "bank_kyc_fraud",
    "count": 4,
    "percentage": 26.67
  },
  {
    "scam_type": "investment_fraud",
    "count": 3,
    "percentage": 20.00
  }
]
```

### Timeline Data

Get last 24 hours:
```bash
curl http://localhost:8000/api/v1/analytics/timeline?hours=24
```

## Complete Workflow Example

Here's a complete workflow from start to finish:

```bash
# 1. Start mock scammer
SCAM_SESSION=$(curl -s -X POST http://localhost:8000/api/v1/mock-scammer/start \
  -H "Content-Type: application/json" \
  -d '{"scenario": "lottery_prize"}' | jq -r '.session_id')

echo "Started scam session: $SCAM_SESSION"

# 2. Get initial scam message
SCAM_MSG=$(curl -s -X POST http://localhost:8000/api/v1/mock-scammer/start \
  -H "Content-Type: application/json" \
  -d "{\"scenario\": \"lottery_prize\"}" | jq -r '.initial_message')

echo "Scam message: $SCAM_MSG"

# 3. Send to honeypot
CONV_ID=$(curl -s -X POST http://localhost:8000/api/v1/messages/incoming \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"$SCAM_MSG\", \"scammer_identifier\": \"test-123\"}" | jq -r '.conversation_id')

echo "Conversation ID: $CONV_ID"

# 4. View conversation details
curl http://localhost:8000/api/v1/conversations/$CONV_ID | jq '.'

# 5. View extracted intelligence
curl http://localhost:8000/api/v1/intelligence | jq '.'

# 6. View analytics
curl http://localhost:8000/api/v1/analytics/overview | jq '.'
```

## Personas

### List Available Personas

```bash
curl http://localhost:8000/api/v1/personas
```

Response:
```json
[
  {
    "id": "persona-0",
    "name": "Ramesh Kumar",
    "age": 58,
    "occupation": "Retired Government Clerk",
    "location": "Pune, Maharashtra",
    "traits": {
      "tech_savvy": "low",
      "trust_level": "high",
      "risk_tolerance": "low"
    },
    "communication_style": "Polite, formal, uses simple language...",
    "is_active": true
  }
]
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found
- `500`: Internal Server Error

Error response format:
```json
{
  "detail": "Error message here"
}
```

## Rate Limiting

The API has a default rate limit of 60 requests per minute per client.

## WebSocket (Future)

Real-time updates will be available via WebSocket at:
```
ws://localhost:8000/ws/conversations
```

This is planned for future implementation.
