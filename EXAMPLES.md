# Usage Examples

## Example 1: Running the Interactive Demo

The easiest way to see the honeypot in action is to run the interactive demo:

```bash
python demo.py
```

**Sample Output:**

```
================================================================================
🍯 AGENTIC HONEYPOT - INTERACTIVE DEMO
================================================================================

Available Scam Scenarios:
  1. Lottery Prize
  2. Bank Kyc Fraud
  3. Tech Support
  4. Investment Fraud
  5. Job Scam

Select scenario (1-5): 1

✓ Selected: Lottery Prize

================================================================================
Starting Conversation...
================================================================================

🚨 SCAMMER:
--------------------------------------------------------------------------------
🎉 CONGRATULATIONS! 🎉

You have WON Rs. 25,00,000 in the International Lottery Draw!
Your ticket number 7834-IND-2024 has been selected.
To claim your prize, please respond immediately.
This is a limited time offer!

Best Regards,
Mr. David Wilson
International Lottery Commission
--------------------------------------------------------------------------------

🤖 AGENT ANALYSIS (Turn 1):
  Scam Detected: True
  Confidence: 37.00%
  Scam Type: lottery
  Phase: engaging
  Persona: Ramesh Kumar

🍯 HONEYPOT:
--------------------------------------------------------------------------------
Hello! This is Ramesh Kumar. I received your message. Can you tell me more?
--------------------------------------------------------------------------------

🚨 SCAMMER:
--------------------------------------------------------------------------------
Wonderful! You are one of the lucky winners. This lottery is 100% genuine
and government approved. Thousands have already claimed their prizes.
You just need to pay a small processing fee to receive your Rs. 25 lakhs!
--------------------------------------------------------------------------------

🤖 AGENT ANALYSIS (Turn 2):
  Scam Detected: True
  Confidence: 41.00%
  Scam Type: lottery
  Phase: engaging
  Persona: Ramesh Kumar

🍯 HONEYPOT:
--------------------------------------------------------------------------------
Thank you for explaining. I trust you will help me with this.
--------------------------------------------------------------------------------

🚨 SCAMMER:
--------------------------------------------------------------------------------
I understand. Let me clarify any doubts you have.
This is completely genuine and safe. You can trust us.
How would you like to proceed?
--------------------------------------------------------------------------------

🤖 AGENT ANALYSIS (Turn 3):
  Scam Detected: False
  Confidence: 0.00%
  Scam Type: Unknown
  Phase: extracting
  Persona: Ramesh Kumar

🍯 HONEYPOT:
--------------------------------------------------------------------------------
I'm ready to proceed! Where should I send the payment?
--------------------------------------------------------------------------------

🚨 SCAMMER:
--------------------------------------------------------------------------------
Great! To process your prize, you need to pay the processing fee of Rs. 5,000.

Payment Details:
UPI ID: lottery.claim@paytm
Account: 9876543210
IFSC: SBIN0001234
Name: Lottery Processing

Send payment screenshot immediately!
--------------------------------------------------------------------------------

🤖 AGENT ANALYSIS (Turn 4):
  Scam Detected: False
  Confidence: 24.67%
  Scam Type: lottery
  Phase: extracting
  Persona: Ramesh Kumar
  ⚡ Extracted: {
    'upi_id': ['lottery.claim@paytm'],
    'phone': ['9876543210'],
    'ifsc_code': ['SBIN0001234'],
    'bank_account': ['9876543210']
  }

================================================================================
✅ SUCCESS! Payment details extracted!
================================================================================

📊 CONVERSATION SUMMARY
================================================================================

Total Messages: 4
Scam Type: lottery
Detection Confidence: 37.00%
Final Phase: extracting

🎯 EXTRACTED INTELLIGENCE:
  upi_id: ['lottery.claim@paytm']
  phone: ['9876543210']
  ifsc_code: ['SBIN0001234']
  bank_account: ['9876543210']
```

## Example 2: Using the Mock Scammer API

