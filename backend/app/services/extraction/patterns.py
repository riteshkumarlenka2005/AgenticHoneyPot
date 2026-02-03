"""Pattern matching for intelligence extraction."""
import re


# Regular expressions for extracting intelligence
UPI_PATTERN = r'\b[a-zA-Z0-9._-]+@[a-zA-Z]{3,}\b'
PHONE_PATTERN = r'(?:\+91|0)?[6-9]\d{9}'
ACCOUNT_NUMBER_PATTERN = r'\b\d{9,18}\b'
IFSC_PATTERN = r'\b[A-Z]{4}0[A-Z0-9]{6}\b'
URL_PATTERN = r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)'
EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'


def extract_upi_ids(text: str) -> list[str]:
    """Extract UPI IDs from text."""
    matches = re.findall(UPI_PATTERN, text)
    # Filter out common false positives
    return [m for m in matches if not m.endswith(('.com', '.in', '.org'))]


def extract_phone_numbers(text: str) -> list[str]:
    """Extract phone numbers from text."""
    matches = re.findall(PHONE_PATTERN, text)
    # Normalize phone numbers
    normalized = []
    for match in matches:
        # Remove +91 or 0 prefix for storage
        clean = re.sub(r'^(\+91|0)', '', match)
        if len(clean) == 10:
            normalized.append(f"+91-{clean}")
    return list(set(normalized))


def extract_bank_accounts(text: str) -> list[str]:
    """Extract bank account numbers from text."""
    matches = re.findall(ACCOUNT_NUMBER_PATTERN, text)
    # Filter out obvious false positives (like dates, phone numbers)
    return [m for m in matches if 9 <= len(m) <= 18]


def extract_ifsc_codes(text: str) -> list[str]:
    """Extract IFSC codes from text."""
    return re.findall(IFSC_PATTERN, text.upper())


def extract_urls(text: str) -> list[str]:
    """Extract URLs from text."""
    return re.findall(URL_PATTERN, text)


def extract_emails(text: str) -> list[str]:
    """Extract email addresses from text."""
    return re.findall(EMAIL_PATTERN, text)


def extract_all_intelligence(text: str) -> dict:
    """
    Extract all types of intelligence from text.
    
    Args:
        text: Text to extract from
        
    Returns:
        Dictionary with all extracted intelligence types
    """
    return {
        "upi_ids": extract_upi_ids(text),
        "phone_numbers": extract_phone_numbers(text),
        "bank_accounts": extract_bank_accounts(text),
        "ifsc_codes": extract_ifsc_codes(text),
        "urls": extract_urls(text),
        "emails": extract_emails(text)
    }


# Questions to ask to extract specific intelligence
EXTRACTION_QUESTIONS = {
    "upi_id": [
        "What UPI ID should I use to send the payment?",
        "Can you share your UPI ID?",
        "Which UPI ID should I send the money to?",
        "What's your UPI address?",
    ],
    "bank_account": [
        "What are your bank account details?",
        "Which account should I transfer to?",
        "Can you share your account number and IFSC code?",
        "I need your bank details for the transfer.",
    ],
    "phone": [
        "What's your contact number?",
        "Can I have your phone number?",
        "How can I reach you on phone?",
        "What number should I call?",
    ],
    "link": [
        "Can you send me the link?",
        "Where should I go to complete this?",
        "What's the website link?",
        "Can you share the portal link?",
    ]
}
