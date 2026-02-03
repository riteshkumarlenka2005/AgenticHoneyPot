"""Agent memory for conversation context."""
from typing import List, Dict, Any, Optional
from collections import deque


class AgentMemory:
    """Manages agent memory and conversation context."""
    
    def __init__(self, max_history: int = 50):
        """
        Initialize agent memory.
        
        Args:
            max_history: Maximum number of messages to keep in history
        """
        self.max_history = max_history
        self.message_history: deque = deque(maxlen=max_history)
        self.context: Dict[str, Any] = {}
        self.learnings: List[Dict[str, Any]] = []
    
    def add_message(self, sender_type: str, content: str, analysis: Optional[Dict] = None):
        """
        Add a message to history.
        
        Args:
            sender_type: Type of sender (scammer or honeypot)
            content: Message content
            analysis: Optional analysis of the message
        """
        self.message_history.append({
            "sender_type": sender_type,
            "content": content,
            "analysis": analysis or {}
        })
    
    def get_recent_messages(self, count: int = 10) -> List[Dict]:
        """Get recent messages from history."""
        return list(self.message_history)[-count:]
    
    def get_full_history(self) -> List[Dict]:
        """Get full message history."""
        return list(self.message_history)
    
    def update_context(self, key: str, value: Any):
        """Update context variable."""
        self.context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get context variable."""
        return self.context.get(key, default)
    
    def add_learning(self, learning: Dict[str, Any]):
        """
        Add a learning point from the conversation.
        
        Args:
            learning: Dictionary with learning information
        """
        self.learnings.append(learning)
    
    def clear_history(self):
        """Clear message history."""
        self.message_history.clear()