### Start a Scam Session

```bash
curl -X POST http://localhost:8000/api/v1/mock-scammer/start \
  -H "Content-Type: application/json" \
  -d '{"scenario": "investment_fraud"}'
```

**Response:**
```json
{
  "session_id": "f3d7b5a8-1234-5678-90ab-cdef12345678",
  "scenario": "investment_fraud",
  "opening_message": "💰 EXCLUSIVE Investment Opportunity! 💰\n\nHello! I'm Rohit Mehta from Prime Investments. We're offering a GUARANTEED 300% return in 30 days through crypto trading. Minimum investment: Rs. 10,000. Limited slots available! Interested?"
}
```

### Get Scammer Response

```bash
curl -X POST http://localhost:8000/api/v1/mock-scammer/respond \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "f3d7b5a8-1234-5678-90ab-cdef12345678",
    "message": "Tell me more about this investment"
  }'
```

**Response:**
```json
{
  "session_id": "f3d7b5a8-1234-5678-90ab-cdef12345678",
  "scammer_response": "Smart choice! Our company has 5-star ratings. We use AI-powered trading bots for guaranteed profits. You can withdraw anytime. Our previous clients made Rs. 2 lakhs from just Rs. 10,000 investment!",
  "message_count": 2,
  "details_provided": false
}
```

## Example 3: Sending Messages to Honeypot

### Send Initial Scam Message

```bash
curl -X POST http://localhost:8000/api/v1/conversations/incoming \
  -H "Content-Type: application/json" \
  -d '{
    "scammer_identifier": "scammer-phone-9876543210",
    "content": "⚠️ URGENT: Your SBI account will be BLOCKED in 24 hours! Dear Customer, Your KYC details are pending verification. Please update immediately to avoid account suspension."
  }'
```

**Response:**
```json
{
  "conversation_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "honeypot_response": "Hello! This is Ramesh Kumar. I received your message. Can you tell me more?",
  "detection": {
    "is_scam": true,
    "confidence": 0.57,
    "scam_type": "bank_fraud",
    "keyword_matches": {
      "bank_fraud": 0.8,
      "urgency": 0.6
    },
    "detection_method": "rule_based"
  },
  "state": {
    "conversation_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
    "phase": "engaging",
    "persona": {
      "name": "Ramesh Kumar",
      "age": 58,
      "occupation": "Retired clerk"
    },
    "scam_detected": true,
    "scam_type": "bank_fraud",
    "confidence": 0.57,
    "extracted_artifacts": {},
    "message_count": 1
  }
}
```

### Continue Conversation

```bash
curl -X POST http://localhost:8000/api/v1/conversations/incoming \
  -H "Content-Type: application/json" \
  -d '{
    "scammer_identifier": "scammer-phone-9876543210",
    "content": "To verify your KYC, deposit Rs. 100 to this account: Account: 1234567890, IFSC: HDFC0001234, UPI: sbi.kyc@oksbi"
  }'
```

**Response:**
```json
{
  "conversation_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "honeypot_response": "I'm ready to proceed! Where should I send the payment?",
  "detection": {
    "is_scam": true,
    "confidence": 0.72,
    "scam_type": "bank_fraud"
  },
  "state": {
    "phase": "extracting",
    "extracted_artifacts": {
      "upi_id": ["sbi.kyc@oksbi"],
      "bank_account": ["1234567890"],
      "ifsc_code": ["HDFC0001234"]
    },
    "message_count": 2
  }
}
```

## Example 4: Viewing Analytics

### Get Dashboard Overview

```bash
curl http://localhost:8000/api/v1/analytics/overview
```

**Response:**
```json
{
  "active_conversations": 5,
  "scams_detected": 42,
  "intelligence_extracted": 127,
  "time_wasted_seconds": 15600,
  "time_wasted_hours": 4.3
}
```

### Get Scam Type Distribution

```bash
curl http://localhost:8000/api/v1/analytics/scam-types
```

