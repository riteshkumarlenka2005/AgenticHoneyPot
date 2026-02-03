"""Rule-based scam detection patterns."""
import re
from enum import Enum


class ScamType(str, Enum):
    """Scam type enumeration."""
    LOTTERY_PRIZE = "lottery_prize"
    BANK_KYC_FRAUD = "bank_kyc_fraud"
    TECH_SUPPORT = "tech_support"
    INVESTMENT_FRAUD = "investment_fraud"
    JOB_SCAM = "job_scam"
    PACKAGE_DELIVERY = "package_delivery"
    TAX_REFUND = "tax_refund"
    ROMANCE_SCAM = "romance_scam"
    UNKNOWN = "unknown"


# Scam detection patterns
SCAM_PATTERNS = {
    ScamType.LOTTERY_PRIZE: [
        r"(?i)congratulations?.{0,50}(won|winner|prize|lottery)",
        r"(?i)(lottery|prize).{0,50}(won|selected|winner)",
        r"(?i)(claim|collect).{0,50}(prize|reward|money)",
        r"(?i)lucky (winner|draw)",
    ],
    ScamType.BANK_KYC_FRAUD: [
        r"(?i)(bank|account).{0,50}(suspended|blocked|locked|deactivated)",
        r"(?i)kyc.{0,50}(update|verification|pending|required)",
        r"(?i)(verify|update).{0,50}(account|kyc|details)",
        r"(?i)(immediate|urgent).{0,50}(action|verification)",
    ],
    ScamType.TECH_SUPPORT: [
        r"(?i)(microsoft|apple|google|amazon).{0,50}(support|technical|security)",
        r"(?i)(virus|malware|security).{0,50}(detected|found|alert)",
        r"(?i)(computer|device|system).{0,50}(infected|compromised|hacked)",
        r"(?i)call.{0,50}(toll.free|helpline|support)",
    ],
    ScamType.INVESTMENT_FRAUD: [
        r"(?i)(invest|investment).{0,50}(opportunity|guaranteed|returns)",
        r"(?i)(double|triple).{0,50}(money|investment)",
        r"(?i)(guaranteed|risk.free).{0,50}(returns|profit)",
        r"(?i)(crypto|bitcoin|forex).{0,50}(trading|investment)",
    ],
    ScamType.JOB_SCAM: [
        r"(?i)(job|work).{0,50}(home|part.time|opportunity)",
        r"(?i)earn.{0,50}(per day|per week|lakhs|thousands)",
        r"(?i)(registration|joining).{0,50}(fee|payment)",
        r"(?i)data entry.{0,50}(work|job)",
    ],
    ScamType.PACKAGE_DELIVERY: [
        r"(?i)(package|parcel|shipment).{0,50}(pending|waiting|delivery)",
        r"(?i)(courier|delivery).{0,50}(attempted|failed|pending)",
        r"(?i)(customs|clearance).{0,50}(fee|payment|charges)",
    ],
    ScamType.TAX_REFUND: [
        r"(?i)(tax|income tax).{0,50}(refund|return)",
        r"(?i)refund.{0,50}(pending|approved|available)",
        r"(?i)(claim|receive).{0,50}(refund|tax)",
    ],
}

# Urgency keywords that scammers often use
URGENCY_KEYWORDS = [
    "urgent", "immediate", "now", "today", "24 hours", "expire", "expiring",
    "last chance", "limited time", "act now", "hurry", "quick", "asap"
]

# Authority keywords
AUTHORITY_KEYWORDS = [
    "official", "government", "bank", "police", "court", "legal",
    "tax department", "revenue", "enforcement", "authority"
]

# Fear keywords
FEAR_KEYWORDS = [
    "suspended", "blocked", "deactivated", "arrested", "legal action",
    "penalty", "fine", "fraud", "hacked", "compromised", "infected"
]

# Request for sensitive information
SENSITIVE_INFO_PATTERNS = [
    r"(?i)(send|share|provide).{0,50}(otp|password|pin|cvv)",
    r"(?i)(account|card).{0,50}(number|details|information)",
    r"(?i)(bank|credit card).{0,50}(details|information)",
    r"(?i)(upi|paytm|phonepe|gpay).{0,50}(id|number)",
]


def detect_scam_type(message: str) -> tuple[ScamType, float]:
    """
    Detect scam type based on patterns.
    
    Args:
        message: The message to analyze
        
    Returns:
        Tuple of (scam_type, confidence)
    """
    message = message.lower()
    best_match = ScamType.UNKNOWN
    best_confidence = 0.0
    
    for scam_type, patterns in SCAM_PATTERNS.items():
        matches = sum(1 for pattern in patterns if re.search(pattern, message))
        if matches > 0:
            confidence = min(matches / len(patterns), 1.0)
            if confidence > best_confidence:
                best_confidence = confidence
                best_match = scam_type
    
    return best_match, best_confidence


def detect_manipulation_tactics(message: str) -> list[str]:
    """
    Detect manipulation tactics used in the message.
    
    Args:
        message: The message to analyze
        
    Returns:
        List of detected tactics
    """
    message = message.lower()
    tactics = []
    
    # Check for urgency
    if any(keyword in message for keyword in URGENCY_KEYWORDS):
        tactics.append("urgency")
    
    # Check for authority
    if any(keyword in message for keyword in AUTHORITY_KEYWORDS):
        tactics.append("authority")
    
    # Check for fear
    if any(keyword in message for keyword in FEAR_KEYWORDS):
        tactics.append("fear")
    
    # Check for requests for sensitive information
    if any(re.search(pattern, message) for pattern in SENSITIVE_INFO_PATTERNS):
        tactics.append("information_request")
    
    return tactics


def calculate_scam_score(message: str) -> float:
    """
    Calculate overall scam score for a message.
    
    Args:
        message: The message to analyze
        
    Returns:
        Scam score between 0.0 and 1.0
    """
    scam_type, type_confidence = detect_scam_type(message)
    tactics = detect_manipulation_tactics(message)
    
    # Base score from type detection
    score = type_confidence * 0.6
    
    # Add points for manipulation tactics
    score += len(tactics) * 0.1
    
    # Cap at 1.0
    return min(score, 1.0)
