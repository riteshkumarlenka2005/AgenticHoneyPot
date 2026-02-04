"""STIX 2.1 Threat Intelligence Export."""
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import uuid4, UUID
import json


class STIXExporter:
    """
    STIX 2.1 exporter for threat intelligence sharing.
    
    Converts honeypot intelligence into STIX 2.1 format for
    sharing with threat intelligence platforms and security teams.
    """

    def __init__(self):
        """Initialize STIX exporter."""
        self.stix_version = "2.1"
        self.spec_version = "2.1"

    def export_conversation(
        self,
        conversation: Dict[str, Any],
        intelligence: List[Dict[str, Any]],
        include_messages: bool = False
    ) -> Dict[str, Any]:
        """
        Export conversation as STIX bundle.
        
        Args:
            conversation: Conversation data
            intelligence: Extracted intelligence artifacts
            include_messages: Whether to include message content
            
        Returns:
            STIX 2.1 bundle
        """
        objects = []
        
        # Create threat actor
        threat_actor = self._create_threat_actor(conversation)
        objects.append(threat_actor)
        
        # Create campaign if scam type is known
        if conversation.get("scam_type"):
            campaign = self._create_campaign(conversation)
            objects.append(campaign)
        
        # Create indicators from intelligence
        for artifact in intelligence:
            indicator = self._create_indicator(artifact, threat_actor["id"])
            if indicator:
                objects.append(indicator)
        
        # Create observed data
        observed_data = self._create_observed_data(
            conversation,
            intelligence,
            include_messages
        )
        objects.append(observed_data)
        
        # Create identity (our honeypot)
        identity = self._create_identity()
        objects.append(identity)
        
        # Create bundle
        bundle = {
            "type": "bundle",
            "id": f"bundle--{uuid4()}",
            "spec_version": self.spec_version,
            "objects": objects
        }
        
        return bundle

    def _create_threat_actor(self, conversation: Dict[str, Any]) -> Dict[str, Any]:
        """Create STIX threat actor object."""
        actor_id = f"threat-actor--{uuid4()}"
        
        return {
            "type": "threat-actor",
            "spec_version": self.spec_version,
            "id": actor_id,
            "created": datetime.utcnow().isoformat() + "Z",
            "modified": datetime.utcnow().isoformat() + "Z",
            "name": conversation.get("scammer_identifier", "Unknown Scammer"),
            "description": f"Scammer engaged in {conversation.get('scam_type', 'unknown')} scam",
            "threat_actor_types": ["criminal"],
            "aliases": [conversation.get("scammer_identifier")],
            "goals": [f"Execute {conversation.get('scam_type', 'fraud')} scam"],
            "sophistication": "minimal",
            "resource_level": "individual",
        }

    def _create_campaign(self, conversation: Dict[str, Any]) -> Dict[str, Any]:
        """Create STIX campaign object."""
        campaign_id = f"campaign--{uuid4()}"
        scam_type = conversation.get("scam_type", "unknown")
        
        return {
            "type": "campaign",
            "spec_version": self.spec_version,
            "id": campaign_id,
            "created": datetime.utcnow().isoformat() + "Z",
            "modified": datetime.utcnow().isoformat() + "Z",
            "name": f"{scam_type.replace('_', ' ').title()} Campaign",
            "description": f"Observed {scam_type} scam campaign",
            "first_seen": conversation.get("started_at", datetime.utcnow().isoformat()),
            "last_seen": conversation.get("last_activity", datetime.utcnow().isoformat()),
            "objective": "Financial fraud through social engineering",
        }

    def _create_indicator(
        self,
        artifact: Dict[str, Any],
        threat_actor_id: str
    ) -> Optional[Dict[str, Any]]:
        """Create STIX indicator from intelligence artifact."""
        artifact_type = artifact.get("artifact_type")
        value = artifact.get("value")
        
        if not artifact_type or not value:
            return None
        
        # Map artifact types to STIX patterns
        pattern_mappings = {
            "phone": f"[phone-number:value = '{value}']",
            "email": f"[email-addr:value = '{value}']",
            "url": f"[url:value = '{value}']",
            "upi_id": f"[x-upi-id:value = '{value}']",
            "bank_account": f"[x-bank-account:value = '{value}']",
            "ifsc_code": f"[x-ifsc-code:value = '{value}']",
        }
        
        pattern = pattern_mappings.get(artifact_type)
        if not pattern:
            # Generic pattern for unknown types
            pattern = f"[x-custom:type = '{artifact_type}' AND x-custom:value = '{value}']"
        
        indicator_id = f"indicator--{uuid4()}"
        
        return {
            "type": "indicator",
            "spec_version": self.spec_version,
            "id": indicator_id,
            "created": artifact.get("extracted_at", datetime.utcnow().isoformat()),
            "modified": datetime.utcnow().isoformat() + "Z",
            "name": f"{artifact_type.upper()} Indicator",
            "description": f"Scammer {artifact_type}: {value}",
            "pattern": pattern,
            "pattern_type": "stix",
            "valid_from": artifact.get("extracted_at", datetime.utcnow().isoformat()),
            "indicator_types": ["malicious-activity"],
            "confidence": int(artifact.get("confidence", 0.5) * 100),
        }

    def _create_observed_data(
        self,
        conversation: Dict[str, Any],
        intelligence: List[Dict[str, Any]],
        include_messages: bool = False
    ) -> Dict[str, Any]:
        """Create STIX observed data object."""
        observed_id = f"observed-data--{uuid4()}"
        
        # Build objects dict
        objects_dict = {}
        
        # Add intelligence artifacts as observables
        for i, artifact in enumerate(intelligence):
            obj_id = str(i)
            artifact_type = artifact.get("artifact_type")
            value = artifact.get("value")
            
            if artifact_type == "phone":
                objects_dict[obj_id] = {
                    "type": "phone-number",
                    "value": value
                }
            elif artifact_type == "email":
                objects_dict[obj_id] = {
                    "type": "email-addr",
                    "value": value
                }
            elif artifact_type == "url":
                objects_dict[obj_id] = {
                    "type": "url",
                    "value": value
                }
            else:
                # Custom observable for UPI, bank accounts, etc.
                objects_dict[obj_id] = {
                    "type": f"x-{artifact_type}",
                    "value": value
                }
        
        observed_data = {
            "type": "observed-data",
            "spec_version": self.spec_version,
            "id": observed_id,
            "created": datetime.utcnow().isoformat() + "Z",
            "modified": datetime.utcnow().isoformat() + "Z",
            "first_observed": conversation.get("started_at", datetime.utcnow().isoformat()),
            "last_observed": conversation.get("last_activity", datetime.utcnow().isoformat()),
            "number_observed": 1,
            "objects": objects_dict,
        }
        
        return observed_data

    def _create_identity(self) -> Dict[str, Any]:
        """Create identity for the honeypot organization."""
        return {
            "type": "identity",
            "spec_version": self.spec_version,
            "id": f"identity--{uuid4()}",
            "created": datetime.utcnow().isoformat() + "Z",
            "modified": datetime.utcnow().isoformat() + "Z",
            "name": "Agentic HoneyPot System",
            "description": "AI-powered honeypot for scam detection and intelligence gathering",
            "identity_class": "system",
            "sectors": ["technology"],
        }

    def export_intelligence_batch(
        self,
        intelligence_list: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Export batch of intelligence as STIX bundle.
        
        Args:
            intelligence_list: List of intelligence artifacts
            metadata: Optional metadata about the batch
            
        Returns:
            STIX 2.1 bundle
        """
        objects = []
        
        # Create identity
        identity = self._create_identity()
        objects.append(identity)
        
        # Group by conversation
        by_conversation: Dict[str, List[Dict]] = {}
        for artifact in intelligence_list:
            conv_id = artifact.get("conversation_id", "unknown")
            if conv_id not in by_conversation:
                by_conversation[conv_id] = []
            by_conversation[conv_id].append(artifact)
        
        # Create indicators for each artifact
        for conv_id, artifacts in by_conversation.items():
            # Create a threat actor for this conversation
            threat_actor = {
                "type": "threat-actor",
                "spec_version": self.spec_version,
                "id": f"threat-actor--{uuid4()}",
                "created": datetime.utcnow().isoformat() + "Z",
                "modified": datetime.utcnow().isoformat() + "Z",
                "name": f"Scammer-{conv_id}",
                "threat_actor_types": ["criminal"],
            }
            objects.append(threat_actor)
            
            # Create indicators
            for artifact in artifacts:
                indicator = self._create_indicator(artifact, threat_actor["id"])
                if indicator:
                    objects.append(indicator)
        
        # Create bundle
        bundle = {
            "type": "bundle",
            "id": f"bundle--{uuid4()}",
            "spec_version": self.spec_version,
            "objects": objects
        }
        
        if metadata:
            bundle["x_metadata"] = metadata
        
        return bundle

    def export_to_json(
        self,
        stix_object: Dict[str, Any],
        pretty: bool = True
    ) -> str:
        """
        Export STIX object to JSON string.
        
        Args:
            stix_object: STIX object or bundle
            pretty: Whether to pretty-print
            
        Returns:
            JSON string
        """
        if pretty:
            return json.dumps(stix_object, indent=2, sort_keys=True)
        else:
            return json.dumps(stix_object)

    def validate_bundle(self, bundle: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate STIX bundle structure.
        
        Args:
            bundle: STIX bundle to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check required fields
        if bundle.get("type") != "bundle":
            errors.append("Object type must be 'bundle'")
        
        if "id" not in bundle:
            errors.append("Bundle must have an 'id'")
        
        if bundle.get("spec_version") != self.spec_version:
            errors.append(f"Spec version must be {self.spec_version}")
        
        if "objects" not in bundle or not isinstance(bundle["objects"], list):
            errors.append("Bundle must contain 'objects' list")
        
        # Check each object has required fields
        for i, obj in enumerate(bundle.get("objects", [])):
            if "type" not in obj:
                errors.append(f"Object {i} missing 'type'")
            if "id" not in obj:
                errors.append(f"Object {i} missing 'id'")
            if "spec_version" not in obj:
                errors.append(f"Object {i} missing 'spec_version'")
        
        return (len(errors) == 0, errors)


# Global STIX exporter instance
stix_exporter = STIXExporter()
