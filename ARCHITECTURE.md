# System Architecture

## Overview

The Agentic HoneyPot is a full-stack application designed to autonomously detect and engage with scammers, extracting intelligence while wasting their time.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                 │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    Next.js 14 Frontend                        │  │
│  │  • Dashboard  • Conversations  • Intelligence  • Analytics    │  │
│  │  • TypeScript • Tailwind CSS  • Real-time Updates            │  │
│  └──────────────────────────────────────────────────────────────┘  │
└──────────────────────────┬───────────────────────────────────────────┘
                           │ HTTP/REST + WebSocket
┌──────────────────────────┴───────────────────────────────────────────┐
│                        API GATEWAY LAYER                             │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                     FastAPI Application                       │  │
│  │  • RESTful API     • CORS Middleware  • Rate Limiting        │  │
│  │  • WebSocket       • Request Validation                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
└──────────────────────────┬───────────────────────────────────────────┘
                           │
┌──────────────────────────┴───────────────────────────────────────────┐
│                      BUSINESS LOGIC LAYER                            │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │              🤖 Agent Orchestration Loop                    │    │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌────────┐  │    │
│  │  │ PERCEIVE  │→ │  THINK    │→ │  DECIDE   │→ │  ACT   │  │    │
│  │  │  Detect   │  │  Analyze  │  │  Strategy │  │ Respond│  │    │
│  │  │  Scam     │  │  Context  │  │  Select   │  │ Generate│ │    │
│  │  └───────────┘  └───────────┘  └───────────┘  └────────┘  │    │
│  │                                                 ↓            │    │
│  │                                           ┌─────────┐        │    │
│  │                                           │  LEARN  │        │    │
│  │                                           │ Update  │        │    │
│  │                                           │  State  │        │    │
│  │                                           └─────────┘        │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │   Scam       │  │   Persona    │  │ Intelligence │             │
│  │  Detection   │  │  Generation  │  │  Extraction  │             │
│  │  Service     │  │  Service     │  │  Service     │             │
│  │              │  │              │  │              │             │
│  │ • Rule-based │  │ • Templates  │  │ • Patterns   │             │
│  │ • ML/LLM     │  │ • Backstory  │  │ • Validation │             │
│  │ • Confidence │  │ • Style      │  │ • Confidence │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │  Response    │  │    Mock      │  │   Safety     │             │
│  │  Generation  │  │   Scammer    │  │  Guardrails  │             │
│  │  Service     │  │  Simulator   │  │              │             │
│  │              │  │              │  │              │             │
│  │ • Phase-aware│  │ • Scenarios  │  │ • Hard Limits│             │
│  │ • Persona    │  │ • Realistic  │  │ • Validation │             │
│  │ • Strategy   │  │ • Testing    │  │ • Sanitize   │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
└──────────────────────────┬───────────────────────────────────────────┘
                           │
┌──────────────────────────┴───────────────────────────────────────────┐
│                       DATA ACCESS LAYER                              │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                SQLAlchemy ORM + Pydantic                      │  │
│  │  • Models  • Schemas  • Validation  • Serialization          │  │
│  └──────────────────────────────────────────────────────────────┘  │
└──────────────────────────┬───────────────────────────────────────────┘
                           │
┌──────────────────────────┴───────────────────────────────────────────┐
│                     PERSISTENCE LAYER                                │
│  ┌─────────────────────────┐      ┌─────────────────────────┐       │
│  │   PostgreSQL Database   │      │    Redis Cache          │       │
│  │  • Conversations        │      │  • Session Data         │       │
│  │  • Messages             │      │  • Real-time Updates    │       │
│  │  • Intelligence         │      │  • Agent State          │       │
│  │  • Personas             │      │                         │       │
│  │  • Scammer Profiles     │      │                         │       │
│  └─────────────────────────┘      └─────────────────────────┘       │
└───────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Frontend (Next.js 14)

**Technology Stack:**
- Next.js 14 with App Router
- TypeScript for type safety
- Tailwind CSS for styling
- React 18 for UI components

**Pages:**
- `/dashboard` - Real-time statistics and activity feed
- `/conversations` - List and detail views of conversations
- `/intelligence` - Extracted artifacts and export
- `/analytics` - Charts and metrics
- `/settings` - Configuration and personas

**Key Features:**
- Server-side rendering for SEO
- Client-side state management
- Real-time updates via polling
- Responsive design (mobile, tablet, desktop)

### 2. Backend (FastAPI)

**Technology Stack:**
- Python 3.11+
- FastAPI for REST API
- SQLAlchemy for ORM
- Pydantic for validation
- Asyncio for concurrency

**API Routes:**
- `/api/v1/conversations/*` - Conversation management
- `/api/v1/intelligence/*` - Intelligence retrieval
- `/api/v1/analytics/*` - Analytics and metrics
- `/api/v1/personas/*` - Persona management
- `/api/v1/mock-scammer/*` - Testing simulator

**Key Features:**
- Automatic API documentation (OpenAPI/Swagger)
- Request/response validation
- CORS middleware
- Error handling
- Logging

### 3. Agent Orchestration

**Agent Loop:**
```python
PERCEIVE: Receive scammer message
    ↓
THINK: Analyze with ScamDetector
    ↓
DECIDE: Determine conversation phase & strategy
    ↓
ACT: Generate response with persona
    ↓
LEARN: Update state & extract intelligence
```

