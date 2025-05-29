"""
Vector store port interface for Document Embedding & Retrieval System.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple
from core.entities.document import Embedding, RetrievalResult


class VectorStorePort(ABC):
    """Port interface for vector store operations."""
    
    @abstractmethod
    async def create_collection(self, collection_name: str, dimension: int, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Create a new collection in the vector store."""
        pass
    
    @abstractmethod
    async def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection from the vector store."""
        pass
    
    @abstractmethod
    async def collection_exists(self, collection_name: str) -> bool:
        """Check if a collection exists."""
        pass
    
    @abstractmethod
    async def add_embedding(self, embedding: Embedding, collection_name: str) -> bool:
        """Add a single embedding to the collection."""
        pass
    
    @abstractmethod
    async def add_embeddings(self, embeddings: List[Embedding], collection_name: str) -> bool:
        """Add multiple embeddings to the collection."""
        pass
    
    @abstractmethod
    async def update_embedding(self, embedding: Embedding, collection_name: str) -> bool:
        """Update an existing embedding in the collection."""
        pass
    
    @abstractmethod
    async def delete_embedding(self, embedding_id: str, collection_name: str) -> bool:
        """Delete an embedding from the collection."""
        pass
    
    @abstractmethod
    async def delete_embeddings_by_document(self, document_id: str, collection_name: str) -> bool:
        """Delete all embeddings for a specific document."""
        pass
    
    @abstractmethod
    async def search_similar(
        self, 
        query_vector: List[float], 
        collection_name: str, 
        top_k: int = 10,
        score_threshold: Optional[float] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResult]:
        """Search for similar vectors."""
        pass
    
    @abstractmethod
    async def get_embedding(self, embedding_id: str, collection_name: str) -> Optional[Embedding]:
        """Get a specific embedding by ID."""
        pass
    
    @abstractmethod
    async def get_embeddings_by_document(self, document_id: str, collection_name: str) -> List[Embedding]:
        """Get all embeddings for a specific document."""
        pass
    
    @abstractmethod
    async def count_embeddings(self, collection_name: str) -> int:
        """Count total number of embeddings in the collection."""
        pass
    
    @abstractmethod
    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get information about a collection."""
        pass
    
    @abstractmethod
    async def list_collections(self) -> List[str]:
        """List all available collections."""
        pass
    
    @abstractmethod
    def get_store_type(self) -> str:
        """Get the type of vector store."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the vector store is healthy and accessible."""
        pass
    
    @abstractmethod
    async def optimize_collection(self, collection_name: str) -> bool:
        """Optimize the collection for better performance."""
        pass
    
    @abstractmethod
    async def get_all_embeddings(self, collection_name: str) -> List[Embedding]:
        """Get all embeddings from a collection."""
        pass
