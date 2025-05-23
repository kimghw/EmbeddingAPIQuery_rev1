"""
Text chunker port interface for Document Embedding & Retrieval System.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from core.entities.document import Document, DocumentChunk


class TextChunkerPort(ABC):
    """Port interface for text chunking operations."""
    
    @abstractmethod
    async def chunk_document(self, document: Document) -> List[DocumentChunk]:
        """Split a document into chunks."""
        pass
    
    @abstractmethod
    async def chunk_text(self, text: str, document_id: str, metadata: Optional[Dict[str, Any]] = None) -> List[DocumentChunk]:
        """Split text into chunks."""
        pass
    
    @abstractmethod
    async def chunk_multiple_documents(self, documents: List[Document]) -> Dict[str, List[DocumentChunk]]:
        """Split multiple documents into chunks."""
        pass
    
    @abstractmethod
    def get_chunk_size(self) -> int:
        """Get the configured chunk size."""
        pass
    
    @abstractmethod
    def get_chunk_overlap(self) -> int:
        """Get the configured chunk overlap."""
        pass
    
    @abstractmethod
    def set_chunk_size(self, size: int) -> None:
        """Set the chunk size."""
        pass
    
    @abstractmethod
    def set_chunk_overlap(self, overlap: int) -> None:
        """Set the chunk overlap."""
        pass
    
    @abstractmethod
    def get_chunker_type(self) -> str:
        """Get the type of chunker being used."""
        pass
