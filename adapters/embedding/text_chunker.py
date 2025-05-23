"""
Text chunker adapter implementation.
"""

from typing import List, Optional, Dict, Any
import asyncio
from core.entities.document import Document, DocumentChunk
from core.ports.text_chunker import TextChunkerPort


class RecursiveTextChunkerAdapter(TextChunkerPort):
    """Recursive character text splitter adapter."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200, separators: Optional[List[str]] = None):
        """
        Initialize text chunker.
        
        Args:
            chunk_size: Maximum size of each chunk
            chunk_overlap: Number of characters to overlap between chunks
            separators: List of separators to use for splitting
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", " ", ""]
    
    async def chunk_document(self, document: Document) -> List[DocumentChunk]:
        """Split a document into chunks."""
        return await self.chunk_text(document.content, document.id, document.metadata)
    
    async def chunk_text(self, text: str, document_id: str, metadata: Optional[Dict[str, Any]] = None) -> List[DocumentChunk]:
        """Split text into chunks."""
        # Run chunking in thread pool to avoid blocking
        chunks_data = await asyncio.get_event_loop().run_in_executor(
            None, self._split_text, text
        )
        
        chunks = []
        for i, (chunk_text, start_char, end_char) in enumerate(chunks_data):
            chunk_metadata = metadata.copy() if metadata else {}
            chunk_metadata.update({
                "chunk_method": "recursive_character",
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap
            })
            
            chunk = DocumentChunk.create(
                document_id=document_id,
                content=chunk_text,
                chunk_index=i,
                start_char=start_char,
                end_char=end_char,
                metadata=chunk_metadata
            )
            chunks.append(chunk)
        
        return chunks
    
    async def chunk_multiple_documents(self, documents: List[Document]) -> Dict[str, List[DocumentChunk]]:
        """Split multiple documents into chunks."""
        result = {}
        
        for document in documents:
            chunks = await self.chunk_document(document)
            result[document.id] = chunks
        
        return result
    
    def get_chunk_size(self) -> int:
        """Get the configured chunk size."""
        return self.chunk_size
    
    def get_chunk_overlap(self) -> int:
        """Get the configured chunk overlap."""
        return self.chunk_overlap
    
    def set_chunk_size(self, size: int) -> None:
        """Set the chunk size."""
        self.chunk_size = size
    
    def set_chunk_overlap(self, overlap: int) -> None:
        """Set the chunk overlap."""
        self.chunk_overlap = overlap
    
    def get_chunker_type(self) -> str:
        """Get the type of chunker being used."""
        return "recursive_character"
    
    def _split_text(self, text: str) -> List[tuple[str, int, int]]:
        """Split text into chunks (synchronous)."""
        if not text:
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Calculate end position
            end = start + self.chunk_size
            
            if end >= len(text):
                # Last chunk
                chunk_text = text[start:]
                chunks.append((chunk_text, start, len(text)))
                break
            
            # Find the best split point
            split_point = self._find_split_point(text, start, end)
            
            chunk_text = text[start:split_point]
            chunks.append((chunk_text, start, split_point))
            
            # Move start position with overlap
            start = split_point - self.chunk_overlap
            if start < 0:
                start = 0
        
        return chunks
    
    def _find_split_point(self, text: str, start: int, end: int) -> int:
        """Find the best point to split the text."""
        # Try to split at separators in order of preference
        for separator in self.separators:
            if not separator:
                # Empty separator means split at any character
                return end
            
            # Look for separator near the end position
            search_start = max(start, end - len(separator) * 10)
            last_sep_pos = text.rfind(separator, search_start, end)
            
            if last_sep_pos != -1 and last_sep_pos > start:
                return last_sep_pos + len(separator)
        
        # If no separator found, split at the end position
        return end


class SemanticTextChunkerAdapter(TextChunkerPort):
    """Semantic text chunker adapter (simplified implementation)."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize semantic text chunker.
        
        Args:
            chunk_size: Maximum size of each chunk
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    async def chunk_document(self, document: Document) -> List[DocumentChunk]:
        """Split a document into chunks."""
        return await self.chunk_text(document.content, document.id, document.metadata)
    
    async def chunk_text(self, text: str, document_id: str, metadata: Optional[Dict[str, Any]] = None) -> List[DocumentChunk]:
        """Split text into chunks using semantic boundaries."""
        # Run chunking in thread pool to avoid blocking
        chunks_data = await asyncio.get_event_loop().run_in_executor(
            None, self._semantic_split_text, text
        )
        
        chunks = []
        for i, (chunk_text, start_char, end_char) in enumerate(chunks_data):
            chunk_metadata = metadata.copy() if metadata else {}
            chunk_metadata.update({
                "chunk_method": "semantic",
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap
            })
            
            chunk = DocumentChunk.create(
                document_id=document_id,
                content=chunk_text,
                chunk_index=i,
                start_char=start_char,
                end_char=end_char,
                metadata=chunk_metadata
            )
            chunks.append(chunk)
        
        return chunks
    
    async def chunk_multiple_documents(self, documents: List[Document]) -> Dict[str, List[DocumentChunk]]:
        """Split multiple documents into chunks."""
        result = {}
        
        for document in documents:
            chunks = await self.chunk_document(document)
            result[document.id] = chunks
        
        return result
    
    def get_chunk_size(self) -> int:
        """Get the configured chunk size."""
        return self.chunk_size
    
    def get_chunk_overlap(self) -> int:
        """Get the configured chunk overlap."""
        return self.chunk_overlap
    
    def set_chunk_size(self, size: int) -> None:
        """Set the chunk size."""
        self.chunk_size = size
    
    def set_chunk_overlap(self, overlap: int) -> None:
        """Set the chunk overlap."""
        self.chunk_overlap = overlap
    
    def get_chunker_type(self) -> str:
        """Get the type of chunker being used."""
        return "semantic"
    
    def _semantic_split_text(self, text: str) -> List[tuple[str, int, int]]:
        """Split text into chunks using semantic boundaries (simplified)."""
        if not text:
            return []
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        current_start = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # If adding this paragraph would exceed chunk size, finalize current chunk
            if current_chunk and len(current_chunk) + len(paragraph) + 2 > self.chunk_size:
                # Finalize current chunk
                end_pos = current_start + len(current_chunk)
                chunks.append((current_chunk.strip(), current_start, end_pos))
                
                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk)
                current_chunk = overlap_text + paragraph
                current_start = end_pos - len(overlap_text)
            else:
                # Add paragraph to current chunk
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
                    current_start = text.find(paragraph)
        
        # Add final chunk
        if current_chunk:
            end_pos = current_start + len(current_chunk)
            chunks.append((current_chunk.strip(), current_start, end_pos))
        
        return chunks
    
    def _get_overlap_text(self, text: str) -> str:
        """Get overlap text from the end of current chunk."""
        if len(text) <= self.chunk_overlap:
            return text
        
        # Try to find sentence boundary for overlap
        overlap_text = text[-self.chunk_overlap:]
        sentence_end = overlap_text.find('. ')
        
        if sentence_end != -1:
            return overlap_text[sentence_end + 2:]
        
        return overlap_text
