"""
Document-related Pydantic schemas for API requests and responses.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class DocumentUploadRequest(BaseModel):
    """Request schema for document upload."""
    title: Optional[str] = Field(None, description="Document title")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class DocumentUploadResponse(BaseModel):
    """Response schema for document upload."""
    document_id: str = Field(..., description="Unique document identifier")
    title: str = Field(..., description="Document title")
    status: str = Field(..., description="Processing status")
    chunks_count: int = Field(..., description="Number of chunks created")
    created_at: datetime = Field(..., description="Creation timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")


class DocumentChunkResponse(BaseModel):
    """Response schema for document chunk."""
    chunk_id: str = Field(..., description="Unique chunk identifier")
    document_id: str = Field(..., description="Parent document identifier")
    content: str = Field(..., description="Chunk content")
    chunk_index: int = Field(..., description="Chunk position in document")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Chunk metadata")


class DocumentListResponse(BaseModel):
    """Response schema for document list."""
    documents: List[DocumentUploadResponse] = Field(..., description="List of documents")
    total: int = Field(..., description="Total number of documents")


class DocumentProcessingStatus(BaseModel):
    """Response schema for document processing status."""
    document_id: str = Field(..., description="Document identifier")
    status: str = Field(..., description="Processing status")
    progress: float = Field(..., description="Processing progress (0.0 to 1.0)")
    message: Optional[str] = Field(None, description="Status message")
    chunks_processed: int = Field(0, description="Number of chunks processed")
    total_chunks: int = Field(0, description="Total number of chunks")


class DocumentSearchRequest(BaseModel):
    """Request schema for document search."""
    query: str = Field(..., description="Search query")
    limit: int = Field(default=5, ge=1, le=50, description="Maximum number of results")
    threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Similarity threshold")
    document_ids: Optional[List[str]] = Field(None, description="Filter by specific document IDs")


class DocumentSearchResult(BaseModel):
    """Response schema for search result item."""
    document_id: str = Field(..., description="Document identifier")
    chunk_id: str = Field(..., description="Chunk identifier")
    content: str = Field(..., description="Chunk content")
    score: float = Field(..., description="Similarity score")
    rank: int = Field(..., description="Result rank")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Chunk metadata")
    is_chunk_result: bool = Field(True, description="Whether this is a chunk result")


class DocumentSearchResponse(BaseModel):
    """Response schema for document search."""
    success: bool = Field(True, description="Search success status")
    query_id: str = Field(..., description="Unique query identifier")
    query_text: str = Field(..., description="Original search query")
    results_count: int = Field(..., description="Number of results returned")
    results: List[DocumentSearchResult] = Field(..., description="Search results")
    retriever_type: str = Field(..., description="Type of retriever used")
    collection_name: str = Field(..., description="Collection name searched")
