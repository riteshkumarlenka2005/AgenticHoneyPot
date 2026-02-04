"""STIX 2.1 formatter for exporting intelligence."""
from typing import List, Dict, Any
from datetime import datetime
from uuid import uuid4
import json

from .schemas import (
    STIXBundle,
    STIXIdentity,
    STIXIndicator,
    STIXObservedData,
    STIXRelationship,
    STIXMalware
)


class STIXFormatter:
    """
    Formats honeypot intelligence data into STIX 2.1 format.
    
    STIX (Structured Threat Information Expression) is a standardized
    language for describing cyber threat information.
    """
    
    def __init__(self, organization_name: str = "Agentic HoneyPot"):
        """
        Initialize STIX formatter.
        
        Args:
            organization_name: Name of the organization creating STIX data
        """
        self.organization_name = organization_name
        self.identity_id = f"identity--{uuid4()}"
    
    def create_bundle(
        self,
        conversations: List[Dict[str, Any]],
        intelligence: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create a STIX bundle from honeypot data.
        
        Args:
            conversations: List of conversation dicts
            intelligence: List of intelligence artifact dicts
        
        Returns:
            STIX bundle as dict
        """
        objects = []
        
        # Add identity object (source of intelligence)
        identity = self._create_identity()
        objects.append(identity)
        
        # Create indicators from intelligence artifacts
        for intel in intelligence:
            indicator = self._create_indicator_from_intelligence(intel)
            if indicator:
                objects.append(indicator)
        
        # Create malware objects for scam campaigns
        scam_types = set(c.get("scam_type") for c in conversations if c.get("scam_type"))
        for scam_type in scam_types:
            malware = self._create_malware_object(scam_type)
            objects.append(malware)
        
        # Create observed data
        for conv in conversations:
            if conv.get("intelligence"):
                observed = self._create_observed_data(conv)
                objects.append(observed)
        
        # Create bundle
        bundle = {
            "type": "bundle",
            "id": f"bundle--{uuid4()}",
            "objects": [obj.model_dump() if hasattr(obj, 'model_dump') else obj for obj in objects]
        }
        
        return bundle
    
    def _create_identity(self) -> STIXIdentity:
        """Create STIX identity object for the organization."""
        now = datetime.utcnow().isoformat() + "Z"
        
        return STIXIdentity(
            id=self.identity_id,
            created=now,
            modified=now,
            name=self.organization_name,
            identity_class="organization"
        )
    
    def _create_indicator_from_intelligence(
        self,
        intel: Dict[str, Any]
    ) -> STIXIndicator:
        """
        Create STIX indicator from intelligence artifact.
        
        Args:
            intel: Intelligence artifact dict
        
        Returns:
            STIX Indicator object
        """
        artifact_type = intel.get("artifact_type", "")
        value = intel.get("value", "")
        confidence = intel.get("confidence", 0.0)
        
        # Map artifact types to STIX patterns
        pattern_map = {
            "UPI_ID": lambda v: f"[email-addr:value = '{v}']",
            "EMAIL": lambda v: f"[email-addr:value = '{v}']",
            "PHONE": lambda v: f"[phone-number:value = '{v}']",
            "URL": lambda v: f"[url:value = '{v}']",
            "BANK_ACCOUNT": lambda v: f"[x-bank-account:value = '{v}']",
            "IFSC_CODE": lambda v: f"[x-ifsc-code:value = '{v}']"
        }
        
        pattern_func = pattern_map.get(artifact_type)
        if not pattern_func:
            return None
        
        pattern = pattern_func(value)
        now = datetime.utcnow().isoformat() + "Z"
        
        # Convert confidence (0-1) to STIX confidence (0-100)
        stix_confidence = int(confidence * 100)
        
        return STIXIndicator(
            id=f"indicator--{uuid4()}",
            created=now,
            modified=now,
            pattern=pattern,
            pattern_type="stix",
            valid_from=intel.get("extracted_at", now),
            indicator_types=["malicious-activity", "phishing"],
            description=f"Scam indicator: {artifact_type}",
            labels=["scam", "honeypot-derived"],
            confidence=stix_confidence
        )
    
    def _create_malware_object(self, scam_type: str) -> STIXMalware:
        """Create STIX malware object for scam campaign."""
        now = datetime.utcnow().isoformat() + "Z"
        
        return STIXMalware(
            id=f"malware--{uuid4()}",
            created=now,
            modified=now,
            name=f"{scam_type} Scam Campaign",
            malware_types=["phishing"],
            is_family=True,
            description=f"Scam campaign using {scam_type} tactics"
        )
    
    def _create_observed_data(
        self,
        conversation: Dict[str, Any]
    ) -> STIXObservedData:
        """Create STIX observed data from conversation."""
        now = datetime.utcnow().isoformat() + "Z"
        started_at = conversation.get("started_at", now)
        
        # Build observed objects from intelligence
        observed_objects = {}
        for idx, intel in enumerate(conversation.get("intelligence", [])):
            artifact_type = intel.get("artifact_type", "")
            value = intel.get("value", "")
            
            # Map to STIX Cyber Observable types
            if artifact_type in ["EMAIL", "UPI_ID"]:
                observed_objects[str(idx)] = {
                    "type": "email-addr",
                    "value": value
                }
            elif artifact_type == "PHONE":
                observed_objects[str(idx)] = {
                    "type": "phone-number",
                    "value": value
                }
            elif artifact_type == "URL":
                observed_objects[str(idx)] = {
                    "type": "url",
                    "value": value
                }
        
        return STIXObservedData(
            id=f"observed-data--{uuid4()}",
            created=now,
            modified=now,
            first_observed=started_at,
            last_observed=now,
            number_observed=1,
            objects=observed_objects
        )
    
    def export_to_file(
        self,
        bundle: Dict[str, Any],
        filename: str
    ):
        """
        Export STIX bundle to JSON file.
        
        Args:
            bundle: STIX bundle dict
            filename: Output filename
        """
        with open(filename, 'w') as f:
            json.dump(bundle, f, indent=2)
    
    def validate_bundle(self, bundle: Dict[str, Any]) -> bool:
        """
        Validate STIX bundle structure.
        
        Args:
            bundle: STIX bundle dict
        
        Returns:
            True if valid
        """
        # Basic validation
        if bundle.get("type") != "bundle":
            return False
        
        if "objects" not in bundle:
            return False
        
        # Each object should have required fields
        for obj in bundle["objects"]:
            if not all(k in obj for k in ["type", "id", "created", "modified"]):
                return False
        
        return True
