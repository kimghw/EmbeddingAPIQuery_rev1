"""
Embedding model port interface for Document Embedding & Retrieval System.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from core.entities.document import DocumentChunk, Embedding


class EmbeddingModelPort(ABC):
    """Port interface for embedding model operations."""
    
    @abstractmethod
    async def embed_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[float]:
        """Generate embedding for a single text."""
        pass
    
    @abstractmethod
    async def embed_texts(self, texts: List[str], metadata: Optional[Dict[str, Any]] = None) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        pass
    
    @abstractmethod
    async def embed_chunk(self, chunk: DocumentChunk) -> Embedding:
        """Generate embedding for a document chunk."""
        pass
    
    @abstractmethod
    async def embed_chunks(self, chunks: List[DocumentChunk]) -> List[Embedding]:
        """Generate embeddings for multiple document chunks."""
        pass
    
    @abstractmethod
    async def embed_query(self, query_text: str) -> List[float]:
        """Generate embedding for a query text."""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get the name of the embedding model."""
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """Get the dimension of the embedding vectors."""
        pass
    
    @abstractmethod
    def get_max_input_length(self) -> int:
        """Get the maximum input length for the model."""
        pass
    
    @abstractmethod
    async def get_model_info(self) -> Dict[str, Any]:
        """Get detailed information about the model."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the embedding model is available."""
        pass
