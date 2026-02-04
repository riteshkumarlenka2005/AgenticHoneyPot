"""STIX 2.1 schemas using Pydantic."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class STIXType(str, Enum):
    """STIX 2.1 object types."""
    BUNDLE = "bundle"
    INDICATOR = "indicator"
    OBSERVED_DATA = "observed-data"
    THREAT_ACTOR = "threat-actor"
    ATTACK_PATTERN = "attack-pattern"
    CAMPAIGN = "campaign"
    IDENTITY = "identity"
    REPORT = "report"


class PatternType(str, Enum):
    """STIX pattern types."""
    STIX = "stix"
    PCRE = "pcre"
    SIGMA = "sigma"
    SNORT = "snort"
    YARA = "yara"


class STIXObject(BaseModel):
    """Base STIX 2.1 object."""
    type: str
    spec_version: str = "2.1"
    id: str
    created: str
    modified: str
    
    class Config:
        use_enum_values = True


class STIXIdentity(STIXObject):
    """STIX 2.1 Identity object."""
    type: str = "identity"
    name: str
    identity_class: str = "system"
    sectors: Optional[List[str]] = None
    contact_information: Optional[str] = None


class STIXIndicator(STIXObject):
    """STIX 2.1 Indicator object."""
    type: str = "indicator"
    name: str
    description: Optional[str] = None
    pattern: str
    pattern_type: str = "stix"
    valid_from: str
    valid_until: Optional[str] = None
    labels: List[str] = Field(default_factory=list)
    confidence: Optional[int] = None
    indicator_types: List[str] = Field(default_factory=list)


class STIXObservedData(STIXObject):
    """STIX 2.1 Observed Data object."""
    type: str = "observed-data"
    first_observed: str
    last_observed: str
    number_observed: int = 1
    objects: Dict[str, Any]
    object_refs: Optional[List[str]] = None


class STIXThreatActor(STIXObject):
    """STIX 2.1 Threat Actor object."""
    type: str = "threat-actor"
    name: str
    description: Optional[str] = None
    threat_actor_types: List[str] = Field(default_factory=list)
    aliases: List[str] = Field(default_factory=list)
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    roles: Optional[List[str]] = None
    goals: Optional[List[str]] = None
    sophistication: Optional[str] = None
    resource_level: Optional[str] = None


class STIXAttackPattern(STIXObject):
    """STIX 2.1 Attack Pattern object."""
    type: str = "attack-pattern"
    name: str
    description: Optional[str] = None
    external_references: Optional[List[Dict[str, str]]] = None


class STIXReport(STIXObject):
    """STIX 2.1 Report object."""
    type: str = "report"
    name: str
    description: Optional[str] = None
    published: str
    object_refs: List[str]
    labels: List[str] = Field(default_factory=list)


class STIXBundle(BaseModel):
    """STIX 2.1 Bundle."""
    type: str = "bundle"
    id: str
    objects: List[STIXObject]
    
    class Config:
        use_enum_values = True


# Cyber Observable Objects

class CyberObservableObject(BaseModel):
    """Base class for STIX Cyber Observable Objects."""
    type: str


class EmailAddress(CyberObservableObject):
    """Email Address Observable."""
    type: str = "email-addr"
    value: str
    display_name: Optional[str] = None


class DomainName(CyberObservableObject):
    """Domain Name Observable."""
    type: str = "domain-name"
    value: str


class URL(CyberObservableObject):
    """URL Observable."""
    type: str = "url"
    value: str


class IPv4Address(CyberObservableObject):
    """IPv4 Address Observable."""
    type: str = "ipv4-addr"
    value: str


class UserAccount(CyberObservableObject):
    """User Account Observable."""
    type: str = "user-account"
    user_id: str
    account_login: Optional[str] = None
    account_type: Optional[str] = None
