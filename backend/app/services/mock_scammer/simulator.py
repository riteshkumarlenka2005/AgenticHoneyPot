"""Mock scammer simulator."""
from typing import Dict
import random
import enum


class ScamScenario(str, enum.Enum):
    """Scam scenario types."""
    LOTTERY_PRIZE = "lottery_prize"
    BANK_KYC_FRAUD = "bank_kyc_fraud"
    TECH_SUPPORT = "tech_support"
    INVESTMENT_FRAUD = "investment_fraud"
    JOB_SCAM = "job_scam"


class MockScammer:
    """Simulate scammer behavior for testing."""
    
    def __init__(self, scenario: ScamScenario):
        """Initialize mock scammer with scenario."""
        self.scenario = scenario
        self.message_count = 0
        self.provided_details = False
        
        # Scammer personas
        self.personas = {
            ScamScenario.LOTTERY_PRIZE: {
                "name": "Mr. David Wilson",
                "organization": "International Lottery Commission",
                "tone": "professional"
            },
            ScamScenario.BANK_KYC_FRAUD: {
                "name": "Customer Service",
                "organization": "State Bank of India",
                "tone": "urgent"
            },
            ScamScenario.TECH_SUPPORT: {
                "name": "John from Microsoft",
                "organization": "Microsoft Tech Support",
                "tone": "helpful"
            },
            ScamScenario.INVESTMENT_FRAUD: {
                "name": "Rohit Mehta",
                "organization": "Prime Investments Ltd",
                "tone": "friendly"
            },
            ScamScenario.JOB_SCAM: {
                "name": "HR Manager",
                "organization": "Amazon Recruitment",
                "tone": "professional"
            }
        }
    
    def get_opening_message(self) -> str:
        """Get the scammer's opening message."""
        messages = {
            ScamScenario.LOTTERY_PRIZE: (
                "🎉 CONGRATULATIONS! 🎉\n\n"
                "You have WON Rs. 25,00,000 in the International Lottery Draw! "
                "Your ticket number 7834-IND-2024 has been selected. "
                "To claim your prize, please respond immediately. "
                "This is a limited time offer!\n\n"
                "Best Regards,\n"
                "Mr. David Wilson\n"
                "International Lottery Commission"
            ),
            ScamScenario.BANK_KYC_FRAUD: (
                "⚠️ URGENT: Your SBI account will be BLOCKED in 24 hours!\n\n"
                "Dear Customer,\n\n"
                "Your KYC details are pending verification. "
                "Please update immediately to avoid account suspension. "
                "Click here or reply with your details.\n\n"
                "SBI Customer Service"
            ),
            ScamScenario.TECH_SUPPORT: (
                "WARNING: Your computer has been infected with a virus!\n\n"
                "This is John from Microsoft Tech Support. "
                "We detected malicious activity from your IP address. "
                "Your system will crash in 2 hours if not fixed. "
                "Reply NOW for immediate assistance.\n\n"
                "Microsoft Support ID: MS-7843-2024"
            ),
            ScamScenario.INVESTMENT_FRAUD: (
                "💰 EXCLUSIVE Investment Opportunity! 💰\n\n"
                "Hello! I'm Rohit Mehta from Prime Investments. "
                "We're offering a GUARANTEED 300% return in 30 days through crypto trading. "
                "Minimum investment: Rs. 10,000. "
                "Limited slots available! Interested?"
            ),
            ScamScenario.JOB_SCAM: (
                "🎯 Job Opportunity: Work From Home 🎯\n\n"
                "Congratulations! You've been selected for a Data Entry position at Amazon. "
                "Salary: Rs. 25,000/month for just 2-3 hours daily work. "
                "Registration fee: Rs. 2,000 (refundable). "
                "Reply to confirm your interest!"
            )
        }
        
        self.message_count += 1
        return messages[self.scenario]
    
    def respond(self, victim_message: str) -> str:
        """Generate scammer response to victim's message."""
        self.message_count += 1
        victim_lower = victim_message.lower()
        
        # Check if victim is asking for payment details
        asking_for_details = any(word in victim_lower for word in [
            "account", "upi", "payment", "transfer", "send", "money", "details", "number"
        ])
        
        if asking_for_details and not self.provided_details:
            self.provided_details = True
            return self._provide_payment_details()
        
        # Check if victim is showing interest
        showing_interest = any(word in victim_lower for word in [
            "interested", "yes", "okay", "sure", "proceed", "tell me", "how"
        ])
        
        if showing_interest and self.message_count <= 3:
            return self._build_trust()
        
        # Check if victim is stalling
        stalling = any(word in victim_lower for word in [
            "wait", "later", "busy", "tomorrow", "think", "son", "daughter"
        ])
        
        if stalling:
            return self._pressure_response()
        
        # Default response
        return self._default_response()
    
    def _provide_payment_details(self) -> str:
        """Provide fake payment details."""
        details = {
            ScamScenario.LOTTERY_PRIZE: (
                "Great! To process your prize, you need to pay the processing fee of Rs. 5,000.\n\n"
                "Payment Details:\n"
                "UPI ID: lottery.claim@paytm\n"
                "Account: 9876543210\n"
                "IFSC: SBIN0001234\n"
                "Name: Lottery Processing\n\n"
                "Send payment screenshot immediately!"
            ),
            ScamScenario.BANK_KYC_FRAUD: (
                "To verify your KYC, deposit Rs. 100 to this account:\n\n"
                "Account: 1234567890\n"
                "IFSC: HDFC0001234\n"
                "UPI: sbi.kyc@oksbi\n\n"
                "Then share your account number for verification."
            ),
            ScamScenario.TECH_SUPPORT: (
                "To fix your computer, purchase a security license for $99.\n\n"
                "Send payment to:\n"
                "UPI: techsupport@paytm\n"
                "Or call: +91-9876543210\n\n"
                "We'll remote access your PC immediately after payment."
            ),
            ScamScenario.INVESTMENT_FRAUD: (
                "Excellent decision! Transfer your investment amount to:\n\n"
                "UPI ID: prime.invest@ybl\n"
                "Account: 8765432109\n"
                "IFSC: ICIC0001234\n"
                "Name: Prime Investments\n\n"
                "WhatsApp: +91-9123456789\n"
                "Your returns will start within 24 hours!"
            ),
            ScamScenario.JOB_SCAM: (
                "Perfect! Send the registration fee to:\n\n"
                "UPI: amazon.jobs@paytm\n"
                "Account: 5432109876\n"
                "IFSC: AXIS0001234\n\n"
                "After payment, we'll send your login credentials and training materials!"
            )
        }
        
        return details[self.scenario]
    
    def _build_trust(self) -> str:
        """Build trust with victim."""
        responses = {
            ScamScenario.LOTTERY_PRIZE: (
                "Wonderful! You are one of the lucky winners. "
                "This lottery is 100% genuine and government approved. "
                "Thousands have already claimed their prizes. "
                "You just need to pay a small processing fee to receive your Rs. 25 lakhs!"
            ),
            ScamScenario.BANK_KYC_FRAUD: (
                "Thank you for your prompt response. "
                "This is mandatory as per RBI guidelines. "
                "All SBI customers must complete KYC update by today. "
                "Don't worry, the process is simple and quick."
            ),
            ScamScenario.TECH_SUPPORT: (
                "Good that you responded quickly. Your computer is at serious risk. "
                "I'm a certified Microsoft technician. "
                "We've helped thousands of customers. "
                "Just follow my instructions carefully."
            ),
            ScamScenario.INVESTMENT_FRAUD: (
                "Smart choice! Our company has 5-star ratings. "
                "We use AI-powered trading bots for guaranteed profits. "
                "You can withdraw anytime. "
                "Our previous clients made Rs. 2 lakhs from just Rs. 10,000 investment!"
            ),
            ScamScenario.JOB_SCAM: (
                "Congratulations on being selected! "
                "This is a legitimate Amazon work-from-home position. "
                "The registration fee is standard and will be refunded with your first salary. "
                "You'll be joining a team of 500+ successful employees."
            )
        }
        
        return responses[self.scenario]
    
    def _pressure_response(self) -> str:
        """Apply pressure when victim stalls."""
        return (
            "⏰ TIME IS RUNNING OUT! ⏰\n\n"
            "Please respond immediately or you will lose this opportunity. "
            "We have other candidates waiting. "
            "This offer expires in 2 hours. "
            "Don't miss out!"
        )
    
    def _default_response(self) -> str:
        """Default response."""
        return (
            "I understand. Let me clarify any doubts you have. "
            "This is completely genuine and safe. "
            "You can trust us. How would you like to proceed?"
        )
