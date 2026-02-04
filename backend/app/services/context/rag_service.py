"""RAG (Retrieval-Augmented Generation) Service."""
from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime


class Document:
    """Document for RAG storage."""

    def __init__(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        embedding: Optional[np.ndarray] = None
    ):
        """Initialize document."""
        self.content = content
        self.metadata = metadata or {}
        self.embedding = embedding
        self.id = self.metadata.get("id", str(hash(content)))


class RAGService:
    """
    RAG Integration Service.
    
    Provides policy document storage and retrieval using vector similarity search.
    In production, this would integrate with vector databases like Pinecone, Weaviate, or Chroma.
    """

    def __init__(self):
        """Initialize RAG service."""
        self.documents: List[Document] = []
        self.policy_documents: List[Document] = []
        self._initialize_default_policies()

    def _initialize_default_policies(self):
        """Initialize with default policy documents."""
        default_policies = [
            {
                "content": "Never provide real personal information including Aadhaar, PAN, or passport numbers. "
                          "Always use simulated data from the assigned persona.",
                "metadata": {"type": "safety", "priority": "critical"}
            },
            {
                "content": "Never send real money or perform actual financial transactions. "
                          "The honeypot operates in a simulated environment only.",
                "metadata": {"type": "safety", "priority": "critical"}
            },
            {
                "content": "Extract intelligence by asking clarifying questions about payment methods, "
                          "contact information, and organizational details.",
                "metadata": {"type": "strategy", "priority": "high"}
            },
            {
                "content": "When scammers create urgency, respond with technical difficulties or "
                          "need for verification to extend the conversation and gather more intelligence.",
                "metadata": {"type": "strategy", "priority": "medium"}
            },
            {
                "content": "Common scam types include: lottery scams, tech support scams, romance scams, "
                          "investment fraud, job scams, and phishing attempts. Each requires different engagement strategies.",
                "metadata": {"type": "knowledge", "priority": "medium"}
            },
            {
                "content": "UPI IDs typically follow pattern: name@bank or phonenumber@bank. "
                          "Bank account numbers are 9-18 digits. IFSC codes are 11 characters.",
                "metadata": {"type": "knowledge", "priority": "low"}
            },
            {
                "content": "Maximum conversation duration is 2 hours. Maximum 100 messages per conversation. "
                          "Only engage when scam confidence is above 50%.",
                "metadata": {"type": "operational", "priority": "high"}
            },
            {
                "content": "Maintain persona consistency throughout the conversation. "
                          "Use persona's communication style, backstory, and behavioral traits.",
                "metadata": {"type": "operational", "priority": "high"}
            }
        ]
        
        for policy in default_policies:
            doc = Document(
                content=policy["content"],
                metadata=policy["metadata"]
            )
            self.policy_documents.append(doc)

    def _simple_embedding(self, text: str) -> np.ndarray:
        """
        Create simple embedding using character frequencies.
        
        In production, use actual embedding models like:
        - OpenAI embeddings
        - Sentence transformers
        - Custom trained embeddings
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        # Simple character frequency based embedding (demonstration only)
        text_lower = text.lower()
        
        # Feature vector with various characteristics
        features = [
            len(text) / 1000.0,  # Normalized length
            text.count(' ') / max(len(text), 1),  # Space ratio
            sum(1 for c in text if c.isupper()) / max(len(text), 1),  # Uppercase ratio
            text_lower.count('scam') + text_lower.count('fraud'),  # Scam keywords
            text_lower.count('money') + text_lower.count('payment'),  # Financial keywords
            text_lower.count('urgent') + text_lower.count('immediately'),  # Urgency keywords
            text_lower.count('verify') + text_lower.count('confirm'),  # Verification keywords
            text_lower.count('personal') + text_lower.count('information'),  # Info keywords
        ]
        
        return np.array(features, dtype=np.float32)

    def add_document(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add document to RAG store.
        
        Args:
            content: Document content
            metadata: Optional metadata
            
        Returns:
            Document ID
        """
        embedding = self._simple_embedding(content)
        doc = Document(content=content, metadata=metadata, embedding=embedding)
        self.documents.append(doc)
        return doc.id

    def similarity_search(
        self,
        query: str,
        k: int = 3,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using vector similarity.
        
        Args:
            query: Search query
            k: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of similar documents with scores
        """
        # Combine policy documents and user documents
        all_docs = self.policy_documents + self.documents
        
        # Filter by metadata if provided
        if filter_metadata:
            filtered_docs = []
            for doc in all_docs:
                match = all(
                    doc.metadata.get(key) == value
                    for key, value in filter_metadata.items()
                )
                if match:
                    filtered_docs.append(doc)
            all_docs = filtered_docs
        
        if not all_docs:
            return []
        
        # Generate query embedding
        query_embedding = self._simple_embedding(query)
        
        # Calculate similarities
        similarities = []
        for doc in all_docs:
            if doc.embedding is None:
                doc.embedding = self._simple_embedding(doc.content)
            
            # Cosine similarity
            similarity = np.dot(query_embedding, doc.embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc.embedding) + 1e-8
            )
            similarities.append((doc, float(similarity)))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top k
        results = []
        for doc, score in similarities[:k]:
            results.append({
                "content": doc.content,
                "metadata": doc.metadata,
                "similarity_score": round(score, 4),
                "id": doc.id
            })
        
        return results

    def retrieve_context(
        self,
        query: str,
        context_type: Optional[str] = None,
        k: int = 3
    ) -> str:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: Query text
            context_type: Filter by type (safety, strategy, knowledge, operational)
            k: Number of documents to retrieve
            
        Returns:
            Formatted context string
        """
        filter_metadata = {"type": context_type} if context_type else None
        results = self.similarity_search(query, k=k, filter_metadata=filter_metadata)
        
        if not results:
            return "No relevant context found."
        
        context_parts = ["=== Relevant Context ==="]
        for i, result in enumerate(results, 1):
            context_parts.append(f"\n{i}. {result['content']}")
            if result.get("metadata", {}).get("priority"):
                context_parts.append(f"   [Priority: {result['metadata']['priority']}]")
        
        return "\n".join(context_parts)

    def get_safety_policies(self) -> List[str]:
        """Get all critical safety policies."""
        return [
            doc.content
            for doc in self.policy_documents
            if doc.metadata.get("type") == "safety"
            and doc.metadata.get("priority") == "critical"
        ]

    def get_strategy_guidance(self, scam_type: Optional[str] = None) -> List[str]:
        """
        Get strategy guidance for handling scams.
        
        Args:
            scam_type: Optional scam type filter
            
        Returns:
            List of strategy recommendations
        """
        strategies = [
            doc.content
            for doc in self.policy_documents
            if doc.metadata.get("type") == "strategy"
        ]
        
        # In production, filter by scam_type
        return strategies

    def update_knowledge_base(
        self,
        scam_type: str,
        intelligence: Dict[str, Any],
        effectiveness: float
    ) -> None:
        """
        Update knowledge base with learnings from conversations.
        
        Args:
            scam_type: Type of scam
            intelligence: Intelligence extracted
            effectiveness: Effectiveness score (0-1)
        """
        learning = {
            "content": f"For {scam_type} scams, effective strategies include gathering "
                      f"{', '.join(intelligence.keys())}. "
                      f"This approach had {effectiveness*100:.0f}% effectiveness.",
            "metadata": {
                "type": "learning",
                "scam_type": scam_type,
                "timestamp": datetime.utcnow().isoformat(),
                "effectiveness": effectiveness
            }
        }
        
        self.add_document(learning["content"], learning["metadata"])


# Global RAG service instance
rag_service = RAGService()
