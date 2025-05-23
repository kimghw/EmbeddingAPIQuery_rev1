"""
Retriever port interface for Document Embedding & Retrieval System.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from core.entities.document import Query, RetrievalResult


class RetrieverPort(ABC):
    """Port interface for document retrieval operations."""
    
    @abstractmethod
    async def retrieve(
        self, 
        query: Query, 
        top_k: int = 10,
        score_threshold: Optional[float] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResult]:
        """Retrieve relevant documents for a query."""
        pass
    
    @abstractmethod
    async def retrieve_by_text(
        self, 
        query_text: str, 
        top_k: int = 10,
        score_threshold: Optional[float] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResult]:
        """Retrieve relevant documents for a text query."""
        pass
    
    @abstractmethod
    async def retrieve_similar_documents(
        self, 
        document_id: str, 
        top_k: int = 10,
        score_threshold: Optional[float] = None
    ) -> List[RetrievalResult]:
        """Retrieve documents similar to a given document."""
        pass
    
    @abstractmethod
    async def retrieve_with_reranking(
        self, 
        query: Query, 
        top_k: int = 10,
        rerank_top_k: int = 100,
        score_threshold: Optional[float] = None
    ) -> List[RetrievalResult]:
        """Retrieve with reranking for better results."""
        pass
    
    @abstractmethod
    def get_retriever_type(self) -> str:
        """Get the type of retriever."""
        pass
    
    @abstractmethod
    async def get_retriever_info(self) -> Dict[str, Any]:
        """Get information about the retriever configuration."""
        pass
    
    @abstractmethod
    def set_collection_name(self, collection_name: str) -> None:
        """Set the collection name for retrieval."""
        pass
    
    @abstractmethod
    def get_collection_name(self) -> str:
        """Get the current collection name."""
        pass
