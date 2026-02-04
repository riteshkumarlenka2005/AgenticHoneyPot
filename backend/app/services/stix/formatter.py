"""STIX 2.1 formatter for intelligence export."""
from typing import List, Dict, Any
from datetime import datetime
from uuid import uuid4
import json

from app.services.stix.schemas import (
    STIXBundle, STIXIdentity, STIXIndicator, STIXObservedData,
    STIXThreatActor, STIXAttackPattern, STIXReport,
    EmailAddress, DomainName, URL, UserAccount
)
from app.models.intelligence import Intelligence, ArtifactType
from app.models.conversation import Conversation


class STIXFormatter:
    """Format intelligence data to STIX 2.1 format."""
    
    def __init__(self):
        """Initialize STIX formatter."""
        self.identity_id = f"identity--{uuid4()}"
    
    def create_identity(self) -> STIXIdentity:
        """Create organization identity."""
        now = datetime.utcnow().isoformat() + "Z"
        
        return STIXIdentity(
            id=self.identity_id,
            created=now,
            modified=now,
            name="Agentic HoneyPot System",
            identity_class="system",
            sectors=["cybersecurity"],
            contact_information="https://github.com/riteshkumarlenka2005/AgenticHoneyPot"
        )
    
    def intelligence_to_stix(
        self,
        intelligence_list: List[Intelligence],
        conversations: Dict[str, Conversation]
    ) -> Dict[str, Any]:
        """
        Convert intelligence artifacts to STIX 2.1 bundle.
        
        Args:
            intelligence_list: List of intelligence artifacts
            conversations: Dictionary mapping conversation IDs to Conversation objects
        
        Returns:
            STIX 2.1 bundle as dictionary
        """
        objects = []
        
        # Add identity
        identity = self.create_identity()
        objects.append(identity.dict(exclude_none=True))
        
        # Group intelligence by conversation
        conv_intelligence = {}
        for intel in intelligence_list:
            conv_id = str(intel.conversation_id)
            if conv_id not in conv_intelligence:
                conv_intelligence[conv_id] = []
            conv_intelligence[conv_id].append(intel)
        
        # Process each conversation
        for conv_id, intel_items in conv_intelligence.items():
            conversation = conversations.get(conv_id)
            
            # Create threat actor for scammer
            if conversation:
                threat_actor = self._create_threat_actor(conversation)
                objects.append(threat_actor.dict(exclude_none=True))
            
            # Create indicators and observed data for each intelligence item
            for intel in intel_items:
                # Create indicator
                indicator = self._create_indicator(intel, conversation)
                objects.append(indicator.dict(exclude_none=True))
                
                # Create observed data
                observed_data = self._create_observed_data(intel, conversation)
                objects.append(observed_data.dict(exclude_none=True))
        
        # Create attack patterns for scam types
        scam_types = {conv.scam_type for conv in conversations.values() if conv.scam_type}
        for scam_type in scam_types:
            attack_pattern = self._create_attack_pattern(scam_type)
            objects.append(attack_pattern.dict(exclude_none=True))
        
        # Create report
        report = self._create_report(objects, intelligence_list)
        objects.insert(1, report.dict(exclude_none=True))  # After identity
        
        # Create bundle
        bundle = STIXBundle(
            id=f"bundle--{uuid4()}",
            objects=objects
        )
        
        return json.loads(bundle.json(exclude_none=True, by_alias=True))
    
    def _create_threat_actor(self, conversation: Conversation) -> STIXThreatActor:
        """Create threat actor from conversation."""
        now = datetime.utcnow().isoformat() + "Z"
        
        return STIXThreatActor(
            id=f"threat-actor--{uuid4()}",
            created=conversation.started_at.isoformat() + "Z",
            modified=now,
            name=f"Scammer: {conversation.scammer_identifier}",
            description=f"Scammer involved in {conversation.scam_type or 'unknown'} scam",
            threat_actor_types=["scammer", "fraudster"],
            aliases=[conversation.scammer_identifier],
            first_seen=conversation.started_at.isoformat() + "Z",
            last_seen=(conversation.last_activity or conversation.started_at).isoformat() + "Z",
            goals=["financial-theft", "identity-theft"],
            sophistication="minimal"
        )
    
    def _create_indicator(
        self,
        intel: Intelligence,
        conversation: Conversation
    ) -> STIXIndicator:
        """Create indicator from intelligence."""
        now = datetime.utcnow().isoformat() + "Z"
        
        # Build STIX pattern
        pattern = self._build_stix_pattern(intel)
        
        # Determine indicator types
        indicator_types = self._get_indicator_types(intel.artifact_type)
        
        return STIXIndicator(
            id=f"indicator--{uuid4()}",
            created=intel.extracted_at.isoformat() + "Z",
            modified=now,
            name=f"{intel.artifact_type.value}: {intel.value}",
            description=f"Extracted from {conversation.scam_type or 'unknown'} scam conversation",
            pattern=pattern,
            pattern_type="stix",
            valid_from=intel.extracted_at.isoformat() + "Z",
            labels=["scam", intel.artifact_type.value, conversation.scam_type or "unknown"],
            confidence=int(intel.confidence * 100),
            indicator_types=indicator_types
        )
    
    def _create_observed_data(
        self,
        intel: Intelligence,
        conversation: Conversation
    ) -> STIXObservedData:
        """Create observed data from intelligence."""
        now = datetime.utcnow().isoformat() + "Z"
        
        # Create cyber observable object
        observable = self._create_observable(intel)
        
        return STIXObservedData(
            id=f"observed-data--{uuid4()}",
            created=intel.extracted_at.isoformat() + "Z",
            modified=now,
            first_observed=intel.extracted_at.isoformat() + "Z",
            last_observed=intel.extracted_at.isoformat() + "Z",
            number_observed=1,
            objects={"0": observable}
        )
    
    def _create_attack_pattern(self, scam_type: str) -> STIXAttackPattern:
        """Create attack pattern for scam type."""
        now = datetime.utcnow().isoformat() + "Z"
        
        descriptions = {
            "lottery_prize": "Fraudulent lottery/prize scam where victim is told they won a prize",
            "bank_kyc_fraud": "Fake KYC update request to steal banking credentials",
            "investment_fraud": "Fraudulent investment scheme promising high returns",
            "tech_support": "Fake tech support scam claiming computer issues",
            "job_scam": "Fake job offer requiring upfront payment"
        }
        
        return STIXAttackPattern(
            id=f"attack-pattern--{uuid4()}",
            created=now,
            modified=now,
            name=scam_type.replace("_", " ").title(),
            description=descriptions.get(scam_type, f"{scam_type} scam pattern")
        )
    
    def _create_report(
        self,
        objects: List[Dict],
        intelligence_list: List[Intelligence]
    ) -> STIXReport:
        """Create report summarizing the intelligence."""
        now = datetime.utcnow().isoformat() + "Z"
        
        object_refs = [obj["id"] for obj in objects if obj.get("id") != self.identity_id]
        
        return STIXReport(
            id=f"report--{uuid4()}",
            created=now,
            modified=now,
            name="Honeypot Intelligence Report",
            description=f"Intelligence gathered from honeypot operations. Contains {len(intelligence_list)} artifacts.",
            published=now,
            object_refs=object_refs,
            labels=["threat-report", "honeypot", "scam-intelligence"]
        )
    
    def _build_stix_pattern(self, intel: Intelligence) -> str:
        """Build STIX pattern for indicator."""
        artifact_type = intel.artifact_type
        value = intel.value.replace("'", "\\'")  # Escape quotes
        
        if artifact_type == ArtifactType.EMAIL:
            return f"[email-addr:value = '{value}']"
        elif artifact_type == ArtifactType.URL:
            return f"[url:value = '{value}']"
        elif artifact_type == ArtifactType.PHONE:
            return f"[x-phone-number:value = '{value}']"
        elif artifact_type == ArtifactType.UPI_ID:
            return f"[x-upi-id:value = '{value}']"
        elif artifact_type == ArtifactType.BANK_ACCOUNT:
            return f"[x-bank-account:number = '{value}']"
        elif artifact_type == ArtifactType.IFSC_CODE:
            return f"[x-ifsc-code:value = '{value}']"
        else:
            return f"[x-artifact:value = '{value}']"
    
    def _get_indicator_types(self, artifact_type: ArtifactType) -> List[str]:
        """Get STIX indicator types for artifact type."""
        mapping = {
            ArtifactType.EMAIL: ["malicious-activity", "attribution"],
            ArtifactType.URL: ["malicious-activity", "phishing"],
            ArtifactType.PHONE: ["malicious-activity", "attribution"],
            ArtifactType.UPI_ID: ["malicious-activity", "attribution"],
            ArtifactType.BANK_ACCOUNT: ["malicious-activity", "attribution"],
            ArtifactType.IFSC_CODE: ["malicious-activity", "attribution"]
        }
        return mapping.get(artifact_type, ["malicious-activity"])
    
    def _create_observable(self, intel: Intelligence) -> Dict:
        """Create cyber observable object."""
        artifact_type = intel.artifact_type
        
        if artifact_type == ArtifactType.EMAIL:
            return EmailAddress(value=intel.value).dict()
        elif artifact_type == ArtifactType.URL:
            return URL(value=intel.value).dict()
        elif artifact_type == ArtifactType.PHONE:
            return {"type": "x-phone-number", "value": intel.value}
        elif artifact_type == ArtifactType.UPI_ID:
            return {"type": "x-upi-id", "value": intel.value}
        elif artifact_type == ArtifactType.BANK_ACCOUNT:
            return {"type": "x-bank-account", "number": intel.value}
        elif artifact_type == ArtifactType.IFSC_CODE:
            return {"type": "x-ifsc-code", "value": intel.value}
        else:
            return {"type": "x-artifact", "value": intel.value}


# Global STIX formatter instance
stix_formatter = STIXFormatter()
