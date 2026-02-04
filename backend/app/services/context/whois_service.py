"""WHOIS Lookup Service."""
from typing import Dict, Any, Optional
import httpx
from datetime import datetime, timedelta


class WHOISService:
    """
    WHOIS lookup service for domain intelligence.
    
    Provides domain registration information to assess legitimacy
    of URLs shared by scammers.
    """

    def __init__(self):
        """Initialize WHOIS service."""
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = timedelta(hours=24)

    async def lookup_domain(self, domain: str) -> Dict[str, Any]:
        """
        Perform WHOIS lookup for a domain.
        
        Args:
            domain: Domain name to lookup
            
        Returns:
            WHOIS information
        """
        # Check cache
        cached = self._get_cached(domain)
        if cached:
            return cached
        
        # Clean domain
        domain = self._clean_domain(domain)
        
        try:
            # In production, use actual WHOIS API like:
            # - WHOIS API (whoisxmlapi.com)
            # - domaintools.com API
            # - ipwhois library
            
            # For now, return simulated data
            result = await self._simulated_lookup(domain)
            
            # Cache result
            self._cache_result(domain, result)
            
            return result
            
        except Exception as e:
            return {
                "domain": domain,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def _clean_domain(self, domain: str) -> str:
        """Clean and normalize domain name."""
        # Remove protocol
        domain = domain.replace("http://", "").replace("https://", "")
        
        # Remove path
        if "/" in domain:
            domain = domain.split("/")[0]
        
        # Remove www
        if domain.startswith("www."):
            domain = domain[4:]
        
        return domain.lower().strip()

    async def _simulated_lookup(self, domain: str) -> Dict[str, Any]:
        """
        Simulated WHOIS lookup.
        
        In production, this would call actual WHOIS APIs or services.
        """
        # Simulate API call delay
        import asyncio
        await asyncio.sleep(0.1)
        
        # Determine if domain looks suspicious
        suspicious_indicators = []
        
        # Check for suspicious TLDs
        suspicious_tlds = [".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top"]
        if any(domain.endswith(tld) for tld in suspicious_tlds):
            suspicious_indicators.append("suspicious_tld")
        
        # Check for recently registered (simulation)
        is_new = len(domain) > 20 or any(char.isdigit() for char in domain[:5])
        if is_new:
            suspicious_indicators.append("recently_registered")
        
        # Check for random-looking domain
        if sum(1 for c in domain if c.isdigit()) > len(domain) * 0.3:
            suspicious_indicators.append("random_pattern")
        
        # Build result
        result = {
            "domain": domain,
            "status": "success",
            "registrar": "Unknown Registrar" if suspicious_indicators else "GoDaddy LLC",
            "creation_date": (datetime.utcnow() - timedelta(days=15)).isoformat() if is_new 
                           else (datetime.utcnow() - timedelta(days=1000)).isoformat(),
            "expiration_date": (datetime.utcnow() + timedelta(days=365)).isoformat(),
            "registrant_country": "Unknown" if suspicious_indicators else "IN",
            "nameservers": ["ns1.unknown.com", "ns2.unknown.com"],
            "risk_score": min(len(suspicious_indicators) * 0.35, 1.0),
            "suspicious_indicators": suspicious_indicators,
            "is_suspicious": len(suspicious_indicators) > 0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return result

    def _get_cached(self, domain: str) -> Optional[Dict[str, Any]]:
        """Get cached WHOIS data if available and not expired."""
        if domain not in self.cache:
            return None
        
        cached_data = self.cache[domain]
        cached_time = datetime.fromisoformat(cached_data["timestamp"])
        
        if datetime.utcnow() - cached_time > self.cache_ttl:
            # Cache expired
            del self.cache[domain]
            return None
        
        return cached_data

    def _cache_result(self, domain: str, result: Dict[str, Any]) -> None:
        """Cache WHOIS lookup result."""
        self.cache[domain] = result

    async def bulk_lookup(self, domains: list[str]) -> Dict[str, Dict[str, Any]]:
        """
        Perform WHOIS lookup for multiple domains.
        
        Args:
            domains: List of domain names
            
        Returns:
            Dict mapping domains to WHOIS info
        """
        results = {}
        
        for domain in domains:
            results[domain] = await self.lookup_domain(domain)
        
        return results

    def analyze_risk(self, whois_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze risk based on WHOIS data.
        
        Args:
            whois_data: WHOIS lookup result
            
        Returns:
            Risk analysis
        """
        if whois_data.get("status") != "success":
            return {
                "risk_level": "unknown",
                "score": 0.5,
                "factors": ["WHOIS lookup failed"]
            }
        
        risk_factors = []
        score = whois_data.get("risk_score", 0.0)
        
        # Check suspicious indicators
        if whois_data.get("is_suspicious"):
            risk_factors.extend(whois_data.get("suspicious_indicators", []))
        
        # Check age
        if "creation_date" in whois_data:
            creation = datetime.fromisoformat(whois_data["creation_date"])
            age_days = (datetime.utcnow() - creation).days
            
            if age_days < 30:
                risk_factors.append("very_new_domain")
                score += 0.3
            elif age_days < 180:
                risk_factors.append("new_domain")
                score += 0.15
        
        # Determine risk level
        if score > 0.7:
            risk_level = "high"
        elif score > 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "risk_level": risk_level,
            "score": min(score, 1.0),
            "factors": risk_factors,
            "recommendation": self._get_recommendation(risk_level)
        }

    def _get_recommendation(self, risk_level: str) -> str:
        """Get recommendation based on risk level."""
        recommendations = {
            "high": "High risk domain. Likely used for scam. Extract maximum intelligence.",
            "medium": "Medium risk domain. Proceed with caution and gather more information.",
            "low": "Low risk domain. May be legitimate. Verify through other signals.",
            "unknown": "Unable to assess risk. Use alternative verification methods."
        }
        return recommendations.get(risk_level, "Unknown risk level")


# Global WHOIS service instance
whois_service = WHOISService()
