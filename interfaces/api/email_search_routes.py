"""
FastAPI routes for email search functionality.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

from core.usecases.email_retrieval import EmailRetrievalUseCase
from config.adapter_factory import get_vector_store, get_embedding_model, get_retriever


class EmailSearchRequest(BaseModel):
    """Request model for email search."""
    query: str = Field(..., description="Search query text")
    top_k: int = Field(5, description="Number of results to return", ge=1, le=50)
    search_type: str = Field("both", description="Search type: subject, body, or both")
    filters: Optional[Dict[str, Any]] = Field(None, description="Optional search filters")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "maritime safety regulations",
                "top_k": 5,
                "search_type": "both",
                "filters": {
                    "correspondence_thread": "PL25008aKRd"
                }
            }
        }


class EmailSearchResponse(BaseModel):
    """Response model for email search."""
    success: bool
    query: str
    search_type: str
    total_results: int
    collection_name: str
    results: List[Dict[str, Any]]
    filters_applied: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None


# Dependency injection
async def get_email_retriever() -> EmailRetrievalUseCase:
    """Get email retrieval use case with dependencies."""
    from config.settings import config
    
    embedding_model = get_embedding_model()
    vector_store = get_vector_store()
    retriever = get_retriever()
    
    return EmailRetrievalUseCase(
        retriever=retriever,
        embedding_model=embedding_model,
        vector_store=vector_store,
        config=config
    )


# Create router
search_router = APIRouter(prefix="/emails", tags=["email-search"])


@search_router.post("/search", response_model=EmailSearchResponse)
async def search_emails(
    request: EmailSearchRequest,
    email_retriever: EmailRetrievalUseCase = Depends(get_email_retriever)
):
    """Search emails using text query.
    
    This endpoint allows searching through processed emails using semantic search.
    You can search in subjects, bodies, or both, and apply additional filters.
    """
    try:
        start_time = datetime.utcnow()
        
        # Perform search
        result = await email_retriever.search_emails(
            query_text=request.query,
            top_k=request.top_k,
            search_type=request.search_type,
            filters=request.filters
        )
        
        # Calculate processing time
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        # Prepare response
        response_data = {
            "success": result["success"],
            "query": result["query"],
            "search_type": result["search_type"],
            "total_results": result["total_results"],
            "collection_name": result["collection_name"],
            "results": result["results"],
            "processing_time": processing_time
        }
        
        if result["success"]:
            response_data["filters_applied"] = result.get("filters_applied")
        else:
            response_data["error"] = result.get("error", "Unknown error")
        
        return EmailSearchResponse(**response_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@search_router.get("/search/thread/{thread_id}")
async def search_by_thread(
    thread_id: str,
    top_k: int = 10,
    email_retriever: EmailRetrievalUseCase = Depends(get_email_retriever)
):
    """Search emails by correspondence thread.
    
    Returns all emails belonging to a specific correspondence thread.
    """
    try:
        result = await email_retriever.search_by_correspondence_thread(
            thread_id=thread_id,
            top_k=top_k
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=404,
                detail=f"Thread not found or error: {result.get('error', 'Unknown error')}"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@search_router.get("/search/sender/{sender_address}")
async def search_by_sender(
    sender_address: str,
    top_k: int = 10,
    email_retriever: EmailRetrievalUseCase = Depends(get_email_retriever)
):
    """Search emails by sender address.
    
    Returns all emails from a specific sender.
    """
    try:
        result = await email_retriever.search_by_sender(
            sender_address=sender_address,
            top_k=top_k
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=404,
                detail=f"Sender not found or error: {result.get('error', 'Unknown error')}"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@search_router.get("/search/similar/{email_id}")
async def get_similar_emails(
    email_id: str,
    top_k: int = 5,
    email_retriever: EmailRetrievalUseCase = Depends(get_email_retriever)
):
    """Find emails similar to a given email.
    
    Returns emails that are semantically similar to the specified email.
    """
    try:
        result = await email_retriever.get_similar_emails(
            email_id=email_id,
            top_k=top_k
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=404,
                detail=f"Email not found or error: {result.get('error', 'Unknown error')}"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@search_router.get("/search/date-range")
async def search_by_date_range(
    start_date: str,
    end_date: str,
    query: Optional[str] = None,
    top_k: int = 10,
    email_retriever: EmailRetrievalUseCase = Depends(get_email_retriever)
):
    """Search emails by date range.
    
    Returns emails within the specified date range, optionally filtered by query text.
    Date format: YYYY-MM-DD
    """
    try:
        result = await email_retriever.search_by_date_range(
            start_date=start_date,
            end_date=end_date,
            query_text=query,
            top_k=top_k
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"Date range search error: {result.get('error', 'Unknown error')}"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@search_router.get("/search/advanced")
async def advanced_search(
    query: str,
    top_k: int = 10,
    search_type: str = "both",
    sender: Optional[str] = None,
    thread: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    has_attachments: Optional[bool] = None,
    importance: Optional[str] = None,
    email_retriever: EmailRetrievalUseCase = Depends(get_email_retriever)
):
    """Advanced email search with multiple filters.
    
    Combines text search with various filters for more precise results.
    """
    try:
        # Build filters dictionary
        filters = {}
        if sender:
            filters["sender_address"] = sender
        if thread:
            filters["correspondence_thread"] = thread
        if start_date:
            filters["start_date"] = start_date
        if end_date:
            filters["end_date"] = end_date
        if has_attachments is not None:
            filters["has_attachments"] = has_attachments
        if importance:
            filters["importance"] = importance
        
        result = await email_retriever.search_emails(
            query_text=query,
            top_k=top_k,
            search_type=search_type,
            filters=filters if filters else None
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"Advanced search error: {result.get('error', 'Unknown error')}"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
