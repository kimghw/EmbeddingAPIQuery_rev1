"""
Document domain entities for Document Embedding & Retrieval System.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid


@dataclass
class Document:
    """Core document entity."""
    
    id: str
    title: str
    content: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Post-initialization processing."""
        if not self.id:
            self.id = str(uuid.uuid4())
        
        if not self.created_at:
            self.created_at = datetime.utcnow()
    
    @classmethod
    def create(
        cls,
        title: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        document_id: Optional[str] = None
    ) -> "Document":
        """Factory method to create a new document."""
        return cls(
            id=document_id or str(uuid.uuid4()),
            title=title,
            content=content,
            metadata=metadata or {},
            created_at=datetime.utcnow()
        )
    
    def update_content(self, content: str) -> None:
        """Update document content."""
        self.content = content
        self.updated_at = datetime.utcnow()
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to document."""
        self.metadata[key] = value
        self.updated_at = datetime.utcnow()
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value."""
        return self.metadata.get(key, default)


@dataclass
class DocumentChunk:
    """Document chunk entity for text splitting."""
    
    id: str
    document_id: str
    content: str
    chunk_index: int
    start_char: int
    end_char: int
    metadata: Dict[str, Any]
    created_at: datetime
    
    def __post_init__(self):
        """Post-initialization processing."""
        if not self.id:
            self.id = f"{self.document_id}_chunk_{self.chunk_index}"
        
        if not self.created_at:
            self.created_at = datetime.utcnow()
    
    @classmethod
    def create(
        cls,
        document_id: str,
        content: str,
        chunk_index: int,
        start_char: int,
        end_char: int,
        metadata: Optional[Dict[str, Any]] = None,
        chunk_id: Optional[str] = None
    ) -> "DocumentChunk":
        """Factory method to create a new document chunk."""
        return cls(
            id=chunk_id or f"{document_id}_chunk_{chunk_index}",
            document_id=document_id,
            content=content,
            chunk_index=chunk_index,
            start_char=start_char,
            end_char=end_char,
            metadata=metadata or {},
            created_at=datetime.utcnow()
        )
    
    def get_char_range(self) -> tuple[int, int]:
        """Get character range of this chunk."""
        return (self.start_char, self.end_char)
    
    def get_length(self) -> int:
        """Get content length."""
        return len(self.content)


@dataclass
class Embedding:
    """Embedding entity for vector representations."""
    
    id: str
    document_id: str
    chunk_id: Optional[str]
    vector: List[float]
    model: str
    dimension: int
    metadata: Dict[str, Any]
    created_at: datetime
    
    def __post_init__(self):
        """Post-initialization processing."""
        if not self.id:
            base_id = self.chunk_id or self.document_id
            self.id = f"{base_id}_embedding"
        
        if not self.created_at:
            self.created_at = datetime.utcnow()
        
        if not self.dimension:
            self.dimension = len(self.vector)
    
    @classmethod
    def create(
        cls,
        document_id: str,
        vector: List[float],
        model: str,
        chunk_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        embedding_id: Optional[str] = None
    ) -> "Embedding":
        """Factory method to create a new embedding."""
        base_id = chunk_id or document_id
        return cls(
            id=embedding_id or f"{base_id}_embedding",
            document_id=document_id,
            chunk_id=chunk_id,
            vector=vector,
            model=model,
            dimension=len(vector),
            metadata=metadata or {},
            created_at=datetime.utcnow()
        )
    
    def get_vector_norm(self) -> float:
        """Calculate L2 norm of the vector."""
        return sum(x * x for x in self.vector) ** 0.5
    
    def cosine_similarity(self, other: "Embedding") -> float:
        """Calculate cosine similarity with another embedding."""
        if len(self.vector) != len(other.vector):
            raise ValueError("Vectors must have the same dimension")
        
        dot_product = sum(a * b for a, b in zip(self.vector, other.vector))
        norm_a = self.get_vector_norm()
        norm_b = other.get_vector_norm()
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)


@dataclass
class RetrievalResult:
    """Retrieval result entity."""
    
    document_id: str
    chunk_id: Optional[str]
    content: str
    score: float
    metadata: Dict[str, Any]
    rank: int
    
    @classmethod
    def create(
        cls,
        document_id: str,
        content: str,
        score: float,
        rank: int,
        chunk_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "RetrievalResult":
        """Factory method to create a retrieval result."""
        return cls(
            document_id=document_id,
            chunk_id=chunk_id,
            content=content,
            score=score,
            metadata=metadata or {},
            rank=rank
        )
    
    def is_chunk_result(self) -> bool:
        """Check if this is a chunk-level result."""
        return self.chunk_id is not None
    
    def get_display_content(self, max_length: int = 200) -> str:
        """Get truncated content for display."""
        if len(self.content) <= max_length:
            return self.content
        return self.content[:max_length] + "..."


@dataclass
class Query:
    """Query entity for search operations."""
    
    id: str
    text: str
    metadata: Dict[str, Any]
    created_at: datetime
    
    def __post_init__(self):
        """Post-initialization processing."""
        if not self.id:
            self.id = str(uuid.uuid4())
        
        if not self.created_at:
            self.created_at = datetime.utcnow()
    
    @classmethod
    def create(
        cls,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        query_id: Optional[str] = None
    ) -> "Query":
        """Factory method to create a new query."""
        return cls(
            id=query_id or str(uuid.uuid4()),
            text=text,
            metadata=metadata or {},
            created_at=datetime.utcnow()
        )
    
    def get_word_count(self) -> int:
        """Get word count of the query."""
        return len(self.text.split())
    
    def is_empty(self) -> bool:
        """Check if query is empty."""
        return not self.text.strip()
