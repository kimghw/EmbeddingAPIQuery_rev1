"""
Email list and detail API routes.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from adapters.vector_store.mock_vector_store import MockVectorStoreAdapter
from config.adapter_factory import get_vector_store
from core.ports.vector_store import VectorStorePort

router = APIRouter(prefix="/emails", tags=["email-list"])


@router.get("/list")
async def get_email_list(
    limit: int = 50,
    offset: int = 0,
    vector_store: VectorStorePort = Depends(get_vector_store)
):
    """Get list of emails with basic information."""
    try:
        collection_name = "emails"
        
        # Check if collection exists
        if not await vector_store.collection_exists(collection_name):
            return {
                "success": True,
                "emails": [],
                "total": 0,
                "message": "No emails found - collection does not exist"
            }
        
        # Get all embeddings from email collection with proper limit
        all_embeddings = await vector_store.get_all_embeddings(collection_name, limit=10000)
        
        # Filter for subject embeddings only to avoid duplicates
        email_data = []
        seen_email_ids = set()
        
        for embedding in all_embeddings:
            metadata = embedding.metadata
            email_id = metadata.get('email_id')
            
            # Check if this is a subject embedding by ID suffix
            is_subject = embedding.id.endswith('_subject')
            
            # Only process subject embeddings to avoid duplicates
            if is_subject and email_id not in seen_email_ids:
                seen_email_ids.add(email_id)
                
                email_info = {
                    "id": email_id,
                    "subject": metadata.get('content', 'No Subject'),
                    "sender_name": metadata.get('sender_name', 'Unknown'),
                    "sender_address": metadata.get('sender_address', ''),
                    "receiver_names": metadata.get('receiver_names', []),
                    "receiver_addresses": metadata.get('receiver_addresses', []),
                    "created_time": metadata.get('created_time', ''),
                    "correspondence_thread": metadata.get('correspondence_thread', ''),
                    "web_link": metadata.get('web_link', ''),
                    "has_attachments": metadata.get('has_attachments', False),
                    "importance": metadata.get('importance', 'normal'),
                    "is_reply": metadata.get('is_reply', False),
                    "is_forward": metadata.get('is_forward', False)
                }
                email_data.append(email_info)
        
        # Sort by created_time (newest first)
        email_data.sort(key=lambda x: x.get('created_time', ''), reverse=True)
        
        # Apply pagination
        total = len(email_data)
        paginated_emails = email_data[offset:offset + limit]
        
        return {
            "success": True,
            "emails": paginated_emails,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get email list: {str(e)}")


@router.get("/detail/{email_id}")
async def get_email_detail(
    email_id: str,
    vector_store: VectorStorePort = Depends(get_vector_store)
):
    """Get detailed information for a specific email."""
    try:
        collection_name = "emails"
        
        # Get all embeddings and filter for this email
        all_embeddings = await vector_store.get_all_embeddings(collection_name, limit=10000)
        
        # Filter embeddings for this specific email
        email_embeddings = []
        for embedding in all_embeddings:
            if embedding.metadata.get('email_id') == email_id:
                email_embeddings.append(embedding)
        
        if not email_embeddings:
            raise HTTPException(status_code=404, detail="Email not found")
        
        # Find subject and body embeddings by ID suffix
        subject_embedding = None
        body_embedding = None
        
        for embedding in email_embeddings:
            if embedding.id.endswith('_subject'):
                subject_embedding = embedding
            elif embedding.id.endswith('_body'):
                body_embedding = embedding
        
        # Build detailed email info
        base_metadata = (subject_embedding or body_embedding).metadata
        email_detail = {
            "id": email_id,
            "subject": subject_embedding.metadata.get('content', 'No Subject') if subject_embedding else 'No Subject',
            "body_content": body_embedding.metadata.get('content', 'No Content') if body_embedding else 'No Content',
            "sender_name": base_metadata.get('sender_name', 'Unknown'),
            "sender_address": base_metadata.get('sender_address', ''),
            "receiver_names": base_metadata.get('receiver_names', []),
            "receiver_addresses": base_metadata.get('receiver_addresses', []),
            "created_time": base_metadata.get('created_time'),
            "correspondence_thread": base_metadata.get('correspondence_thread'),
            "web_link": base_metadata.get('web_link'),
            "has_attachments": base_metadata.get('has_attachments', False),
            "importance": base_metadata.get('importance', 'normal'),
            "is_reply": base_metadata.get('is_reply', False),
            "is_forward": base_metadata.get('is_forward', False),
            "embeddings_count": len(email_embeddings)
        }
        
        return {
            "success": True,
            "email": email_detail
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get email detail: {str(e)}")
