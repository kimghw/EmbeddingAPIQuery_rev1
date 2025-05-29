"""
Email-optimized Qdrant Vector Store Adapter

This module extends the QdrantVectorStoreAdapter to properly handle email metadata
by flattening email-specific fields to the top level for easier access.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from qdrant_client.http.models import PointStruct

from .qdrant_vector_store import QdrantVectorStoreAdapter
from core.entities.document import Embedding


class QdrantEmailVectorStoreAdapter(QdrantVectorStoreAdapter):
    """
    Email-optimized Qdrant implementation that flattens email metadata.
    
    This adapter ensures that email-specific fields like email_id, embedding_type,
    sender_address, etc. are stored at the top level of the payload for easier access.
    """
    
    def _create_email_payload(self, embedding: Embedding) -> Dict[str, Any]:
        """Create payload with flattened email metadata."""
        
        # Start with base fields
        payload = {
            "document_id": embedding.document_id,
            "chunk_id": embedding.chunk_id,
            "original_embedding_id": embedding.id,
            "model": embedding.model,
            "dimension": embedding.dimension,
            "created_at": embedding.created_at.isoformat(),
            "content": embedding.metadata.get("content", ""),
        }
        
        # Flatten all metadata fields to top level
        if embedding.metadata:
            payload.update(embedding.metadata)
        
        return payload
    
    async def add_embedding(self, embedding: Embedding, collection_name: str) -> bool:
        """Add a single embedding with flattened email metadata."""
        try:
            # Ensure collection exists
            if not await self.collection_exists(collection_name):
                await self.create_collection(collection_name, len(embedding.vector))
            
            # Create flattened payload
            payload = self._create_email_payload(embedding)
            
            # Ensure valid point ID for Qdrant
            valid_point_id = self._ensure_valid_point_id(embedding.id)
            
            # Create point for Qdrant
            point = PointStruct(
                id=valid_point_id,
                vector=embedding.vector,
                payload=payload
            )
            
            # Store point in Qdrant
            operation_info = self.client.upsert(
                collection_name=collection_name,
                points=[point]
            )
            
            return operation_info.status.name == "COMPLETED"
            
        except Exception as e:
            print(f"❌ Failed to add email embedding: {e}")
            return False
    
    async def add_embeddings(self, embeddings: List[Embedding], collection_name: str) -> bool:
        """Add multiple embeddings with flattened email metadata."""
        try:
            if not embeddings:
                return True
            
            # Ensure collection exists
            if not await self.collection_exists(collection_name):
                await self.create_collection(collection_name, len(embeddings[0].vector))
            
            points = []
            for embedding in embeddings:
                # Create flattened payload
                payload = self._create_email_payload(embedding)
                
                # Ensure valid point ID for Qdrant
                valid_point_id = self._ensure_valid_point_id(embedding.id)
                
                # Create point for Qdrant
                point = PointStruct(
                    id=valid_point_id,
                    vector=embedding.vector,
                    payload=payload
                )
                points.append(point)
            
            # Store points in Qdrant
            operation_info = self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            
            print(f"✅ Stored {len(points)} email embeddings in Qdrant with flattened metadata")
            return operation_info.status.name == "COMPLETED"
            
        except Exception as e:
            print(f"❌ Failed to add email embeddings: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def get_all_embeddings(self, collection_name: str, limit: int = 1000, offset: int = 0) -> List[Embedding]:
        """Get all embeddings with properly reconstructed metadata."""
        try:
            # Use scroll to get all points
            search_results = self.client.scroll(
                collection_name=collection_name,
                limit=limit,
                offset=offset,
                with_payload=True,
                with_vectors=True
            )
            
            embeddings = []
            points = search_results[0] if search_results else []
            
            for point in points:
                payload = point.payload
                
                # Use original embedding ID if available
                original_id = payload.get("original_embedding_id", str(point.id))
                
                # Parse created_at from ISO format
                created_at_str = payload.get("created_at")
                created_at = datetime.fromisoformat(created_at_str) if created_at_str else datetime.utcnow()
                
                # Reconstruct metadata from flattened payload
                # Exclude system fields and keep email-specific fields
                system_fields = {
                    "document_id", "chunk_id", "original_embedding_id", 
                    "model", "dimension", "created_at"
                }
                
                metadata = {
                    key: value for key, value in payload.items() 
                    if key not in system_fields
                }
                
                embedding = Embedding(
                    id=original_id,
                    document_id=payload["document_id"],
                    chunk_id=payload["chunk_id"],
                    vector=point.vector,
                    model=payload.get("model", "unknown"),
                    dimension=payload.get("dimension", len(point.vector)),
                    metadata=metadata,
                    created_at=created_at
                )
                embeddings.append(embedding)
            
            print(f"✅ Retrieved {len(embeddings)} email embeddings from {collection_name}")
            return embeddings
            
        except Exception as e:
            print(f"❌ Failed to get email embeddings from {collection_name}: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_store_type(self) -> str:
        """Get the type of vector store."""
        return "qdrant_email"


# Factory function for easy instantiation
def create_qdrant_email_adapter(
    host: str = "localhost",
    port: int = 6333,
    vector_dimension: int = 1536,
    distance_metric: str = "cosine"
) -> QdrantEmailVectorStoreAdapter:
    """
    Factory function to create an email-optimized Qdrant vector store adapter.
    
    Args:
        host: Qdrant server host
        port: Qdrant server port  
        vector_dimension: Dimension of vectors
        distance_metric: Distance metric for similarity
        
    Returns:
        Configured QdrantEmailVectorStoreAdapter instance
    """
    return QdrantEmailVectorStoreAdapter(
        host=host,
        port=port,
        vector_dimension=vector_dimension,
        distance_metric=distance_metric
    )
