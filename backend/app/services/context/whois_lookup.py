"""WHOIS domain lookup service."""
import socket
from typing import Optional, Dict
from datetime import datetime
import httpx


class WhoisLookupService:
    """Service for looking up domain information."""
    
    def __init__(self):
        """Initialize WHOIS lookup service."""
        self.timeout = 10
    
    async def lookup_domain(self, domain: str) -> Dict:
        """
        Perform WHOIS lookup for a domain.
        
        Args:
            domain: Domain name to lookup
        
        Returns:
            Dictionary with domain information
        """
        result = {
            "domain": domain,
            "exists": False,
            "ip_address": None,
            "is_suspicious": False,
            "risk_score": 0.0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            # Try to resolve domain to IP
            ip_address = socket.gethostbyname(domain)
            result["exists"] = True
            result["ip_address"] = ip_address
            
            # Check if IP is suspicious (basic checks)
            result["is_suspicious"] = self._is_suspicious_ip(ip_address)
            
            # Calculate risk score
            result["risk_score"] = self._calculate_risk_score(domain, ip_address)
            
        except socket.gaierror:
            # Domain doesn't resolve
            result["exists"] = False
            result["is_suspicious"] = True
            result["risk_score"] = 0.8  # High risk if domain doesn't exist
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    async def check_url(self, url: str) -> Dict:
        """
        Check URL for suspicious characteristics.
        
        Args:
            url: Full URL to check
        
        Returns:
            Dictionary with URL analysis
        """
        from urllib.parse import urlparse
        
        parsed = urlparse(url)
        domain = parsed.netloc
        
        result = {
            "url": url,
            "domain": domain,
            "scheme": parsed.scheme,
            "is_suspicious": False,
            "risk_factors": [],
            "risk_score": 0.0
        }
        
        # Check for suspicious patterns
        if parsed.scheme not in ["http", "https"]:
            result["risk_factors"].append("Non-HTTP(S) scheme")
            result["risk_score"] += 0.3
        
        # Check for IP address instead of domain
        if self._is_ip_address(domain):
            result["risk_factors"].append("IP address instead of domain")
            result["risk_score"] += 0.4
        
        # Check for suspicious keywords in domain
        suspicious_keywords = ["verify", "secure", "account", "login", "update", "confirm"]
        if any(kw in domain.lower() for kw in suspicious_keywords):
            result["risk_factors"].append("Suspicious keywords in domain")
            result["risk_score"] += 0.2
        
        # Check domain length (very long domains can be suspicious)
        if len(domain) > 50:
            result["risk_factors"].append("Unusually long domain")
            result["risk_score"] += 0.1
        
        # Perform domain lookup
        if domain and not self._is_ip_address(domain):
            domain_info = await self.lookup_domain(domain)
            if not domain_info["exists"]:
                result["risk_factors"].append("Domain does not exist")
                result["risk_score"] += 0.5
            elif domain_info["is_suspicious"]:
                result["risk_factors"].append("Suspicious IP address")
                result["risk_score"] += 0.3
        
        result["is_suspicious"] = result["risk_score"] >= 0.5
        result["risk_score"] = min(result["risk_score"], 1.0)
        
        return result
    
    def _is_ip_address(self, s: str) -> bool:
        """Check if string is an IP address."""
        parts = s.split('.')
        if len(parts) != 4:
            return False
        try:
            return all(0 <= int(part) <= 255 for part in parts)
        except ValueError:
            return False
    
    def _is_suspicious_ip(self, ip: str) -> bool:
        """Check if IP address is suspicious."""
        # Check for common suspicious IP ranges (simplified)
        # In production, use threat intelligence feeds
        
        parts = ip.split('.')
        if len(parts) != 4:
            return True
        
        try:
            first_octet = int(parts[0])
            
            # Private IP ranges (shouldn't be used for public websites)
            if first_octet == 10:
                return True
            if first_octet == 172 and 16 <= int(parts[1]) <= 31:
                return True
            if first_octet == 192 and int(parts[1]) == 168:
                return True
            
            # Localhost
            if first_octet == 127:
                return True
            
        except ValueError:
            return True
        
        return False
    
    def _calculate_risk_score(self, domain: str, ip: str) -> float:
        """Calculate risk score for domain."""
        score = 0.0
        
        # Check domain characteristics
        if len(domain) < 5:
            score += 0.2  # Very short domains
        
        if domain.count('.') > 3:
            score += 0.2  # Too many subdomains
        
        # Check IP
        if self._is_suspicious_ip(ip):
            score += 0.4
        
        return min(score, 1.0)


# Global WHOIS service instance
whois_service = WhoisLookupService()
