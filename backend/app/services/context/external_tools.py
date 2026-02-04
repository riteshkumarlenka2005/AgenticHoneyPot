"""External tools interface for agent tool calling."""
from typing import Dict, Any, List
from app.services.context.whois_lookup import whois_service
from app.services.context.url_expander import url_expander


class ExternalToolsService:
    """Service for calling external tools from the agent."""
    
    def __init__(self):
        """Initialize external tools service."""
        self.available_tools = {
            "whois_lookup": self._whois_lookup_tool,
            "url_expand": self._url_expand_tool,
            "url_safety_check": self._url_safety_check_tool,
            "domain_check": self._domain_check_tool
        }
    
    async def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Call an external tool.
        
        Args:
            tool_name: Name of the tool to call
            **kwargs: Tool-specific arguments
        
        Returns:
            Tool execution result
        """
        if tool_name not in self.available_tools:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
                "available_tools": list(self.available_tools.keys())
            }
        
        try:
            result = await self.available_tools[tool_name](**kwargs)
            return {
                "success": True,
                "tool": tool_name,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "tool": tool_name,
                "error": str(e)
            }
    
    def get_tool_descriptions(self) -> List[Dict[str, Any]]:
        """Get descriptions of all available tools for LLM."""
        return [
            {
                "name": "whois_lookup",
                "description": "Look up domain registration and IP information",
                "parameters": {
                    "domain": "Domain name to lookup (e.g., 'example.com')"
                },
                "example": {"domain": "suspicious-site.com"}
            },
            {
                "name": "url_expand",
                "description": "Expand shortened URLs and trace redirect chains",
                "parameters": {
                    "url": "URL to expand (can be shortened URL)"
                },
                "example": {"url": "https://bit.ly/xyz123"}
            },
            {
                "name": "url_safety_check",
                "description": "Check URL safety without visiting it",
                "parameters": {
                    "url": "URL to check for safety"
                },
                "example": {"url": "https://example.com/suspicious"}
            },
            {
                "name": "domain_check",
                "description": "Check if a domain exists and get basic info",
                "parameters": {
                    "domain": "Domain to check"
                },
                "example": {"domain": "scam-site.com"}
            }
        ]
    
    async def _whois_lookup_tool(self, domain: str) -> Dict:
        """WHOIS lookup tool."""
        return await whois_service.lookup_domain(domain)
    
    async def _url_expand_tool(self, url: str) -> Dict:
        """URL expansion tool."""
        return await url_expander.expand_url(url)
    
    async def _url_safety_check_tool(self, url: str) -> Dict:
        """URL safety check tool."""
        # Combine URL expander safety check with WHOIS
        safety = await url_expander.check_url_safety(url)
        
        # Also check the domain if available
        from urllib.parse import urlparse
        parsed = urlparse(url)
        if parsed.netloc and not whois_service._is_ip_address(parsed.netloc):
            whois_result = await whois_service.check_url(url)
            safety["whois_info"] = whois_result
            
            # Combine risk scores
            if "risk_score" in whois_result:
                safety["combined_risk_score"] = (
                    safety["risk_score"] * 0.5 +
                    whois_result["risk_score"] * 0.5
                )
        
        return safety
    
    async def _domain_check_tool(self, domain: str) -> Dict:
        """Domain check tool."""
        return await whois_service.lookup_domain(domain)


# Global external tools instance
external_tools = ExternalToolsService()
