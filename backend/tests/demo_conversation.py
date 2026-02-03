"""End-to-end demo of honeypot engaging with mock scammer."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.detection.detector import ScamDetector
from app.services.persona.generator import PersonaGenerator
from app.services.extraction.extractor import IntelligenceExtractor
from app.services.response.generator import ResponseGenerator
from app.core.agent.loop import HoneypotAgent
from app.services.mock_scammer.simulator import MockScammer, ScamScenario
import asyncio
import json

async def run_demo_conversation():
    """Run a full conversation between honeypot and mock scammer."""
    print("\n" + "="*80)
    print("AGENTIC HONEYPOT - END-TO-END DEMO")
    print("="*80)
    
    # Initialize components
    detector = ScamDetector()
    persona_gen = PersonaGenerator()
    extractor = IntelligenceExtractor()
    response_gen = ResponseGenerator()
    agent = HoneypotAgent(detector, persona_gen, extractor, response_gen)
    
    # Create mock scammer
    scammer = MockScammer(ScamScenario.LOTTERY_PRIZE)
    conversation_id = "demo-conv-001"
    
    print("\n🎭 Scenario: Lottery Prize Scam")
    print("📞 Scammer initiates contact...\n")
    
    # Scammer sends opening message
    scammer_msg = scammer.get_opening_message()
    print("🚨 SCAMMER:")
    print("-" * 80)
    print(scammer_msg)
    print("-" * 80)
    
    conversation_history = []
    
    # Honeypot processes and responds
    for turn in range(5):
        print(f"\n--- Turn {turn + 1} ---")
        
        # Add scammer message to history
        conversation_history.append({
            "sender_type": "scammer",
            "content": scammer_msg,
            "timestamp": "2024-01-01T00:00:00"
        })
        
        # Agent processes the message
        result = await agent.process_message(
            conversation_id=conversation_id,
            message=scammer_msg,
            conversation_history=conversation_history
        )
        
        honeypot_response = result["response"]
        
        # Display agent thinking
        print("\n🤖 AGENT ANALYSIS:")
        print(f"  Scam Detected: {result['detection']['is_scam']}")
        print(f"  Confidence: {result['detection']['confidence']:.2f}")
        print(f"  Scam Type: {result['detection']['scam_type']}")
        print(f"  Phase: {result['state']['phase']}")
        if result['state']['persona']:
            print(f"  Persona: {result['state']['persona']['name']}")
        
        # Display extracted intelligence
        if result['extracted']:
            print(f"  Extracted: {result['extracted']}")
        
        print("\n🍯 HONEYPOT RESPONSE:")
        print("-" * 80)
        print(honeypot_response)
        print("-" * 80)
        
        # Add honeypot response to history
        conversation_history.append({
            "sender_type": "honeypot",
            "content": honeypot_response,
            "timestamp": "2024-01-01T00:00:00"
        })
        
        # Scammer responds
        scammer_msg = scammer.respond(honeypot_response)
        
        print("\n🚨 SCAMMER:")
        print("-" * 80)
        print(scammer_msg)
        print("-" * 80)
        
        # Stop if scammer provided payment details
        if scammer.provided_details:
            print("\n✅ SUCCESS! Payment details extracted!")
            break
    
    # Final summary
    print("\n" + "="*80)
    print("CONVERSATION SUMMARY")
    print("="*80)
    
    state = agent.states[conversation_id]
    print(f"\nTotal Messages: {state.message_count}")
    print(f"Scam Type: {state.scam_type}")
    print(f"Detection Confidence: {state.confidence:.2f}")
    print(f"Conversation Phase: {state.phase}")
    
    if state.extracted_artifacts:
        print("\n📊 EXTRACTED INTELLIGENCE:")
        for artifact_type, values in state.extracted_artifacts.items():
            print(f"  {artifact_type}: {values}")
    
    # Generate structured output
    output = {
        "conversation_id": conversation_id,
        "scam_detected": state.scam_detected,
        "scam_type": state.scam_type,
        "detection_confidence": state.confidence,
        "engagement_phase": state.phase,
        "persona_used": state.persona,
        "extracted_intelligence": state.extracted_artifacts,
        "conversation_metrics": {
            "total_messages": state.message_count,
            "scammer_time_wasted_seconds": state.message_count * 120
        }
    }
    
    print("\n" + "="*80)
    print("STRUCTURED JSON OUTPUT")
    print("="*80)
    print(json.dumps(output, indent=2, default=str))
    
    print("\n" + "="*80)
    print("DEMO COMPLETED SUCCESSFULLY")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(run_demo_conversation())
