"""
FastAPI routes for email processing functionality.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

from adapters.email.json_email_loader import JsonEmailLoaderAdapter
from core.usecases.email_processing import EmailProcessingUseCase
from core.usecases.email_retrieval import EmailRetrievalUseCase
from adapters.vector_store.mock_vector_store import MockVectorStoreAdapter
from adapters.vector_store.simple_retriever import SimpleRetrieverAdapter
from config.adapter_factory import AdapterFactory, get_vector_store, get_embedding_model, get_config
from core.ports.vector_store import VectorStorePort
from core.ports.embedding_model import EmbeddingModelPort
from config.settings import ConfigPort


# Pydantic models for API
class EmailProcessingRequest(BaseModel):
    """Request model for email processing."""
    json_data: Dict[str, Any] = Field(..., description="Microsoft Graph API email JSON data")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    class Config:
        schema_extra = {
            "example": {
                "json_data": {
                    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users('user-id')/messages",
                    "value": [
                        {
                            "id": "email-id",
                            "subject": "Test Email",
                            "body": {"content": "Email content", "contentType": "text"},
                            "sender": {"emailAddress": {"name": "Sender", "address": "sender@example.com"}},
                            "createdDateTime": "2025-05-29T10:00:00Z",
                            "toRecipients": [{"emailAddress": {"name": "Recipient", "address": "recipient@example.com"}}],
                            "ccRecipients": [],
                            "bccRecipients": []
                        }
                    ]
                },
                "metadata": {
                    "source": "api",
                    "batch_id": "batch-123"
                }
            }
        }


class WebhookRequest(BaseModel):
    """Request model for webhook processing."""
    webhook_data: Dict[str, Any] = Field(..., description="Webhook payload data")
    callback_url: Optional[str] = Field(None, description="Optional callback URL for notifications")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    class Config:
        schema_extra = {
            "example": {
                "webhook_data": {
                    "id": "webhook-email-id",
                    "subject": "Webhook Email",
                    "body": {"content": "Webhook content", "contentType": "text"},
                    "sender": {"emailAddress": {"name": "Webhook Sender", "address": "webhook@example.com"}},
                    "createdDateTime": "2025-05-29T10:00:00Z"
                },
                "callback_url": "https://example.com/webhook-callback",
                "metadata": {
                    "webhook_source": "outlook",
                    "real_time": True
                }
            }
        }


class EmailProcessingResponse(BaseModel):
    """Response model for email processing."""
    success: bool
    processed_count: int
    embedded_count: int
    collection_name: str
    message: Optional[str] = None
    error: Optional[str] = None
    statistics: Optional[Dict[str, Any]] = None
    emails: Optional[List[Dict[str, Any]]] = None
    processing_time: Optional[float] = None


class EmailStatsResponse(BaseModel):
    """Response model for email statistics."""
    success: bool
    collection_exists: bool
    total_embeddings: int
    estimated_email_count: int
    collection_name: str
    embedding_model: str
    vector_dimension: int
    loader_type: str
    error: Optional[str] = None


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


class MockEmbeddingModel:
    """Mock embedding model for API."""
    
    def __init__(self):
        self.model_name = "mock-embedding-model"
        self.dimension = 1536
        self.max_input_length = 8191
    
    async def embed_texts(self, texts):
        import random
        embeddings = []
        for text in texts:
            random.seed(hash(text) % 2**32)
            embedding = [random.uniform(-1, 1) for _ in range(self.dimension)]
            embeddings.append(embedding)
        return embeddings
    
    def get_model_name(self) -> str:
        return self.model_name
    
    def get_dimension(self) -> int:
        return self.dimension
    
    def get_max_input_length(self) -> int:
        return self.max_input_length


class MockConfig:
    """Mock configuration for API."""
    
    def get_openai_api_key(self) -> str:
        return "mock-api-key"
    
    def get_qdrant_url(self) -> str:
        return "http://localhost:6333"
    
    def get_qdrant_api_key(self) -> str:
        return "mock-qdrant-key"


# Dependency injection
async def get_email_processor(
    vector_store: VectorStorePort = Depends(get_vector_store),
    embedding_model: EmbeddingModelPort = Depends(get_embedding_model),
    config: ConfigPort = Depends(get_config)
) -> EmailProcessingUseCase:
    """Get email processing use case with dependencies."""
    email_loader = JsonEmailLoaderAdapter()
    
    return EmailProcessingUseCase(
        email_loader=email_loader,
        embedding_model=embedding_model,
        vector_store=vector_store,
        config=config
    )


async def get_email_retriever() -> EmailRetrievalUseCase:
    """Get email retrieval use case with dependencies."""
    embedding_model = MockEmbeddingModel()
    vector_store = MockVectorStoreAdapter()
    config = MockConfig()
    retriever = SimpleRetrieverAdapter(vector_store=vector_store, embedding_model=embedding_model)
    
    return EmailRetrievalUseCase(
        retriever=retriever,
        embedding_model=embedding_model,
        vector_store=vector_store,
        config=config
    )


# Create router
router = APIRouter(prefix="/emails", tags=["emails"])


@router.post("/process", response_model=EmailProcessingResponse)
async def process_emails(
    request: EmailProcessingRequest,
    background_tasks: BackgroundTasks,
    email_processor: EmailProcessingUseCase = Depends(get_email_processor)
):
    """
    Process emails from JSON data.
    
    This endpoint accepts Microsoft Graph API email JSON format and processes
    the emails by creating embeddings and storing them in the vector database.
    """
    try:
        start_time = datetime.utcnow()
        
        # Add API metadata
        api_metadata = request.metadata or {}
        api_metadata.update({
            "source": "api",
            "endpoint": "/emails/process",
            "timestamp": start_time.isoformat()
        })
        
        # Process emails
        result = await email_processor.process_emails_from_json(
            request.json_data, 
            api_metadata
        )
        
        # Calculate processing time
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        # Prepare response
        response_data = {
            "success": result["success"],
            "processed_count": result["processed_count"],
            "embedded_count": result["embedded_count"],
            "collection_name": result["collection_name"],
            "processing_time": processing_time
        }
        
        if result["success"]:
            response_data.update({
                "message": f"Successfully processed {result['processed_count']} emails",
                "statistics": result.get("statistics"),
                "emails": result.get("emails")
            })
        else:
            response_data["error"] = result.get("error", "Unknown error")
        
        return EmailProcessingResponse(**response_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/webhook", response_model=EmailProcessingResponse)
async def process_webhook(
    request: WebhookRequest,
    background_tasks: BackgroundTasks,
    email_processor: EmailProcessingUseCase = Depends(get_email_processor)
):
    """
    Process emails from webhook payload.
    
    This endpoint handles real-time webhook notifications from email services
    and processes the incoming email data.
    """
    try:
        start_time = datetime.utcnow()
        
        # Add webhook metadata
        webhook_metadata = request.metadata or {}
        webhook_metadata.update({
            "source": "webhook",
            "endpoint": "/emails/webhook",
            "timestamp": start_time.isoformat(),
            "callback_url": request.callback_url
        })
        
        # Process webhook
        result = await email_processor.process_emails_from_webhook(
            request.webhook_data,
            webhook_metadata
        )
        
        # Calculate processing time
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        # Prepare response
        response_data = {
            "success": result["success"],
            "processed_count": result["processed_count"],
            "embedded_count": result["embedded_count"],
            "collection_name": result["collection_name"],
            "processing_time": processing_time
        }
        
        if result["success"]:
            response_data.update({
                "message": f"Successfully processed {result['processed_count']} emails from webhook",
                "statistics": result.get("statistics"),
                "emails": result.get("emails")
            })
            
            # Schedule callback if provided
            if request.callback_url:
                background_tasks.add_task(
                    send_webhook_callback,
                    request.callback_url,
                    result
                )
        else:
            response_data["error"] = result.get("error", "Unknown error")
        
        return EmailProcessingResponse(**response_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/stats", response_model=EmailStatsResponse)
async def get_email_stats(
    email_processor: EmailProcessingUseCase = Depends(get_email_processor)
):
    """
    Get email processing statistics.
    
    Returns information about the email collection, including total embeddings,
    estimated email count, and collection metadata.
    """
    try:
        result = await email_processor.get_processing_stats()
        
        response_data = {
            "success": result["success"],
            "collection_exists": result.get("collection_exists", False),
            "total_embeddings": result.get("total_embeddings", 0),
            "estimated_email_count": result.get("estimated_email_count", 0),
            "collection_name": result.get("collection_name", "emails"),
            "embedding_model": result.get("embedding_model", "unknown"),
            "vector_dimension": result.get("vector_dimension", 0),
            "loader_type": result.get("loader_type", "unknown")
        }
        
        if not result["success"]:
            response_data["error"] = result.get("error", "Unknown error")
        
        return EmailStatsResponse(**response_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{email_id}")
async def get_email_info(
    email_id: str,
    email_processor: EmailProcessingUseCase = Depends(get_email_processor)
):
    """
    Get information about a specific email's embeddings.
    
    Returns details about the embeddings created for a specific email,
    including embedding types, metadata, and content previews.
    """
    try:
        result = await email_processor.get_email_info(email_id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=404,
                detail=f"Email not found: {result.get('error', 'Unknown error')}"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/{email_id}")
async def delete_email(
    email_id: str,
    email_processor: EmailProcessingUseCase = Depends(get_email_processor)
):
    """
    Delete an email and all its embeddings.
    
    Removes all embeddings associated with the specified email ID
    from the vector database.
    """
    try:
        result = await email_processor.delete_email(email_id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=404,
                detail=f"Failed to delete email: {result.get('error', 'Unknown error')}"
            )
        
        return {
            "success": True,
            "message": f"Email {email_id} deleted successfully",
            "email_id": email_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/validate")
async def validate_email_json(request: EmailProcessingRequest):
    """
    Validate email JSON structure without processing.
    
    Checks if the provided JSON data has the correct structure
    for email processing without actually processing the emails.
    """
    try:
        email_loader = JsonEmailLoaderAdapter()
        
        # Validate structure
        is_valid = email_loader.validate_json_structure(request.json_data)
        
        if not is_valid:
            return {
                "valid": False,
                "error": "Invalid JSON structure for email processing"
            }
        
        # Get statistics
        stats = email_loader.get_statistics(request.json_data)
        
        return {
            "valid": True,
            "message": "JSON structure is valid for email processing",
            "statistics": stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Validation error: {str(e)}"
        )


# Background task for webhook callbacks
async def send_webhook_callback(callback_url: str, data: Dict[str, Any]):
    """Send callback notification to external URL."""
    try:
        import aiohttp
        
        callback_data = {
            "success": data["success"],
            "processed_count": data["processed_count"],
            "embedded_count": data["embedded_count"],
            "timestamp": datetime.utcnow().isoformat(),
            "collection_name": data["collection_name"]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                callback_url,
                json=callback_data,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    print(f"✅ Webhook callback sent successfully to {callback_url}")
                else:
                    print(f"❌ Webhook callback failed: {response.status}")
                    
    except Exception as e:
        print(f"❌ Error sending webhook callback: {e}")


# Email chat response model
class EmailChatResponse(BaseModel):
    """Response model for email chat."""
    response: str
    context_emails: List[Dict[str, Any]]
    query: str
    total_found: int
    error: Optional[str] = None


@router.post("/chat", response_model=EmailChatResponse)
async def email_chat(
    request: Dict[str, Any],
    email_retriever: EmailRetrievalUseCase = Depends(get_email_retriever)
):
    """
    Chat with email context.
    
    Process natural language queries about emails and return
    contextual responses based on email content.
    """
    try:
        message = request.get("message", "")
        context_emails = request.get("context_emails", 5)
        include_metadata = request.get("include_metadata", True)
        
        if not message:
            raise HTTPException(
                status_code=400,
                detail="Message is required"
            )
        
        # Search for relevant emails
        search_result = await email_retriever.search_emails(
            query_text=message, 
            top_k=context_emails,
            search_type="both"
        )
        
        if not search_result["success"]:
            return {
                "response": "Sorry, I couldn't find any relevant emails.",
                "context_emails": [],
                "query": message,
                "total_found": 0,
                "error": search_result.get("error")
            }
        
        # Generate response based on found emails
        emails = search_result.get("results", [])
        
        if not emails:
            response_text = f"I couldn't find any emails related to '{message}'."
        else:
            response_text = f"Based on {len(emails)} relevant emails:\n\n"
            
            for i, email in enumerate(emails[:3], 1):
                response_text += f"{i}. **{email.get('subject', 'No Subject')}**\n"
                response_text += f"   From: {email.get('sender_name', 'Unknown')}\n"
                response_text += f"   Preview: {email.get('content_preview', '')[:100]}...\n\n"
        
        return {
            "response": response_text,
            "context_emails": emails if include_metadata else [],
            "query": message,
            "total_found": len(emails)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat processing failed: {str(e)}"
        )


# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint for email processing service."""
    try:
        # Test basic components
        email_loader = JsonEmailLoaderAdapter()
        embedding_model = MockEmbeddingModel()
        vector_store = MockVectorStoreAdapter()
        
        # Basic functionality test
        test_data = {
            "@odata.context": "test",
            "value": []
        }
        
        is_valid = email_loader.validate_json_structure(test_data)
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "email_loader": "ok",
                "embedding_model": "ok",
                "vector_store": "ok"
            },
            "validation_test": "passed" if is_valid else "failed",
            "version": "1.0.0"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )
