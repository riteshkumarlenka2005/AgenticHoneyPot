"""Mock scammer scenarios."""
from enum import Enum


class ScamScenario(str, Enum):
    """Scam scenario enumeration."""
    LOTTERY_PRIZE = "lottery_prize"
    BANK_KYC_FRAUD = "bank_kyc_fraud"
    TECH_SUPPORT = "tech_support"
    INVESTMENT_FRAUD = "investment_fraud"
    JOB_SCAM = "job_scam"


# Initial scam messages for different scenarios
SCENARIO_OPENERS = {
    ScamScenario.LOTTERY_PRIZE: [
        "Congratulations! You have won Rs 25,00,000 in the Kaun Banega Crorepati Lucky Draw. To claim your prize, please reply immediately.",
        "Dear Winner, Your mobile number has won £1,000,000 in the UK National Lottery. Claim code: KBC2024. Contact us to process your winning.",
        "URGENT: You are selected as lucky winner of Rs 15 Lakh from WhatsApp lucky draw. Limited time offer. Reply YES to claim.",
    ],
    ScamScenario.BANK_KYC_FRAUD: [
        "ALERT: Your bank account will be suspended in 24 hours due to pending KYC verification. Update immediately: http://fake-sbi-kyc.com",
        "Dear Customer, Your SBI account is temporarily locked. Complete KYC verification within 12 hours to restore services. Click here.",
        "HDFC Bank Notice: Your account requires immediate KYC update as per RBI guidelines. Failure to comply will result in account deactivation.",
    ],
    ScamScenario.TECH_SUPPORT: [
        "CRITICAL: Microsoft Security has detected 5 viruses on your computer. Your system will be locked in 30 minutes. Call toll-free: 1800-XXX-XXXX",
        "Apple Security Alert: Your iPhone has been compromised. Immediate action required. Contact Apple Support: +91-XXXXXXXXXX",
        "Your computer is sending spam emails. Google detected suspicious activity. Call technical support immediately: 1800-XXX-XXXX",
    ],
    ScamScenario.INVESTMENT_FRAUD: [
        "Special Investment Opportunity: Double your money in 30 days with our guaranteed crypto trading program. Minimum investment: ₹10,000",
        "Exclusive Forex Trading Alert: Join our private group and earn ₹50,000-₹2,00,000 per month. Limited seats. Register now!",
        "Stock Market Tip: We have insider information on stocks that will 10x in 3 months. Investment required: ₹25,000. Guaranteed returns.",
    ],
    ScamScenario.JOB_SCAM: [
        "Urgent Hiring: Data entry work from home. Earn ₹25,000-₹40,000 per month. No experience needed. Registration fee: ₹2,500",
        "Amazon is hiring! Part-time product review job. Earn ₹1,500 per day. Pay one-time joining fee of ₹3,000 to start.",
        "Work from home opportunity: Copy-paste work, earn ₹800 per page. Registration charges ₹5,000. Limited positions available.",
    ]
}

# Fake scammer details to provide when victim asks
FAKE_SCAMMER_DETAILS = {
    "upi_ids": [
        "winner2024@paytm",
        "prizeoffice@upi",
        "claimprize@ybl",
        "kycupdate@oksbi",
        "microsoft.support@paytm",
        "investment.pro@upi"
    ],
    "bank_accounts": [
        {
            "account_number": "1234567890123",
            "ifsc_code": "SBIN0001234",
            "account_holder": "Prize Distribution Office"
        },
        {
            "account_number": "9876543210987",
            "ifsc_code": "HDFC0004567",
            "account_holder": "KYC Verification Center"
        },
        {
            "account_number": "5555666677778888",
            "ifsc_code": "ICIC0001111",
            "account_holder": "Investment Group"
        }
    ],
    "phone_numbers": [
        "+91-9876543210",
        "+91-8765432109",
        "+91-7654321098"
    ],
    "phishing_links": [
        "http://claim-prize-now.com/winner",
        "http://sbi-kyc-update.net/verify",
        "http://microsoft-security.support/fix",
        "http://investment-profits.biz/register"
    ]
}
