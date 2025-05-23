"""
Document loader port interface for Document Embedding & Retrieval System.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from core.entities.document import Document


class DocumentLoaderPort(ABC):
    """Port interface for document loading operations."""
    
    @abstractmethod
    async def load_from_file(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> Document:
        """Load a document from a file path."""
        pass
    
    @abstractmethod
    async def load_from_bytes(self, content: bytes, filename: str, metadata: Optional[Dict[str, Any]] = None) -> Document:
        """Load a document from bytes content."""
        pass
    
    @abstractmethod
    async def load_from_url(self, url: str, metadata: Optional[Dict[str, Any]] = None) -> Document:
        """Load a document from a URL."""
        pass
    
    @abstractmethod
    async def load_multiple_files(self, file_paths: List[str], metadata: Optional[Dict[str, Any]] = None) -> List[Document]:
        """Load multiple documents from file paths."""
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        pass
    
    @abstractmethod
    def is_format_supported(self, file_extension: str) -> bool:
        """Check if a file format is supported."""
        pass
