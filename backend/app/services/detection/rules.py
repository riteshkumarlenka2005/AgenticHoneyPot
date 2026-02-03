"""Scam detection patterns and rules."""
import re
from typing import Dict, List


# Scam detection keywords and patterns
SCAM_KEYWORDS = {
    "lottery": ["lottery", "won", "prize", "winner", "jackpot", "cash prize"],
    "bank_fraud": ["kyc", "bank account", "verify", "suspended", "blocked", "update details"],
    "tech_support": ["microsoft", "apple", "google", "virus", "infected", "tech support", "refund"],
    "investment": ["investment", "returns", "profit", "crypto", "bitcoin", "trading", "roi"],
    "job_scam": ["work from home", "earn money", "part time job", "easy money", "recruitment"],
    "urgency": ["urgent", "immediately", "now", "today", "limited time", "expires"],
    "authority": ["officer", "manager", "official", "government", "police", "tax"],
    "payment": ["send money", "transfer", "payment", "deposit", "wire", "upi", "account number"],
}

# Regex patterns for extracting intelligence
PATTERNS = {
    "upi_id": r'\b[\w\.-]+@[\w\.-]+\b',
    "phone": r'\+?91[-\s]?\d{10}|\d{10}',
    "ifsc_code": r'\b[A-Z]{4}0[A-Z0-9]{6}\b',
    "bank_account": r'\b\d{9,18}\b',
    "url": r'https?://[^\s]+',
    "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
}


def check_scam_keywords(text: str) -> Dict[str, float]:
    """Check text for scam keywords and return confidence scores."""
    text_lower = text.lower()
    scores = {}
    
    for category, keywords in SCAM_KEYWORDS.items():
        matches = sum(1 for keyword in keywords if keyword in text_lower)
        if matches > 0:
            scores[category] = min(matches * 0.2, 1.0)
    
    return scores


def extract_patterns(text: str) -> Dict[str, List[str]]:
    """Extract intelligence patterns from text."""
    extracted = {}
    
    for pattern_type, pattern in PATTERNS.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            extracted[pattern_type] = list(set(matches))
    
    return extracted


def calculate_scam_confidence(keyword_scores: Dict[str, float]) -> float:
    """Calculate overall scam confidence from keyword scores."""
    if not keyword_scores:
        return 0.0
    
    # Weight different categories
    weights = {
        "lottery": 0.9,
        "bank_fraud": 0.95,
        "tech_support": 0.85,
        "investment": 0.8,
        "job_scam": 0.75,
        "urgency": 0.5,
        "authority": 0.5,
        "payment": 0.7,
    }
    
    weighted_sum = sum(score * weights.get(category, 0.5) for category, score in keyword_scores.items())
    category_count = len(keyword_scores)
    
    return min(weighted_sum / max(category_count, 1), 1.0)
