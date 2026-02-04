"""Policy store for RAG-based policy checking."""
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PolicyDocument:
    """Policy document for RAG retrieval."""
    id: str
    title: str
    content: str
    category: str
    tags: List[str]
    created_at: datetime
    embedding: Optional[List[float]] = None


class PolicyStore:
    """Store and retrieve policy documents for RAG."""
    
    def __init__(self):
        """Initialize policy store with default policies."""
        self.policies: Dict[str, PolicyDocument] = {}
        self._initialize_default_policies()
    
    def _initialize_default_policies(self):
        """Load default bank and scam detection policies."""
        # Bank policies
        self.add_policy(PolicyDocument(
            id="bank_001",
            title="Never Share OTP",
            content="""
            Banks will NEVER ask customers to share their OTP (One-Time Password).
            OTPs are confidential and should only be used by the account holder for
            transactions they initiate themselves. Sharing OTP can lead to unauthorized
            access to your account.
            """,
            category="bank_security",
            tags=["otp", "security", "authentication"],
            created_at=datetime.utcnow()
        ))
        
        self.add_policy(PolicyDocument(
            id="bank_002",
            title="Official Communication Channels",
            content="""
            Banks communicate with customers through official channels only:
            - Official email addresses (@bankname.com)
            - Verified mobile numbers
            - In-app notifications
            - Physical mail from official address
            
            Banks will NEVER use WhatsApp, Telegram, or personal phone numbers
            for official business.
            """,
            category="bank_communication",
            tags=["communication", "verification", "channels"],
            created_at=datetime.utcnow()
        ))
        
        self.add_policy(PolicyDocument(
            id="bank_003",
            title="No Unsolicited Money Requests",
            content="""
            Banks will NEVER ask for money transfers or payments via:
            - UPI to personal accounts
            - Third-party payment gateways
            - Cryptocurrency
            - Gift cards or vouchers
            
            All legitimate bank fees are deducted directly from your account.
            """,
            category="bank_payments",
            tags=["payments", "fees", "fraud"],
            created_at=datetime.utcnow()
        ))
        
        # Scam patterns
        self.add_policy(PolicyDocument(
            id="scam_001",
            title="Lottery/Prize Scam Indicators",
            content="""
            Common indicators of lottery/prize scams:
            - Winning a lottery you never entered
            - Requests for fees or taxes upfront
            - Urgency to claim prize within hours
            - Payment via gift cards or cryptocurrency
            - Poor grammar and spelling
            - Requests for personal/banking information
            """,
            category="scam_patterns",
            tags=["lottery", "prize", "winnings", "fraud"],
            created_at=datetime.utcnow()
        ))
        
        self.add_policy(PolicyDocument(
            id="scam_002",
            title="KYC Update Scam Indicators",
            content="""
            Red flags for fake KYC update scams:
            - Threats of account suspension
            - Requests to click suspicious links
            - Asking for full debit/credit card details
            - Requesting CVV or PIN
            - Urgency (account will be blocked today)
            - Poorly designed forms or websites
            """,
            category="scam_patterns",
            tags=["kyc", "bank", "phishing", "fraud"],
            created_at=datetime.utcnow()
        ))
        
        self.add_policy(PolicyDocument(
            id="scam_003",
            title="Investment Scam Indicators",
            content="""
            Warning signs of investment scams:
            - Guaranteed high returns with no risk
            - Pressure to invest immediately
            - Unregistered investment opportunities
            - Pyramid or MLM structure
            - Requests for cryptocurrency investment
            - Celebrity endorsements (often fake)
            - No clear business model
            """,
            category="scam_patterns",
            tags=["investment", "fraud", "ponzi", "mlm"],
            created_at=datetime.utcnow()
        ))
        
        self.add_policy(PolicyDocument(
            id="scam_004",
            title="Job Scam Indicators",
            content="""
            Red flags for job scams:
            - Requests for payment for training or materials
            - Too-good-to-be-true salary offers
            - No interview process
            - Poor job description
            - Requests for personal documents before hiring
            - Work-from-home with minimal qualifications
            - Payment processing or money transfer jobs
            """,
            category="scam_patterns",
            tags=["job", "employment", "fraud", "work-from-home"],
            created_at=datetime.utcnow()
        ))
    
    def add_policy(self, policy: PolicyDocument):
        """Add a policy document to the store."""
        self.policies[policy.id] = policy
    
    def get_policy(self, policy_id: str) -> Optional[PolicyDocument]:
        """Get a specific policy by ID."""
        return self.policies.get(policy_id)
    
    def search_by_category(self, category: str) -> List[PolicyDocument]:
        """Search policies by category."""
        return [
            policy for policy in self.policies.values()
            if policy.category == category
        ]
    
    def search_by_tags(self, tags: List[str]) -> List[PolicyDocument]:
        """Search policies by tags."""
        results = []
        for policy in self.policies.values():
            if any(tag in policy.tags for tag in tags):
                results.append(policy)
        return results
    
    def search_by_keywords(self, keywords: List[str]) -> List[PolicyDocument]:
        """Search policies by keywords in content."""
        results = []
        keywords_lower = [kw.lower() for kw in keywords]
        
        for policy in self.policies.values():
            content_lower = policy.content.lower()
            title_lower = policy.title.lower()
            
            if any(kw in content_lower or kw in title_lower for kw in keywords_lower):
                results.append(policy)
        
        return results
    
    def get_relevant_policies(
        self,
        scam_type: str,
        keywords: Optional[List[str]] = None
    ) -> List[PolicyDocument]:
        """Get policies relevant to a scam type."""
        # Map scam types to tags
        scam_type_tags = {
            "lottery_prize": ["lottery", "prize", "winnings"],
            "bank_kyc_fraud": ["kyc", "bank", "phishing"],
            "investment_fraud": ["investment", "ponzi", "mlm"],
            "tech_support": ["tech", "support", "virus"],
            "job_scam": ["job", "employment", "work-from-home"]
        }
        
        tags = scam_type_tags.get(scam_type, [])
        if keywords:
            tags.extend(keywords)
        
        # Get policies by tags
        policies = self.search_by_tags(tags)
        
        # Also get by scam_patterns category
        pattern_policies = self.search_by_category("scam_patterns")
        
        # Combine and deduplicate
        all_policies = {policy.id: policy for policy in policies + pattern_policies}
        
        return list(all_policies.values())


# Global policy store instance
policy_store = PolicyStore()
