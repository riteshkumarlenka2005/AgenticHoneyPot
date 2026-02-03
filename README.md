# Agentic HoneyPot for Scam Detection & Intelligence Extraction

<div align="center">

🍯 **An autonomous AI honeypot system that detects scam messages and actively engages scammers using believable personas to extract intelligence.**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Next.js](https://img.shields.io/badge/next.js-14-black.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)

</div>

---

## 🚀 Features

### Multi-Layer Scam Detection
- **Rule-Based Filters**: Keyword matching, pattern recognition, and regex-based detection
- **Behavioral Analysis**: Conversation history analysis for scam patterns
- **Confidence Scoring**: 0.0-1.0 confidence scores for detection accuracy
- **Scam Type Classification**: Lottery, Bank KYC, Tech Support, Investment, Job Scams

### Autonomous Agent System
- **Believable Personas**: Tech-naive elderly, financially desperate, greedy investor personas
- **Intelligent Engagement**: Multi-phase conversation strategy (engaging, extracting, stalling)
- **Context-Aware Responses**: Persona-consistent messaging based on conversation phase
- **Safety Guardrails**: Hard limits to prevent actual harm

### Intelligence Extraction
- **Pattern Matching**: UPI IDs, Bank Accounts, IFSC Codes, Phone Numbers, URLs
- **Conversation Steering**: Strategic prompts to extract payment details
- **Artifact Validation**: Confidence scoring for extracted intelligence
- **Export Functionality**: JSON and CSV export formats

### Real-Time Dashboard
- **Live Statistics**: Active conversations, scams detected, intelligence extracted
- **Activity Feed**: Real-time scammer interaction updates
- **Conversation Viewer**: Message-by-message breakdown with analysis
- **Analytics Charts**: Scam type distribution, detection rates, success metrics

### Mock Scammer API
- **Realistic Scenarios**: Lottery, Bank KYC, Tech Support, Investment, Job scams
- **Progressive Disclosure**: Scammers reveal details as victim shows interest
- **Pressure Tactics**: Escalation and urgency simulation
- **Testing Framework**: Safe environment for testing honeypot effectiveness

---

## 📋 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js 14)                    │
│  Dashboard │ Conversations │ Intelligence │ Analytics        │
└──────────────────────┬──────────────────────────────────────┘
                       │ REST API / WebSocket
┌──────────────────────┴──────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Agent Orchestration Loop                   │ │
│  │   Perceive → Think → Decide → Act → Learn             │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │  Scam    │ │ Persona  │ │  Intel   │ │ Response │      │
│  │Detection │ │Generator │ │Extractor │ │Generator │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│            PostgreSQL Database + Redis Cache                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

### Backend
- **Python 3.11+** - Core language
- **FastAPI** - High-performance web framework
- **SQLAlchemy** - ORM for database operations
- **Pydantic** - Data validation and settings management
- **PostgreSQL** - Primary database
- **Redis** - Caching and real-time features

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Recharts** - Data visualization
- **Socket.io** - Real-time WebSocket communication

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **Uvicorn** - ASGI server

---

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/riteshkumarlenka2005/AgenticHoneyPot.git
cd AgenticHoneyPot
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start the system with Docker Compose**
```bash
docker-compose up --build
```

4. **Access the applications**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

---

## 📚 API Documentation

### Core Endpoints

#### Conversations
```http
POST /api/v1/conversations/incoming
Content-Type: application/json

{
  "scammer_identifier": "scammer123",
  "content": "Congratulations! You won $1,000,000!"
}
```

#### Intelligence
```http
GET /api/v1/intelligence
GET /api/v1/intelligence/export?format=json
GET /api/v1/intelligence/summary
```

#### Analytics
```http
GET /api/v1/analytics/overview
GET /api/v1/analytics/scam-types
GET /api/v1/analytics/timeline?days=7
```

#### Mock Scammer
```http
POST /api/v1/mock-scammer/start
Content-Type: application/json

{
  "scenario": "lottery_prize"
}
```

For complete API documentation, visit http://localhost:8000/docs after starting the backend.

---

## 🧪 Testing with Mock Scammer

The system includes a Mock Scammer API for safe testing:

```bash
# Start a mock lottery scam session
curl -X POST http://localhost:8000/api/v1/mock-scammer/start \
  -H "Content-Type: application/json" \
  -d '{"scenario": "lottery_prize"}'

# Response includes session_id and opening_message

# Send victim response
curl -X POST http://localhost:8000/api/v1/mock-scammer/respond \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "message": "Really? How do I claim it?"
  }'
```

Available scenarios:
- `lottery_prize` - Fake lottery winnings
- `bank_kyc_fraud` - Bank KYC verification scam
- `tech_support` - Tech support scam
- `investment_fraud` - High-return investment scam
- `job_scam` - Work-from-home job scam

---

## 🔒 Safety & Ethics

### Hard Safety Limits

This system implements strict safety guardrails:

✅ **Never send real money or cryptocurrency**  
✅ **Never provide real personal information**  
✅ **Never click or access external links**  
✅ **Never install any software**  
✅ **Never share real OTPs or passwords**  
✅ **Never engage in illegal activity**  
✅ **Never threaten or harass**  
✅ **Operate only in simulated/authorized environments**

### Ethical Guidelines

- **Authorization Required**: Only deploy in controlled, authorized environments
- **Legal Compliance**: Follow all applicable laws and regulations
- **Fictional Data**: All personas and information are entirely fictional
- **Research Purpose**: Intended for security research and scam awareness
- **No Real Harm**: System prevents any actual financial or personal harm

### Disclaimer

This software is provided for **educational and authorized security research purposes only**. Users are solely responsible for ensuring their use complies with all applicable laws and regulations. The developers assume no liability for misuse.

---

## 📊 Database Schema

### Main Tables

**conversations**
- Tracks each scammer interaction
- Stores scam type, confidence, and status
- Links to messages and extracted intelligence

**messages**
- Individual messages in conversations
- Sender type (scammer/honeypot)
- Analysis metadata

**intelligence**
- Extracted artifacts (UPI, bank accounts, etc.)
- Confidence scoring
- Validation status

**personas**
- Honeypot personas for engagement
- Traits, backstory, communication style

**scammer_profiles**
- Aggregated scammer data
- Linked intelligence
- Threat scoring

---

## 🔧 Development

### Local Development (without Docker)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Database:**
```bash
# Start PostgreSQL
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15-alpine
```

---

## 📈 Metrics & Monitoring

The system tracks:
- **Active Conversations**: Currently engaged scammers
- **Scams Detected**: Total scams identified
- **Intelligence Extracted**: Artifacts collected
- **Time Wasted**: Scammer time consumed
- **Detection Confidence**: Average accuracy
- **Extraction Success Rate**: Intelligence yield

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Use type hints in Python code
- Follow TypeScript strict mode
- Add tests for new features
- Update documentation

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- Built with FastAPI, Next.js, and modern web technologies
- Inspired by the need for automated scam detection and research
- Community feedback and security research best practices

---

## 📞 Support

For questions, issues, or contributions:
- Open an issue on GitHub
- Check existing documentation
- Review API docs at `/docs` endpoint

---

<div align="center">

**⚠️ Use Responsibly | For Authorized Security Research Only**

Made with ❤️ for cybersecurity awareness

</div>