"""Quick test script to verify basic functionality."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.detection.detector import ScamDetector
from app.services.persona.generator import PersonaGenerator
from app.services.extraction.extractor import IntelligenceExtractor
from app.services.response.generator import ResponseGenerator
from app.services.mock_scammer.simulator import MockScammer, ScamScenario
from app.core.security import SafetyGuardrails
import asyncio

async def test_scam_detection():
    """Test scam detection."""
    print("\n=== Testing Scam Detection ===")
    detector = ScamDetector()
    
    test_messages = [
        "Congratulations! You won Rs. 25 lakhs in the lottery!",
        "Your bank account has been suspended. Click here to verify.",
        "Hello, this is from Microsoft. Your computer has a virus.",
        "Join our investment program for 300% returns!",
        "Just checking if you're available for coffee tomorrow"
    ]
    
    for msg in test_messages:
        result = await detector.detect_scam(msg)
        print(f"\nMessage: {msg[:60]}...")
        print(f"Is Scam: {result['is_scam']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Type: {result['scam_type']}")

async def test_persona_generation():
    """Test persona generation."""
    print("\n=== Testing Persona Generation ===")
    persona_gen = PersonaGenerator()
    
    persona = persona_gen.get_random_persona()
    print(f"\nPersona: {persona['name']}")
    print(f"Age: {persona['age']}")
    print(f"Occupation: {persona['occupation']}")
    print(f"Location: {persona['location']}")

async def test_intelligence_extraction():
    """Test intelligence extraction."""
    print("\n=== Testing Intelligence Extraction ===")
    extractor = IntelligenceExtractor()
    
    test_message = """
    Please transfer Rs. 5000 to:
    UPI: scammer@paytm
    Account: 1234567890
    IFSC: SBIN0001234
    Phone: +91-9876543210
    """
    
    extracted = extractor.extract_from_message(test_message)
    print(f"\nExtracted intelligence:")
    for artifact_type, values in extracted.items():
        print(f"  {artifact_type}: {values}")

async def test_mock_scammer():
    """Test mock scammer."""
    print("\n=== Testing Mock Scammer ===")
    scammer = MockScammer(ScamScenario.LOTTERY_PRIZE)
    
    opening = scammer.get_opening_message()
    print(f"\nScammer opening:\n{opening[:200]}...")
    
    response1 = scammer.respond("Really? How do I claim this?")
    print(f"\nScammer response 1:\n{response1[:200]}...")
    
    response2 = scammer.respond("What is your account number?")
    print(f"\nScammer response 2:\n{response2[:200]}...")

def test_safety_guardrails():
    """Test safety guardrails."""
    print("\n=== Testing Safety Guardrails ===")
    
    safe_responses = [
        "I'm interested! Please tell me more.",
        "What do I need to do next?"
    ]
    
    unsafe_responses = [
        "I will transfer the money now",
        "Let me install this software",
        "Here is my real password: abc123"
    ]
    
    print("\nSafe responses:")
    for resp in safe_responses:
        is_safe = SafetyGuardrails.validate_response(resp)
        print(f"  '{resp[:40]}...' - Safe: {is_safe}")
    
    print("\nUnsafe responses:")
    for resp in unsafe_responses:
        is_safe = SafetyGuardrails.validate_response(resp)
        print(f"  '{resp[:40]}...' - Safe: {is_safe}")

async def main():
    """Run all tests."""
    print("="*60)
    print("AGENTIC HONEYPOT - COMPONENT TESTS")
    print("="*60)
    
    await test_scam_detection()
    await test_persona_generation()
    await test_intelligence_extraction()
    await test_mock_scammer()
    test_safety_guardrails()
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
