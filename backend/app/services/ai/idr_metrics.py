"""IDR/IDS/HAR Metrics Calculator."""
from typing import Dict, List, Any
from datetime import datetime, timedelta


class IDRMetricsCalculator:
    """
    Calculate Information Disclosure Rate (IDR), Information Disclosure Score (IDS),
    and Harm Assessment Rate (HAR) metrics for scam conversations.
    """

    def __init__(self):
        """Initialize metrics calculator."""
        # Weights for different artifact types (higher = more valuable)
        self.artifact_weights = {
            "upi_id": 1.0,
            "bank_account": 1.2,
            "ifsc_code": 0.8,
            "phone": 0.6,
            "url": 0.5,
            "email": 0.5,
        }
        
        # Harm potential based on scam type
        self.scam_harm_scores = {
            "tech_support": 0.7,
            "phishing": 0.8,
            "romance": 0.9,
            "investment": 0.95,
            "lottery": 0.6,
            "job_scam": 0.65,
            "loan_scam": 0.85,
            "unknown": 0.5,
        }

    def calculate_idr(
        self,
        intelligence_count: int,
        message_count: int,
        duration_seconds: int
    ) -> float:
        """
        Calculate Information Disclosure Rate (IDR).
        
        IDR = (Intelligence Artifacts / Messages) * (3600 / Duration)
        Normalized to artifacts per hour per message.
        
        Args:
            intelligence_count: Number of intelligence artifacts extracted
            message_count: Total number of messages
            duration_seconds: Conversation duration in seconds
            
        Returns:
            IDR score (artifacts per hour per message)
        """
        if message_count == 0 or duration_seconds == 0:
            return 0.0
        
        # Artifacts per message
        artifacts_per_message = intelligence_count / message_count
        
        # Normalize to per hour (3600 seconds)
        duration_hours = max(duration_seconds / 3600.0, 0.01)  # Avoid division by zero
        
        idr = artifacts_per_message * (1.0 / duration_hours)
        
        return round(idr, 4)

    def calculate_ids(
        self,
        intelligence_artifacts: List[Dict[str, Any]],
        message_count: int
    ) -> float:
        """
        Calculate Information Disclosure Score (IDS).
        
        IDS = Σ(artifact_value * confidence * weight) / message_count
        Weighted score of artifact quality.
        
        Args:
            intelligence_artifacts: List of extracted intelligence with type and confidence
            message_count: Total number of messages
            
        Returns:
            IDS score (weighted quality per message)
        """
        if message_count == 0:
            return 0.0
        
        total_score = 0.0
        
        for artifact in intelligence_artifacts:
            artifact_type = artifact.get("artifact_type", "unknown")
            confidence = artifact.get("confidence", 0.0)
            
            # Get weight for this artifact type
            weight = self.artifact_weights.get(artifact_type, 0.5)
            
            # Calculate weighted score
            artifact_score = confidence * weight
            total_score += artifact_score
        
        ids = total_score / message_count
        
        return round(ids, 4)

    def calculate_har(
        self,
        scam_type: str,
        intelligence_count: int,
        detection_confidence: float,
        has_payment_request: bool = False,
        has_urgency: bool = False
    ) -> float:
        """
        Calculate Harm Assessment Rate (HAR).
        
        HAR considers scam type severity, intelligence disclosure,
        detection confidence, and behavioral risk factors.
        
        Args:
            scam_type: Type of scam detected
            intelligence_count: Number of intelligence artifacts
            detection_confidence: Confidence in scam detection (0-1)
            has_payment_request: Whether payment was requested
            has_urgency: Whether urgency tactics were used
            
        Returns:
            HAR score (0-1, higher = more harmful)
        """
        # Base harm score from scam type
        base_harm = self.scam_harm_scores.get(scam_type, 0.5)
        
        # Intelligence disclosure factor (more intelligence = higher harm)
        intelligence_factor = min(intelligence_count * 0.1, 0.3)
        
        # Detection confidence factor
        confidence_factor = detection_confidence * 0.2
        
        # Behavioral risk factors
        payment_factor = 0.2 if has_payment_request else 0.0
        urgency_factor = 0.1 if has_urgency else 0.0
        
        # Calculate total HAR
        har = (
            base_harm +
            intelligence_factor +
            confidence_factor +
            payment_factor +
            urgency_factor
        )
        
        # Normalize to 0-1 range
        har = min(har, 1.0)
        
        return round(har, 4)

    def calculate_all_metrics(
        self,
        conversation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate all metrics for a conversation.
        
        Args:
            conversation_data: Dict containing conversation details
            
        Returns:
            Dict with IDR, IDS, HAR, and interpretation
        """
        # Extract data
        intelligence = conversation_data.get("intelligence", [])
        message_count = conversation_data.get("message_count", 0)
        duration_seconds = conversation_data.get("duration_seconds", 0)
        scam_type = conversation_data.get("scam_type", "unknown")
        detection_confidence = conversation_data.get("detection_confidence", 0.0)
        
        # Check for behavioral factors
        messages = conversation_data.get("messages", [])
        has_payment_request = any(
            "pay" in msg.get("content", "").lower() or
            "money" in msg.get("content", "").lower()
            for msg in messages
            if msg.get("sender_type") == "scammer"
        )
        has_urgency = any(
            "urgent" in msg.get("content", "").lower() or
            "immediately" in msg.get("content", "").lower()
            for msg in messages
            if msg.get("sender_type") == "scammer"
        )
        
        # Calculate metrics
        idr = self.calculate_idr(len(intelligence), message_count, duration_seconds)
        ids = self.calculate_ids(intelligence, message_count)
        har = self.calculate_har(
            scam_type,
            len(intelligence),
            detection_confidence,
            has_payment_request,
            has_urgency
        )
        
        # Interpretation
        interpretation = self._interpret_metrics(idr, ids, har)
        
        return {
            "idr": idr,
            "ids": ids,
            "har": har,
            "intelligence_count": len(intelligence),
            "message_count": message_count,
            "duration_hours": round(duration_seconds / 3600.0, 2),
            "interpretation": interpretation
        }

    def _interpret_metrics(
        self, idr: float, ids: float, har: float
    ) -> Dict[str, str]:
        """
        Provide human-readable interpretation of metrics.
        
        Args:
            idr: Information Disclosure Rate
            ids: Information Disclosure Score
            har: Harm Assessment Rate
            
        Returns:
            Dict with interpretation strings
        """
        # IDR interpretation
        if idr > 1.0:
            idr_desc = "Very High - Extremely effective intelligence extraction"
        elif idr > 0.5:
            idr_desc = "High - Good intelligence extraction rate"
        elif idr > 0.2:
            idr_desc = "Moderate - Average intelligence extraction"
        elif idr > 0.0:
            idr_desc = "Low - Limited intelligence extraction"
        else:
            idr_desc = "None - No intelligence extracted"
        
        # IDS interpretation
        if ids > 0.8:
            ids_desc = "Excellent - High-quality, high-confidence intelligence"
        elif ids > 0.5:
            ids_desc = "Good - Quality intelligence artifacts"
        elif ids > 0.3:
            ids_desc = "Fair - Moderate quality intelligence"
        elif ids > 0.0:
            ids_desc = "Poor - Low quality or confidence"
        else:
            ids_desc = "None - No intelligence data"
        
        # HAR interpretation
        if har > 0.8:
            har_desc = "Critical - High potential for significant harm"
        elif har > 0.6:
            har_desc = "High - Substantial harm potential"
        elif har > 0.4:
            har_desc = "Medium - Moderate harm potential"
        elif har > 0.2:
            har_desc = "Low - Limited harm potential"
        else:
            har_desc = "Minimal - Very low harm potential"
        
        return {
            "idr": idr_desc,
            "ids": ids_desc,
            "har": har_desc,
            "overall": self._get_overall_assessment(idr, ids, har)
        }

    def _get_overall_assessment(
        self, idr: float, ids: float, har: float
    ) -> str:
        """Get overall assessment of conversation effectiveness."""
        # High intelligence extraction + high harm = excellent honeypot performance
        if idr > 0.5 and har > 0.7:
            return "Excellent - High-value intelligence from high-threat scam"
        elif idr > 0.3 and ids > 0.5:
            return "Very Good - Quality intelligence extraction"
        elif idr > 0.1 or ids > 0.3:
            return "Good - Useful intelligence gathered"
        elif idr > 0.0 or ids > 0.0:
            return "Fair - Some intelligence obtained"
        else:
            return "Poor - No actionable intelligence"