**Conversation Phases:**
1. **Detecting** - Initial scam detection
2. **Engaging** - Build trust with scammer
3. **Extracting** - Actively request payment details
4. **Stalling** - Delay while maintaining engagement

**State Management:**
- Conversation state per scammer
- Persona consistency
- Extraction tracking
- Phase transitions

### 4. Services

#### Scam Detection Service
- **Rule-Based**: Keyword matching, pattern recognition
- **Confidence Scoring**: 0.0 - 1.0 scale
- **Type Classification**: lottery, bank_fraud, tech_support, investment, job_scam
- **Threshold**: 0.3 (adjustable)

#### Persona Generation Service
- **Templates**: 3 predefined personas
- **Attributes**: Name, age, occupation, location, traits, backstory
- **Type Matching**: Persona selection based on scam type
- **Consistency**: Maintains character throughout conversation

#### Intelligence Extraction Service
- **Pattern Matching**:
  - UPI IDs: `user@provider`
  - Phone: `+91-XXXXXXXXXX` or `XXXXXXXXXX`
  - IFSC Codes: `ABCD0123456`
  - Bank Accounts: `9-18 digits`
  - URLs: `http(s)://...`
  - Emails: `user@domain.com`
- **Deduplication**: Removes duplicate artifacts
- **Validation**: Confidence scoring

#### Response Generation Service
- **Phase-Based**: Different strategies per phase
- **Persona-Aware**: Maintains character voice
- **Extraction Focus**: Steers toward intelligence gathering
- **Safety Validated**: All responses checked by guardrails

### 5. Mock Scammer Simulator

**Scenarios:**
- Lottery Prize
- Bank KYC Fraud
- Tech Support
- Investment Fraud
- Job Scam

**Behavior:**
- Realistic opening messages
- Progressive information disclosure
- Pressure tactics for stalling victims
- Payment detail revelation on request

### 6. Safety Guardrails

**Hard Limits:**
- ❌ Never send real money
- ❌ Never provide real personal info
- ❌ Never click external links
- ❌ Never install software
- ❌ Never share real OTPs/passwords
- ❌ Never engage in illegal activity

**Implementation:**
- Pre-response validation
- Keyword blocking
- Action prevention
- Response sanitization

### 7. Database Schema

**Conversations:**
```sql
id, scammer_identifier, persona_id, status, scam_type,
detection_confidence, started_at, last_activity,
total_duration_seconds, metadata
```

**Messages:**
```sql
id, conversation_id, sender_type, content, timestamp, analysis
```

**Intelligence:**
```sql
id, conversation_id, artifact_type, value,
confidence, extracted_at, validated
```

**Personas:**
```sql
id, name, age, occupation, location, traits,
communication_style, backstory, is_active
```

**Scammer Profiles:**
```sql
id, identifier, known_aliases, first_seen, last_seen,
total_conversations, linked_intelligence, threat_score
```

## Data Flow

### Incoming Scam Message Flow

```
1. POST /api/v1/conversations/incoming
   ├─ Validate request
   ├─ Find/create conversation
   └─ Save scammer message
       ↓
2. Agent.process_message()
   ├─ ScamDetector.detect_scam()
   ├─ Update conversation state
   ├─ Select/maintain persona
   └─ IntelligenceExtractor.extract()
       ↓
3. ResponseGenerator.generate()
   ├─ Determine phase
   ├─ Generate response
   └─ SafetyGuardrails.validate()
       ↓
4. Save honeypot message
5. Return response to API
```

### Analytics Query Flow

```
1. GET /api/v1/analytics/overview
   ├─ Query database (SQLAlchemy)
   ├─ Aggregate statistics
   └─ Return JSON
       ↓
2. Frontend receives data
   ├─ Update state
   ├─ Re-render components
   └─ Display metrics
```

## Deployment

### Docker Compose Architecture

```yaml
services:
  db:       PostgreSQL 15
  redis:    Redis 7
  backend:  FastAPI app
  frontend: Next.js app
```

**Network:**
- Backend ↔ Database: Internal network
- Backend ↔ Redis: Internal network
- Frontend ↔ Backend: HTTP/REST
- Client ↔ Frontend: HTTP/HTTPS

**Volumes:**
- `postgres_data`: Database persistence
- `./backend/app`: Backend hot reload
- `./frontend/src`: Frontend hot reload

## Security Considerations

1. **Input Validation**: All API inputs validated with Pydantic
2. **SQL Injection**: Protected by SQLAlchemy ORM
3. **XSS Prevention**: React auto-escapes output
4. **CORS**: Configured for specific origins
5. **Rate Limiting**: Planned for production
6. **Safety Guardrails**: Prevents harmful actions

## Performance Characteristics

**Expected Latency:**
- Scam detection: < 100ms
- Response generation: < 500ms
- API response: < 1s
- Frontend page load: < 2s

**Scalability:**
- Horizontal scaling: Backend can run multiple instances
- Database: PostgreSQL supports read replicas
- Caching: Redis for frequently accessed data
- WebSocket: Socket.io for real-time features

## Future Enhancements

1. **LLM Integration**: GPT-4 for advanced detection & responses
2. **ML Classification**: Train models on scam data
3. **WebSocket**: Real-time dashboard updates
4. **Image Analysis**: OCR for screenshot scams
5. **Multi-language**: Support for multiple languages
6. **Advanced Analytics**: ML-powered insights
7. **Threat Intelligence**: Integration with external DBs
8. **Automated Reporting**: Generate scam reports
