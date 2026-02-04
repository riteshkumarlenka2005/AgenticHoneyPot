# 🕵️ Agentic HoneyPot for Scam Detection & Intelligence Extraction

> An autonomous AI-powered honeypot system that detects scam messages and actively engages scammers using believable personas to extract intelligence.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Next.js](https://img.shields.io/badge/next.js-14-black.svg)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Safety & Ethics](#safety--ethics)
- [Development](#development)
- [Contributing](#contributing)

## 🎯 Overview

The Agentic HoneyPot is a production-grade AI system designed to:

1. **Detect** scam messages using multi-layer detection (rules + LLM)
2. **Engage** scammers with believable AI personas
3. **Extract** intelligence (bank accounts, UPI IDs, phishing links)
4. **Waste** scammer time through strategic stalling
5. **Analyze** patterns and provide actionable insights

### Key Capabilities

- **Multi-Layer Scam Detection**: Rule-based + LLM-powered analysis
- **Autonomous Agent Loop**: Perceive → Think → Decide → Act → Learn
- **Believable Personas**: Tech-naive elderly, desperate job seekers, greedy investors
- **Intelligence Extraction**: Automated extraction of payment details, contact info, phishing links
- **Mock Scammer Simulator**: Built-in testing with realistic scam scenarios
- **Real-time Dashboard**: Live monitoring and analytics

## ✨ Features

### Backend (FastAPI + Python)

- **Scam Detection Service**
  - Rule-based pattern matching for common scam types
  - LLM-powered intent classification
  - Confidence scoring and scam type identification
  
- **Persona Generation**
  - Multiple pre-configured personas
  - Dynamic backstory generation
  - Communication style adaptation
  
- **Intelligence Extraction**
  - Regex-based extraction (UPI IDs, bank accounts, phone numbers, URLs)
  - Confidence scoring
  - Conversation steering to elicit information
  
- **Response Generation**
  - LLM-powered persona-consistent responses
  - Strategy-based adaptation (engage, extract, stall, exit)
  - Safety guardrails enforcement
  
- **Agent Orchestration**
  - Complete agent loop implementation
  - State management and memory
  - Automated decision-making

### Frontend (Next.js 14 + TypeScript)

- **Dashboard**: Real-time statistics, active conversations, time wasted
- **Conversations**: List and view all honeypot sessions
- **Intelligence**: View and export extracted artifacts
- **Analytics**: Scam type distribution, trends, metrics
- **Settings**: Configuration and persona management

### Mock Scammer Simulator

Test the honeypot with realistic scam scenarios:
- Lottery Prize scams
- Bank KYC Fraud
- Tech Support scams
- Investment Fraud
- Job Scams

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│  (Next.js 14 + TypeScript + Tailwind CSS)                   │
│                                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │Dashboard │ │  Convos  │ │  Intel   │ │Analytics │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
└───────────────────────────┬──────────────────────────────────┘
                            │ REST API + WebSocket
┌───────────────────────────┴──────────────────────────────────┐
│                      Backend (FastAPI)                        │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           Agent Orchestration Loop                   │    │
│  │  Perceive → Think → Decide → Act → Learn           │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Scam    │  │ Persona  │  │  Intel   │  │ Response │   │
│  │Detector  │  │Generator │  │Extractor │  │Generator │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            Safety Guardrails                          │   │
│  │  - No real money/credentials                         │   │
│  │  - Time/message limits                               │   │
│  │  - Response validation                               │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────────┬───────────────────────────────────┘
                            │
┌───────────────────────────┴───────────────────────────────────┐
│                    Data Layer                                  │
│  ┌──────────────┐              ┌──────────────┐              │
│  │  PostgreSQL  │              │    Redis     │              │
│  │   (Primary)  │              │   (Cache)    │              │
│  └──────────────┘              └──────────────┘              │
└────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- OpenAI API key (optional, for LLM features)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/riteshkumarlenka2005/AgenticHoneyPot.git
   cd AgenticHoneyPot
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Testing with Mock Scammer

```bash
# Start a lottery scam simulation
curl -X POST http://localhost:8000/api/v1/mock-scammer/start \
  -H "Content-Type: application/json" \
  -d '{"scenario": "lottery_prize"}'

# Response: {"session_id": "...", "initial_message": "Congratulations! You won..."}

# Send scammer message to honeypot
curl -X POST http://localhost:8000/api/v1/messages/incoming \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Congratulations! You won Rs 25,00,000...",
    "scammer_identifier": "test-scammer"
  }'

# View results in dashboard: http://localhost:3000/dashboard
```

## 📚 API Documentation

### Core Endpoints

#### Messages
```http
POST /api/v1/messages/incoming
```
Receive and process incoming scam messages. Returns honeypot response and detection results.

#### Conversations
```http
GET  /api/v1/conversations
GET  /api/v1/conversations/{id}
```
List and view conversation details.

#### Intelligence
```http
GET  /api/v1/intelligence
GET  /api/v1/intelligence/export?format=json|csv
```
Access and export extracted intelligence artifacts.

#### Analytics
```http
GET  /api/v1/analytics/overview
GET  /api/v1/analytics/scam-types
GET  /api/v1/analytics/timeline
```
Retrieve system analytics and metrics.

#### Mock Scammer (Testing)
```http
POST /api/v1/mock-scammer/start
POST /api/v1/mock-scammer/respond
GET  /api/v1/mock-scammer/scenarios
```
Simulate realistic scammer behavior for testing.

Full API documentation available at: http://localhost:8000/docs

## 🛡️ Safety & Ethics

### Safety Guardrails (CRITICAL)

This system implements strict safety measures:

1. **Never send real money or cryptocurrency**
2. **Never provide real personal information**
3. **Never click or access external links**
4. **Never install any software**
5. **Never share real OTPs or passwords**
6. **Operate only in authorized/simulated environments**

### Ethical Guidelines

- **Purpose**: This tool is for research, education, and defensive security only
- **Legal**: Only use in jurisdictions where honeypot operations are legal
- **Privacy**: All extracted data should be handled according to privacy laws
- **Disclosure**: Be transparent about the system's operation with stakeholders
- **Limits**: Respect conversation duration and message limits

### Hard Limits Enforced

- Max conversation duration: 3600 seconds (1 hour)
- Max messages per conversation: 100
- Minimum scam confidence to engage: 0.5 (50%)
- Response validation against forbidden patterns

## 💻 Development

### Project Structure

```
AgenticHoneyPot/
├── backend/
│   ├── app/
│   │   ├── api/routes/          # API endpoints
│   │   ├── core/                # Agent logic, security
│   │   ├── services/            # Business logic
│   │   ├── models/              # Database models
│   │   └── main.py              # FastAPI app
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js 14 pages
│   │   ├── components/          # React components
│   │   └── lib/                 # API client, utils
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

### Running Locally

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Environment Variables

```bash
# Backend
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/honeypot
REDIS_URL=redis://redis:6379/0
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
SECRET_KEY=your-secret-key

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## ⚠️ Disclaimer

This software is provided for educational and defensive security research purposes only. Users are responsible for ensuring their use complies with all applicable laws and regulations. The authors assume no liability for misuse of this system.

---

**Built with ❤️ for cybersecurity research and scam prevention**
## 🆕 New Features

### Advanced Backend Capabilities

#### Database & Persistence
- **Alembic Migrations**: Proper database schema management with async PostgreSQL support
- **Database Service Layer**: Clean separation of data access with CRUD operations for all models
- **Persistent Storage**: All conversations, messages, and intelligence stored in database

#### Real-Time Communication
- **WebSocket Support**: Real-time updates for new messages, intelligence extraction, and analytics
- **Connection Manager**: Handles multiple WebSocket clients with subscription management
- **Event Broadcasting**: Targeted updates to conversation subscribers and dashboard

#### Intelligence & Security
- **STIX 2.1 Export**: Industry-standard threat intelligence format export
- **Prompt Injection Protection**: Multi-layer guardrails for input/output filtering
- **Instruction Hierarchy**: Prioritization system ensuring safety rules are never bypassed
- **RAG Integration**: Policy-based checking using retrieval-augmented generation
- **Behavioral Context**: WHOIS lookup, URL expansion, and redirect chain tracing

#### LLM Provider Abstraction
- **Multi-Provider Support**: OpenAI GPT-4 and Google Gemini
- **Factory Pattern**: Easy switching between providers
- **Auto-Detection**: Automatically uses available provider based on API keys

#### Advanced Agent Features
- **Hidden Markov Model**: Scam stage prediction (initial contact → building trust → urgency → payment request)
- **IDR Metrics**: Information Disclosure Rate and Speed calculations
- **Efficiency Scoring**: Combined metrics for honeypot effectiveness

#### Caching & Performance
- **Redis Integration**: Caching layer for frequently accessed data
- **Cache Invalidation**: Smart invalidation on conversation updates
- **Async Operations**: Full async support for high concurrency

### Enhanced Frontend Features

#### New Pages
- **Conversation Detail View** (`/conversations/[id]`): Full message thread with timeline and intelligence sidebar
- **Persona Management** (`/settings/personas`): Create, edit, and manage AI personas
- **Intelligence Export UI**: Download intelligence as JSON, CSV, or STIX format

#### Improved Analytics
- **Real-Time Updates**: WebSocket integration for live dashboard updates
- **Enhanced Metrics**: IDR, IDS, and efficiency scores
- **Better Visualizations**: Improved charts for scam type distribution and timeline

### Security Features

#### Input Protection
- Prompt injection detection and blocking
- Suspicious pattern recognition
- Context stuffing prevention
- Instruction hijacking prevention

#### Output Validation
- AI self-reference removal
- Persona consistency checking
- Credential leak prevention
- Character break detection

### Export Formats

#### JSON
Standard JSON export with all intelligence artifacts and conversation metadata.

#### CSV
Spreadsheet-compatible format for data analysis.

#### STIX 2.1
Industry-standard Structured Threat Information Expression format including:
- Threat actors (scammers)
- Indicators (extracted artifacts)
- Observed data
- Attack patterns
- Comprehensive threat reports

## 📊 Metrics & Analytics

### Information Disclosure Rate (IDR)
Measures the efficiency of intelligence extraction:
```
IDR = (Intelligence Artifacts) / (Total Messages)
```

### Information Disclosure Speed (IDS)
Measures how quickly intelligence is extracted:
```
IDS = (Intelligence Artifacts) / (Time in Minutes)
```

### Efficiency Score
Combined metric incorporating IDR, IDS, and time wasted:
```
Efficiency = (IDR × 0.4 + IDS × 0.3 + TimeWasted × 0.3) × 100
```

## 🔧 Configuration

### Database
```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/honeypot
```

### Redis
```bash
REDIS_URL=redis://localhost:6379/0
```

### LLM Providers
```bash
# OpenAI (default)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview

# Google Gemini (alternative)
GOOGLE_API_KEY=...
```

## 🔌 API Endpoints

### WebSocket
```
WS /api/v1/ws
```
Real-time updates for conversations and intelligence.

### Intelligence
```
GET    /api/v1/intelligence
GET    /api/v1/intelligence/export?format=json|csv|stix
PATCH  /api/v1/intelligence/{id}/validate
```

### Conversations
```
GET /api/v1/conversations
GET /api/v1/conversations/{id}
```

See [API_EXAMPLES.md](API_EXAMPLES.md) for detailed usage examples.

## 🏗️ Architecture Updates

The system now follows a clean layered architecture:

```
Frontend (Next.js) 
    ↓ REST API + WebSocket
Backend (FastAPI)
    ↓ Service Layer
    ├─ LLM Providers (OpenAI/Gemini)
    ├─ RAG Services (Policy Store + Retriever)
    ├─ Context Services (WHOIS, URL Expansion)
    ├─ Guardrails (Input/Output Filtering)
    ├─ Detection (HMM, Rules, LLM Analysis)
    └─ Metrics (IDR, IDS, Efficiency)
    ↓ Data Layer
    ├─ PostgreSQL (Primary Storage)
    └─ Redis (Cache)
```

