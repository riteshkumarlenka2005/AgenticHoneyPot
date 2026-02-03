#!/usr/bin/env python3
"""
Interactive demo script to test the honeypot system end-to-end.
This script simulates a full conversation flow without requiring database setup.
"""
import asyncio
import json
from pathlib import Path
import sys

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.detection.detector import ScamDetector
from app.services.persona.generator import PersonaGenerator
from app.services.extraction.extractor import IntelligenceExtractor
from app.services.response.generator import ResponseGenerator
from app.core.agent.loop import HoneypotAgent
from app.services.mock_scammer.simulator import MockScammer, ScamScenario


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


async def interactive_demo():
    """Run an interactive honeypot demo."""
    print(f"\n{Colors.HEADER}{'='*80}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}🍯 AGENTIC HONEYPOT - INTERACTIVE DEMO{Colors.END}")
    print(f"{Colors.HEADER}{'='*80}{Colors.END}\n")
    
    # Choose scenario
    print(f"{Colors.CYAN}Available Scam Scenarios:{Colors.END}")
    scenarios = list(ScamScenario)
    for i, scenario in enumerate(scenarios, 1):
        print(f"  {i}. {scenario.value.replace('_', ' ').title()}")
    
    while True:
        try:
            choice = input(f"\n{Colors.YELLOW}Select scenario (1-{len(scenarios)}): {Colors.END}")
            scenario_idx = int(choice) - 1
            if 0 <= scenario_idx < len(scenarios):
                selected_scenario = scenarios[scenario_idx]
                break
            else:
                print(f"{Colors.RED}Invalid choice. Please try again.{Colors.END}")
        except (ValueError, KeyboardInterrupt):
            print(f"\n{Colors.RED}Exiting...{Colors.END}")
            return
    
    print(f"\n{Colors.GREEN}✓ Selected: {selected_scenario.value.replace('_', ' ').title()}{Colors.END}\n")
    
    # Initialize components
    detector = ScamDetector()
    persona_gen = PersonaGenerator()
    extractor = IntelligenceExtractor()
    response_gen = ResponseGenerator()
    agent = HoneypotAgent(detector, persona_gen, extractor, response_gen)
    
    # Create mock scammer
    scammer = MockScammer(selected_scenario)
    conversation_id = f"interactive-{selected_scenario.value}"
    
    print(f"{Colors.HEADER}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}Starting Conversation...{Colors.END}")
    print(f"{Colors.HEADER}{'='*80}{Colors.END}\n")
    
    # Get opening message
    scammer_msg = scammer.get_opening_message()
    print(f"{Colors.RED}🚨 SCAMMER:{Colors.END}")
    print(f"{Colors.RED}{'-'*80}{Colors.END}")
    print(scammer_msg)
    print(f"{Colors.RED}{'-'*80}{Colors.END}\n")
    
    conversation_history = []
    turn = 0
    max_turns = 10
    
    while turn < max_turns:
        turn += 1
        
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
        
        # Display agent analysis
        print(f"{Colors.CYAN}🤖 AGENT ANALYSIS (Turn {turn}):{Colors.END}")
        print(f"  Scam Detected: {Colors.GREEN if result['detection']['is_scam'] else Colors.YELLOW}{result['detection']['is_scam']}{Colors.END}")
        print(f"  Confidence: {result['detection']['confidence']:.2%}")
        print(f"  Scam Type: {result['detection']['scam_type'] or 'Unknown'}")
        print(f"  Phase: {result['state']['phase']}")
        
        if result['state']['persona']:
            print(f"  Persona: {result['state']['persona']['name']}")
        
        if result['extracted']:
            print(f"  {Colors.YELLOW}⚡ Extracted: {result['extracted']}{Colors.END}")
        
        # Display honeypot response
        print(f"\n{Colors.BLUE}🍯 HONEYPOT:{Colors.END}")
        print(f"{Colors.BLUE}{'-'*80}{Colors.END}")
        print(honeypot_response)
        print(f"{Colors.BLUE}{'-'*80}{Colors.END}\n")
        
        # Add honeypot response to history
        conversation_history.append({
            "sender_type": "honeypot",
            "content": honeypot_response,
            "timestamp": "2024-01-01T00:00:00"
        })
        
        # Check if payment details were extracted
        if scammer.provided_details:
            print(f"{Colors.GREEN}{'='*80}{Colors.END}")
            print(f"{Colors.GREEN}{Colors.BOLD}✅ SUCCESS! Payment details extracted!{Colors.END}")
            print(f"{Colors.GREEN}{'='*80}{Colors.END}\n")
            break
        
        # Scammer responds
        scammer_msg = scammer.respond(honeypot_response)
        print(f"{Colors.RED}🚨 SCAMMER:{Colors.END}")
        print(f"{Colors.RED}{'-'*80}{Colors.END}")
        print(scammer_msg)
        print(f"{Colors.RED}{'-'*80}{Colors.END}\n")
        
        # Small delay for readability
        await asyncio.sleep(0.5)
    
    # Display summary
    state = agent.states[conversation_id]
    
    print(f"\n{Colors.HEADER}{'='*80}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}📊 CONVERSATION SUMMARY{Colors.END}")
    print(f"{Colors.HEADER}{'='*80}{Colors.END}\n")
    
    print(f"Total Messages: {state.message_count}")
    print(f"Scam Type: {state.scam_type or 'Unknown'}")
    print(f"Detection Confidence: {state.confidence:.2%}")
    print(f"Final Phase: {state.phase}")
    
    if state.extracted_artifacts:
        print(f"\n{Colors.GREEN}🎯 EXTRACTED INTELLIGENCE:{Colors.END}")
        for artifact_type, values in state.extracted_artifacts.items():
            print(f"  {artifact_type}: {values}")
    else:
        print(f"\n{Colors.YELLOW}⚠️  No intelligence artifacts extracted yet{Colors.END}")
    
    # Create structured output
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
    
    print(f"\n{Colors.CYAN}📄 STRUCTURED JSON OUTPUT:{Colors.END}")
    print(json.dumps(output, indent=2, default=str))
    
    print(f"\n{Colors.HEADER}{'='*80}{Colors.END}")
    print(f"{Colors.GREEN}{Colors.BOLD}✅ DEMO COMPLETED SUCCESSFULLY{Colors.END}")
    print(f"{Colors.HEADER}{'='*80}{Colors.END}\n")


def main():
    """Main entry point."""
    try:
        asyncio.run(interactive_demo())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Demo interrupted by user.{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.END}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
