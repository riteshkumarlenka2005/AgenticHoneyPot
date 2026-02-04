"""URL expander for tracing redirect chains."""
import httpx
from typing import List, Dict, Optional
from datetime import datetime


class URLExpanderService:
    """Service for expanding shortened URLs and tracing redirects."""
    
    def __init__(self):
        """Initialize URL expander service."""
        self.timeout = 10
        self.max_redirects = 10
        self.user_agent = "Mozilla/5.0 (compatible; HoneyPotBot/1.0)"
    
    async def expand_url(self, url: str) -> Dict:
        """
        Expand a URL and trace all redirects.
        
        Args:
            url: URL to expand
        
        Returns:
            Dictionary with redirect chain and final destination
        """
        result = {
            "original_url": url,
            "final_url": None,
            "redirect_chain": [],
            "redirect_count": 0,
            "is_shortened": False,
            "is_suspicious": False,
            "risk_score": 0.0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Check if URL is from a known URL shortener
        result["is_shortened"] = self._is_shortened_url(url)
        
        try:
            async with httpx.AsyncClient(
                follow_redirects=False,
                timeout=self.timeout,
                headers={"User-Agent": self.user_agent}
            ) as client:
                current_url = url
                visited_urls = {url}
                
                for i in range(self.max_redirects):
                    try:
                        response = await client.get(current_url, follow_redirects=False)
                        
                        # Add to chain
                        result["redirect_chain"].append({
                            "url": current_url,
                            "status_code": response.status_code,
                            "step": i + 1
                        })
                        
                        # Check if redirect
                        if response.status_code in [301, 302, 303, 307, 308]:
                            next_url = response.headers.get("location")
                            if not next_url:
                                break
                            
                            # Handle relative URLs
                            if not next_url.startswith("http"):
                                from urllib.parse import urljoin
                                next_url = urljoin(current_url, next_url)
                            
                            # Check for redirect loop
                            if next_url in visited_urls:
                                result["is_suspicious"] = True
                                result["risk_score"] = 0.9
                                break
                            
                            visited_urls.add(next_url)
                            current_url = next_url
                        else:
                            # Final destination reached
                            result["final_url"] = current_url
                            break
                    
                    except httpx.HTTPError:
                        break
                
                result["redirect_count"] = len(result["redirect_chain"]) - 1
                
                # Calculate risk score
                result["risk_score"] = self._calculate_risk_score(result)
                result["is_suspicious"] = result["risk_score"] >= 0.6
        
        except Exception as e:
            result["error"] = str(e)
            result["is_suspicious"] = True
            result["risk_score"] = 0.7
        
        return result
    
    async def check_url_safety(self, url: str) -> Dict:
        """
        Perform safety checks on a URL without actually visiting it.
        
        Args:
            url: URL to check
        
        Returns:
            Dictionary with safety information
        """
        from urllib.parse import urlparse
        
        parsed = urlparse(url)
        
        result = {
            "url": url,
            "is_shortened": self._is_shortened_url(url),
            "domain": parsed.netloc,
            "scheme": parsed.scheme,
            "is_suspicious": False,
            "risk_factors": [],
            "risk_score": 0.0
        }
        
        # Check scheme
        if parsed.scheme not in ["http", "https"]:
            result["risk_factors"].append("Non-HTTP(S) scheme")
            result["risk_score"] += 0.4
        
        # Check for suspicious patterns
        if "@" in url:
            result["risk_factors"].append("@ symbol in URL (phishing indicator)")
            result["risk_score"] += 0.5
        
        # Check for multiple subdomains
        if parsed.netloc.count('.') > 3:
            result["risk_factors"].append("Multiple subdomains")
            result["risk_score"] += 0.2
        
        # Check for URL encoding obfuscation
        if '%' in url:
            encoded_count = url.count('%')
            if encoded_count > 5:
                result["risk_factors"].append("Excessive URL encoding")
                result["risk_score"] += 0.3
        
        result["is_suspicious"] = result["risk_score"] >= 0.5
        result["risk_score"] = min(result["risk_score"], 1.0)
        
        return result
    
    def _is_shortened_url(self, url: str) -> bool:
        """Check if URL is from a known URL shortener."""
        shorteners = [
            "bit.ly", "tinyurl.com", "goo.gl", "ow.ly", "t.co",
            "is.gd", "buff.ly", "adf.ly", "bl.ink", "short.link",
            "cutt.ly", "tiny.cc", "rb.gy", "s.id"
        ]
        
        url_lower = url.lower()
        return any(shortener in url_lower for shortener in shorteners)
    
    def _calculate_risk_score(self, expand_result: Dict) -> float:
        """Calculate risk score based on redirect chain."""
        score = 0.0
        
        # Long redirect chains are suspicious
        if expand_result["redirect_count"] > 5:
            score += 0.4
        elif expand_result["redirect_count"] > 3:
            score += 0.2
        
        # URL shorteners add risk
        if expand_result["is_shortened"]:
            score += 0.1
        
        # Check if final URL is very different from original
        if expand_result["final_url"]:
            from urllib.parse import urlparse
            original_domain = urlparse(expand_result["original_url"]).netloc
            final_domain = urlparse(expand_result["final_url"]).netloc
            
            if original_domain != final_domain:
                score += 0.2
        
        return min(score, 1.0)


# Global URL expander instance
url_expander = URLExpanderService()
