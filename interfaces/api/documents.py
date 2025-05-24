"""
Document processing API endpoints.
"""

import asyncio
import time
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse

from core.usecases.document_processing import DocumentProcessingUseCase
from core.usecases.document_retrieval import DocumentRetrievalUseCase
from schemas.document import (
    DocumentUploadRequest,
    DocumentUploadResponse,
    DocumentListResponse,
    DocumentProcessingStatus,
    DocumentSearchRequest,
    DocumentSearchResponse,
)
from config.settings import ConfigPort, config
from adapters.pdf.pdf_loader import PdfLoaderAdapter
from adapters.embedding.text_chunker import RecursiveTextChunkerAdapter
from adapters.embedding.openai_embedding import OpenAIEmbeddingAdapter
from adapters.vector_store.qdrant_vector_store import QdrantVectorStoreAdapter
from adapters.vector_store.simple_retriever import SimpleRetrieverAdapter

router = APIRouter(prefix="/documents", tags=["documents"])


def get_document_processing_usecase(config: ConfigPort = Depends(lambda: config)) -> DocumentProcessingUseCase:
    """Dependency injection for DocumentProcessingUseCase."""
    document_loader = PdfLoaderAdapter()
    text_chunker = RecursiveTextChunkerAdapter(
        chunk_size=config.get_chunk_size(),
        chunk_overlap=config.get_chunk_overlap()
    )
    embedding_model = OpenAIEmbeddingAdapter(config)
    vector_store = QdrantVectorStoreAdapter()
    
    return DocumentProcessingUseCase(
        document_loader=document_loader,
        text_chunker=text_chunker,
        embedding_model=embedding_model,
        vector_store=vector_store,
        config=config
    )


def get_document_retrieval_usecase(config: ConfigPort = Depends(lambda: config)) -> DocumentRetrievalUseCase:
    """Dependency injection for DocumentRetrievalUseCase."""
    embedding_model = OpenAIEmbeddingAdapter(config)
    vector_store = QdrantVectorStoreAdapter()
    
    return DocumentRetrievalUseCase(
        embedding_model=embedding_model,
        vector_store=vector_store
    )


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(None),
    usecase: DocumentProcessingUseCase = Depends(get_document_processing_usecase)
):
    """
    Upload and process a document.
    
    - **file**: PDF file to upload
    - **title**: Optional document title (defaults to filename)
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Read file content
        file_content = await file.read()
        
        # Use filename as title if not provided
        document_title = title or file.filename
        
        # Process document
        result = await usecase.process_document(
            file_content=file_content,
            filename=file.filename,
            title=document_title,
            metadata={"original_filename": file.filename, "file_size": len(file_content)}
        )
        
        return DocumentUploadResponse(
            document_id=result.document_id,
            title=result.title,
            status="completed",
            chunks_count=len(result.chunks),
            created_at=result.created_at,
            metadata=result.metadata
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    usecase: DocumentProcessingUseCase = Depends(get_document_processing_usecase)
):
    """
    List all processed documents.
    """
    try:
        documents = await usecase.list_documents()
        
        document_responses = [
            DocumentUploadResponse(
                document_id=doc.document_id,
                title=doc.title,
                status="completed",
                chunks_count=len(doc.chunks) if hasattr(doc, 'chunks') else 0,
                created_at=doc.created_at,
                metadata=doc.metadata
            )
            for doc in documents
        ]
        
        return DocumentListResponse(
            documents=document_responses,
            total=len(document_responses)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@router.get("/{document_id}/status", response_model=DocumentProcessingStatus)
async def get_document_status(
    document_id: str,
    usecase: DocumentProcessingUseCase = Depends(get_document_processing_usecase)
):
    """
    Get document processing status.
    """
    try:
        document = await usecase.get_document(document_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return DocumentProcessingStatus(
            document_id=document.document_id,
            status="completed",
            progress=1.0,
            message="Document processing completed",
            chunks_processed=len(document.chunks) if hasattr(document, 'chunks') else 0,
            total_chunks=len(document.chunks) if hasattr(document, 'chunks') else 0
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get document status: {str(e)}")


@router.post("/search")
async def search_documents(
    request: DocumentSearchRequest,
    config: ConfigPort = Depends(lambda: config)
):
    """
    Search documents using semantic similarity.
    
    - **query**: Search query text
    - **limit**: Maximum number of results (1-50)
    - **threshold**: Similarity threshold (0.0-1.0)
    - **document_ids**: Optional filter by specific document IDs
    """
    try:
        start_time = time.time()
        
        # Create components
        embedding_model = OpenAIEmbeddingAdapter(config)
        vector_store = QdrantVectorStoreAdapter()
        retriever = SimpleRetrieverAdapter(vector_store, embedding_model)
        
        # Set collection name
        retriever.set_collection_name(config.get_collection_name())
        
        # Create query entity
        from core.entities.document import Query
        query = Query.create(request.query)
        
        # Perform search
        results = await retriever.retrieve(
            query=query,
            top_k=request.limit,
            score_threshold=request.threshold
        )
        
        processing_time = time.time() - start_time
        
        # Convert results to response format
        search_results = [
            {
                "chunk_id": result.chunk_id,
                "document_id": result.document_id,
                "document_title": "Unknown",  # We don't have document title in current system
                "content": result.content,
                "similarity_score": result.score,
                "chunk_index": result.metadata.get("chunk_index", 0),
                "metadata": result.metadata
            }
            for result in results
        ]
        
        return {
            "query": request.query,
            "results": search_results,
            "total_results": len(search_results),
            "processing_time": processing_time
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    usecase: DocumentProcessingUseCase = Depends(get_document_processing_usecase)
):
    """
    Delete a document and its associated chunks.
    """
    try:
        success = await usecase.delete_document(document_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {"message": f"Document {document_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")