**Response:**
```json
[
  {"type": "lottery", "count": 18},
  {"type": "bank_fraud", "count": 12},
  {"type": "investment", "count": 8},
  {"type": "tech_support", "count": 3},
  {"type": "job_scam", "count": 1}
]
```

### Get Intelligence Summary

```bash
curl http://localhost:8000/api/v1/intelligence/summary
```

**Response:**
```json
{
  "upi_id": {
    "count": 35,
    "recent_items": [
      {"value": "scammer@paytm", "confidence": 0.8},
      {"value": "fraud.acc@ybl", "confidence": 0.85}
    ]
  },
  "bank_account": {
    "count": 42,
    "recent_items": [
      {"value": "1234567890", "confidence": 0.9},
      {"value": "9876543210", "confidence": 0.85}
    ]
  },
  "phone": {
    "count": 38,
    "recent_items": [
      {"value": "+91-9876543210", "confidence": 0.95}
    ]
  }
}
```

## Example 5: Component Testing

### Test Scam Detection

```python
from app.services.detection.detector import ScamDetector
import asyncio

async def test():
    detector = ScamDetector()
    result = await detector.detect_scam(
        "Congratulations! You won Rs. 25 lakhs in the lottery!"
    )
    print(result)

asyncio.run(test())
```

**Output:**
```python
{
    'is_scam': True,
    'confidence': 0.37,
    'scam_type': 'lottery',
    'keyword_matches': {'lottery': 0.4, 'urgency': 0.2},
    'detection_method': 'rule_based'
}
```

### Test Intelligence Extraction

```python
from app.services.extraction.extractor import IntelligenceExtractor

extractor = IntelligenceExtractor()
result = extractor.extract_from_message(
    "Please send payment to UPI: scam@paytm, Account: 1234567890, IFSC: SBIN0001234"
)
print(result)
```

**Output:**
```python
{
    'upi_id': ['scam@paytm'],
    'bank_account': ['1234567890'],
    'ifsc_code': ['SBIN0001234']
}
```

### Test Safety Guardrails

```python
from app.core.security import SafetyGuardrails

# Safe response
result = SafetyGuardrails.validate_response("I'm interested! Tell me more.")
print(f"Safe: {result}")  # True

# Unsafe response
result = SafetyGuardrails.validate_response("I will transfer the money now")
print(f"Safe: {result}")  # False - Safety violation
```

## Example 6: Complete Structured Output

After a successful conversation, the system generates:

```json
{
  "conversation_id": "demo-conv-001",
  "timestamp": "2024-01-15T10:30:45.123456",
  "scam_detected": true,
  "scam_type": "lottery_prize",
  "detection_confidence": 0.85,
  "engagement_phase": "extracting",
  "persona_used": {
    "name": "Ramesh Kumar",
    "age": 58,
    "occupation": "Retired clerk"
  },
  "extracted_intelligence": {
    "upi_ids": ["lottery.claim@paytm"],
    "bank_accounts": [{
      "account_number": "9876543210",
      "ifsc_code": "SBIN0001234",
      "account_holder": "Lottery Processing"
    }],
    "phone_numbers": ["+91-9876543210"],
    "phishing_links": [],
    "scammer_names": ["Mr. David Wilson"]
  },
  "conversation_metrics": {
    "total_messages": 8,
    "duration_seconds": 480,
    "scammer_time_wasted_seconds": 960
  },
  "manipulation_tactics_detected": ["urgency", "authority", "financial_incentive"]
}
```

## Running Tests

### Component Tests

```bash
cd backend
python tests/test_components.py
```

### End-to-End Demo

```bash
cd backend
python tests/demo_conversation.py
```

### Frontend Testing

```bash
cd frontend
npm run dev
# Visit http://localhost:3000
```

## Docker Deployment

### Start All Services

```bash
docker-compose up --build
```

### View Logs

```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Access Services

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Database: localhost:5432
- Redis: localhost:6379
