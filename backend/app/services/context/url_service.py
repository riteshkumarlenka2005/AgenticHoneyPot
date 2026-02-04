"""URL Expansion Service for shortened links."""
from typing import Dict, Any, Optional
import httpx
from datetime import datetime
import re


class URLExpansionService:
    """
    URL expansion service for shortened links.
    
    Expands shortened URLs (bit.ly, tinyurl, etc.) to reveal actual destination
    without actually visiting the link (for safety).
    """

    def __init__(self):
        """Initialize URL expansion service."""
        self.cache: Dict[str, str] = {}
        
        # Common URL shortener patterns
        self.shortener_patterns = [
            r"bit\.ly",
            r"tinyurl\.com",
            r"t\.co",
            r"goo\.gl",
            r"ow\.ly",
            r"is\.gd",
            r"buff\.ly",
            r"adf\.ly",
            r"short\.link",
            r"cutt\.ly",
        ]

    def is_shortened_url(self, url: str) -> bool:
        """
        Check if URL is a shortened link.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL appears to be shortened
        """
        for pattern in self.shortener_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        return False

    async def expand_url(self, short_url: str) -> Dict[str, Any]:
        """
        Expand a shortened URL to reveal destination.
        
        Args:
            short_url: Shortened URL
            
        Returns:
            Expansion result with destination URL
        """
        # Check cache
        if short_url in self.cache:
            return {
                "original": short_url,
                "expanded": self.cache[short_url],
                "cached": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Safety check
        if not self.is_shortened_url(short_url):
            return {
                "original": short_url,
                "expanded": short_url,
                "is_shortened": False,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        try:
            # Expand URL using HEAD request (safer than GET)
            expanded = await self._expand_safe(short_url)
            
            # Cache result
            self.cache[short_url] = expanded
            
            return {
                "original": short_url,
                "expanded": expanded,
                "is_shortened": True,
                "cached": False,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "original": short_url,
                "expanded": None,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def _expand_safe(self, url: str) -> str:
        """
        Safely expand URL using HEAD request.
        
        Args:
            url: URL to expand
            
        Returns:
            Expanded URL
        """
        # Ensure URL has protocol
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        try:
            async with httpx.AsyncClient(
                follow_redirects=True,
                timeout=10.0
            ) as client:
                # Use HEAD request to avoid downloading content
                response = await client.head(url)
                
                # Return final URL after redirects
                return str(response.url)
                
        except httpx.HTTPError:
            # Fallback: try GET request with minimal data
            try:
                async with httpx.AsyncClient(
                    follow_redirects=True,
                    timeout=10.0
                ) as client:
                    # Only read headers, not body
                    response = await client.get(url, stream=True)
                    await response.aclose()
                    return str(response.url)
            except Exception:
                # If all fails, return original URL
                return url

    async def analyze_url(self, url: str) -> Dict[str, Any]:
        """
        Analyze URL for safety and extract information.
        
        Args:
            url: URL to analyze
            
        Returns:
            URL analysis
        """
        analysis = {
            "url": url,
            "is_shortened": self.is_shortened_url(url),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Expand if shortened
        if analysis["is_shortened"]:
            expansion = await self.expand_url(url)
            analysis["expanded_url"] = expansion.get("expanded")
            url_to_analyze = expansion.get("expanded", url)
        else:
            url_to_analyze = url
        
        # Extract domain
        domain_match = re.search(r"(?:https?://)?(?:www\.)?([^/]+)", url_to_analyze)
        if domain_match:
            analysis["domain"] = domain_match.group(1)
        
        # Check for suspicious patterns
        analysis["suspicious_indicators"] = []
        
        # Check for IP address instead of domain
        if re.match(r"\d+\.\d+\.\d+\.\d+", url_to_analyze):
            analysis["suspicious_indicators"].append("ip_address_url")
        
        # Check for excessive subdomains
        if url_to_analyze.count(".") > 3:
            analysis["suspicious_indicators"].append("excessive_subdomains")
        
        # Check for suspicious keywords
        suspicious_keywords = ["login", "verify", "account", "secure", "update", "confirm"]
        if any(keyword in url_to_analyze.lower() for keyword in suspicious_keywords):
            analysis["suspicious_indicators"].append("phishing_keywords")
        
        # Check for suspicious TLD
        suspicious_tlds = [".tk", ".ml", ".ga", ".cf", ".gq"]
        if any(url_to_analyze.endswith(tld) for tld in suspicious_tlds):
            analysis["suspicious_indicators"].append("suspicious_tld")
        
        # Calculate risk score
        analysis["risk_score"] = min(len(analysis["suspicious_indicators"]) * 0.25, 1.0)
        analysis["is_suspicious"] = analysis["risk_score"] > 0.5
        
        return analysis

    async def bulk_expand(self, urls: list[str]) -> Dict[str, Dict[str, Any]]:
        """
        Expand multiple URLs.
        
        Args:
            urls: List of URLs to expand
            
        Returns:
            Dict mapping original URLs to expansion results
        """
        results = {}
        
        for url in urls:
            if self.is_shortened_url(url):
                results[url] = await self.expand_url(url)
            else:
                results[url] = {
                    "original": url,
                    "expanded": url,
                    "is_shortened": False
                }
        
        return results

    def extract_urls(self, text: str) -> list[str]:
        """
        Extract URLs from text.
        
        Args:
            text: Text to search
            
        Returns:
            List of found URLs
        """
        # URL pattern
        url_pattern = r"https?://[^\s]+"
        urls = re.findall(url_pattern, text, re.IGNORECASE)
        
        # Also find URLs without protocol
        domain_pattern = r"(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?"
        potential_urls = re.findall(domain_pattern, text)
        
        # Add potential URLs that look like shortened links
        for potential in potential_urls:
            if self.is_shortened_url(potential) and potential not in urls:
                urls.append(potential)
        
        return urls

    async def process_message_urls(self, message: str) -> Dict[str, Any]:
        """
        Extract and analyze all URLs in a message.
        
        Args:
            message: Message text
            
        Returns:
            URL analysis results
        """
        urls = self.extract_urls(message)
        
        if not urls:
            return {
                "found_urls": False,
                "count": 0,
                "urls": []
            }
        
        analyses = []
        for url in urls:
            analysis = await self.analyze_url(url)
            analyses.append(analysis)
        
        # Calculate overall risk
        max_risk = max(a.get("risk_score", 0) for a in analyses) if analyses else 0
        
        return {
            "found_urls": True,
            "count": len(urls),
            "urls": analyses,
            "max_risk_score": max_risk,
            "has_suspicious_urls": any(a.get("is_suspicious") for a in analyses)
        }


# Global URL service instance
url_service = URLExpansionService()
