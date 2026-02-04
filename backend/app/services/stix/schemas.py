"""Pydantic schemas for STIX 2.1 objects."""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import uuid4


class STIXObject(BaseModel):
    """Base STIX object."""
    type: str
    id: str
    created: str
    modified: str
    spec_version: str = "2.1"


class STIXIdentity(STIXObject):
    """STIX Identity object."""
    type: str = "identity"
    name: str
    identity_class: str = "organization"
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "identity",
                "id": "identity--uuid",
                "created": "2024-01-01T00:00:00.000Z",
                "modified": "2024-01-01T00:00:00.000Z",
                "name": "Agentic HoneyPot",
                "identity_class": "organization"
            }
        }


class STIXIndicator(STIXObject):
    """STIX Indicator object."""
    type: str = "indicator"
    pattern: str
    pattern_type: str = "stix"
    valid_from: str
    indicator_types: List[str] = ["malicious-activity"]
    description: Optional[str] = None
    labels: Optional[List[str]] = None
    confidence: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "indicator",
                "id": "indicator--uuid",
                "pattern": "[email-addr:value = 'scammer@example.com']",
                "pattern_type": "stix",
                "valid_from": "2024-01-01T00:00:00.000Z"
            }
        }


class STIXMalware(STIXObject):
    """STIX Malware object."""
    type: str = "malware"
    name: str
    malware_types: List[str]
    is_family: bool = False
    description: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "malware",
                "id": "malware--uuid",
                "name": "Scam Campaign",
                "malware_types": ["phishing"]
            }
        }


class STIXRelationship(STIXObject):
    """STIX Relationship object."""
    type: str = "relationship"
    relationship_type: str
    source_ref: str
    target_ref: str
    description: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "relationship",
                "id": "relationship--uuid",
                "relationship_type": "indicates",
                "source_ref": "indicator--uuid",
                "target_ref": "malware--uuid"
            }
        }


class STIXObservedData(STIXObject):
    """STIX Observed Data object."""
    type: str = "observed-data"
    first_observed: str
    last_observed: str
    number_observed: int
    objects: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "observed-data",
                "id": "observed-data--uuid",
                "first_observed": "2024-01-01T00:00:00.000Z",
                "last_observed": "2024-01-01T00:00:00.000Z",
                "number_observed": 1,
                "objects": {
                    "0": {
                        "type": "email-addr",
                        "value": "scammer@example.com"
                    }
                }
            }
        }


class STIXBundle(BaseModel):
    """STIX Bundle containing multiple objects."""
    type: str = "bundle"
    id: str = Field(default_factory=lambda: f"bundle--{uuid4()}")
    objects: List[STIXObject] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "bundle",
                "id": "bundle--uuid",
                "objects": []
            }
        }
