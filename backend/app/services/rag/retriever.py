"""Document retriever for RAG-based policy checking."""
from typing import List, Optional, Dict
from app.services.rag.policy_store import policy_store, PolicyDocument


class PolicyRetriever:
    """Retrieve relevant policy documents for context-aware scam detection."""
    
    def __init__(self):
        """Initialize retriever with policy store."""
        self.policy_store = policy_store
    
    def retrieve_for_scam_detection(
        self,
        message: str,
        scam_type: Optional[str] = None
    ) -> List[PolicyDocument]:
        """
        Retrieve relevant policies for scam detection.
        
        Args:
            message: The message to analyze
            scam_type: Optional scam type hint
        
        Returns:
            List of relevant policy documents
        """
        # Extract keywords from message
        keywords = self._extract_keywords(message)
        
        # Get policies by scam type if provided
        if scam_type:
            policies = self.policy_store.get_relevant_policies(scam_type, keywords)
        else:
            # Search by keywords
            policies = self.policy_store.search_by_keywords(keywords)
        
        # Sort by relevance (simple keyword matching for now)
        scored_policies = []
        for policy in policies:
            score = self._calculate_relevance_score(policy, keywords)
            scored_policies.append((score, policy))
        
        scored_policies.sort(key=lambda x: x[0], reverse=True)
        
        # Return top 3 most relevant
        return [policy for score, policy in scored_policies[:3]]
    
    def retrieve_for_response_generation(
        self,
        scam_type: str,
        persona_type: str
    ) -> List[PolicyDocument]:
        """
        Retrieve policies to guide response generation.
        
        Args:
            scam_type: Type of scam detected
            persona_type: Type of persona being used
        
        Returns:
            List of relevant policy documents
        """
        # Get scam-specific policies
        policies = self.policy_store.get_relevant_policies(scam_type)
        
        # Add bank security policies if relevant
        if scam_type in ["bank_kyc_fraud", "lottery_prize"]:
            bank_policies = self.policy_store.search_by_category("bank_security")
            policies.extend(bank_policies)
        
        return policies[:5]  # Return top 5
    
    def get_policy_context(
        self,
        policies: List[PolicyDocument]
    ) -> str:
        """
        Format policies as context for LLM.
        
        Args:
            policies: List of policy documents
        
        Returns:
            Formatted context string
        """
        if not policies:
            return ""
        
        context_parts = ["## Relevant Policies and Guidelines\n"]
        
        for idx, policy in enumerate(policies, 1):
            context_parts.append(f"### {idx}. {policy.title}\n")
            context_parts.append(f"{policy.content.strip()}\n")
        
        return "\n".join(context_parts)
    
    def _extract_keywords(self, message: str) -> List[str]:
        """Extract relevant keywords from message."""
        # Common scam-related keywords
        scam_keywords = [
            "otp", "password", "pin", "cvv", "account", "bank", "upi",
            "lottery", "prize", "won", "winner", "congratulations",
            "kyc", "update", "verify", "confirm", "suspend", "block",
            "investment", "returns", "profit", "guaranteed",
            "job", "work from home", "earn", "salary",
            "urgent", "immediately", "today", "expired",
            "link", "click", "download", "install",
            "payment", "transfer", "send", "fee", "tax"
        ]
        
        message_lower = message.lower()
        found_keywords = []
        
        for keyword in scam_keywords:
            if keyword in message_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _calculate_relevance_score(
        self,
        policy: PolicyDocument,
        keywords: List[str]
    ) -> float:
        """Calculate relevance score for a policy."""
        score = 0.0
        policy_text = (policy.title + " " + policy.content).lower()
        
        # Score based on keyword matches
        for keyword in keywords:
            if keyword in policy_text:
                score += 1.0
        
        # Boost score for tag matches
        for keyword in keywords:
            if keyword in policy.tags:
                score += 2.0
        
        return score


# Global retriever instance
retriever = PolicyRetriever()
