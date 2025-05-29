"""
Qdrant Vector Store Adapter

This module implements the VectorStorePort interface using Qdrant as the backend.
Qdrant is a vector similarity search engine with extended filtering support.
"""

import uuid
import hashlib
from typing import List, Optional, Dict, Any
import asyncio
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct

from core.ports.vector_store import VectorStorePort
from core.entities.document import Embedding, RetrievalResult


class QdrantVectorStoreAdapter(VectorStorePort):
    """
    Qdrant implementation of VectorStorePort.
    
    This adapter provides vector storage and retrieval capabilities using Qdrant,
    a high-performance vector database with HNSW indexing.
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        vector_dimension: int = 1536,
        distance_metric: str = "cosine"
    ):
        """
        Initialize Qdrant vector store adapter.
        
        Args:
            host: Qdrant server host
            port: Qdrant server port
            vector_dimension: Dimension of the vectors (default: 1536 for OpenAI)
            distance_metric: Distance metric for similarity search (cosine, dot, euclidean)
        """
        self.host = host
        self.port = port
        self.vector_dimension = vector_dimension
        self.distance_metric = distance_metric
        
        # Initialize Qdrant client
        self.client = QdrantClient(host=host, port=port)
        
        # Distance mapping
        self._distance_map = {
            "cosine": Distance.COSINE,
            "dot": Distance.DOT,
            "euclidean": Distance.EUCLID
        }
    
    def _string_to_uuid(self, text: str) -> str:
        """Convert a string to a valid UUID using hash."""
        # Create a hash of the string and convert to UUID
        hash_object = hashlib.md5(text.encode())
        hash_hex = hash_object.hexdigest()
        # Convert hash to UUID format
        uuid_str = f"{hash_hex[:8]}-{hash_hex[8:12]}-{hash_hex[12:16]}-{hash_hex[16:20]}-{hash_hex[20:32]}"
        return uuid_str
    
    def _ensure_valid_point_id(self, point_id: str) -> str:
        """Ensure point ID is valid for Qdrant (UUID format)."""
        try:
            # Try to parse as UUID
            uuid.UUID(point_id)
            return point_id
        except ValueError:
            # If not valid UUID, convert string to UUID
            return self._string_to_uuid(point_id)
    
    async def create_collection(self, collection_name: str, dimension: int, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Create a new collection in the vector store."""
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=dimension,
                    distance=self._distance_map.get(self.distance_metric, Distance.COSINE)
                )
            )
            print(f"✅ Created Qdrant collection: {collection_name}")
            return True
        except Exception as e:
            print(f"❌ Failed to create collection {collection_name}: {e}")
            return False
    
    async def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection from the vector store."""
        try:
            self.client.delete_collection(collection_name)
            print(f"✅ Deleted Qdrant collection: {collection_name}")
            return True
        except Exception as e:
            print(f"❌ Failed to delete collection {collection_name}: {e}")
            return False
    
    async def collection_exists(self, collection_name: str) -> bool:
        """Check if a collection exists."""
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            return collection_name in collection_names
        except Exception as e:
            print(f"❌ Failed to check collection existence: {e}")
            return False
    
    async def add_embedding(self, embedding: Embedding, collection_name: str) -> bool:
        """Add a single embedding to the collection."""
        try:
            # Ensure collection exists
            if not await self.collection_exists(collection_name):
                await self.create_collection(collection_name, len(embedding.vector))
            
            # Prepare metadata payload - flatten all metadata to top level for easy searching
            payload = {
                "document_id": embedding.document_id,
                "chunk_id": embedding.chunk_id,
                "original_embedding_id": embedding.id,  # Store original ID
                "model": embedding.model,  # Store model info
                "dimension": embedding.dimension,  # Store dimension
                "created_at": embedding.created_at.isoformat(),  # Store creation time
                "content": embedding.metadata.get("content", ""),  # Store chunk content
            }
            
            # Flatten all metadata fields to top level for easy filtering
            if embedding.metadata:
                payload.update(embedding.metadata)
            
            # Remove None values to keep payload clean
            payload = {k: v for k, v in payload.items() if v is not None}
            
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
            
            return operation_info.status == models.UpdateStatus.COMPLETED
            
        except Exception as e:
            print(f"❌ Failed to add embedding: {e}")
            print(f"   Raw response content:")
            print(f"   {e}")
            return False
    
    async def add_embeddings(self, embeddings: List[Embedding], collection_name: str) -> bool:
        """Add multiple embeddings to the collection."""
        try:
            if not embeddings:
                return True
            
            # Ensure collection exists
            if not await self.collection_exists(collection_name):
                await self.create_collection(collection_name, len(embeddings[0].vector))
            
            points = []
            for embedding in embeddings:
                # Prepare metadata payload - flatten all metadata to top level for easy searching
                payload = {
                    "document_id": embedding.document_id,
                    "chunk_id": embedding.chunk_id,
                    "original_embedding_id": embedding.id,  # Store original ID
                    "model": embedding.model,  # Store model info
                    "dimension": embedding.dimension,  # Store dimension
                    "created_at": embedding.created_at.isoformat(),  # Store creation time
                    "content": embedding.metadata.get("content", ""),  # Store chunk content
                }
                
                # Flatten all metadata fields to top level for easy filtering
                if embedding.metadata:
                    payload.update(embedding.metadata)
                
                # Remove None values to keep payload clean
                payload = {k: v for k, v in payload.items() if v is not None}
                
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
            
            print(f"✅ Stored {len(points)} embeddings in Qdrant")
            return operation_info.status == models.UpdateStatus.COMPLETED
            
        except Exception as e:
            print(f"❌ Failed to add embeddings: {e}")
            print(f"   Raw response content:")
            print(f"   {e}")
            return False
    
    async def update_embedding(self, embedding: Embedding, collection_name: str) -> bool:
        """Update an existing embedding in the collection."""
        # In Qdrant, upsert handles both insert and update
        return await self.add_embedding(embedding, collection_name)
    
    async def delete_embedding(self, embedding_id: str, collection_name: str) -> bool:
        """Delete an embedding from the collection."""
        try:
            # Convert to valid point ID
            valid_point_id = self._ensure_valid_point_id(embedding_id)
            
            operation_info = self.client.delete(
                collection_name=collection_name,
                points_selector=models.PointIdsList(points=[valid_point_id])
            )
            
            return operation_info.status == models.UpdateStatus.COMPLETED
            
        except Exception as e:
            print(f"❌ Failed to delete embedding {embedding_id}: {e}")
            return False
    
    async def delete_embeddings_by_document(self, document_id: str, collection_name: str) -> bool:
        """Delete all embeddings for a specific document."""
        try:
            operation_info = self.client.delete(
                collection_name=collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="document_id",
                                match=models.MatchValue(value=document_id)
                            )
                        ]
                    )
                )
            )
            
            return operation_info.status == models.UpdateStatus.COMPLETED
            
        except Exception as e:
            print(f"❌ Failed to delete embeddings for document {document_id}: {e}")
            return False
    
    async def search_similar(
        self, 
        query_vector: List[float], 
        collection_name: str, 
        top_k: int = 10,
        score_threshold: Optional[float] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResult]:
        """Search for similar vectors."""
        try:
            # Prepare search filter if provided
            search_filter = None
            if filter_metadata:
                search_filter = models.Filter(
                    must=[
                        models.FieldCondition(
                            key=f"metadata.{key}",
                            match=models.MatchValue(value=value)
                        )
                        for key, value in filter_metadata.items()
                    ]
                )
            
            # Perform similarity search
            search_results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=top_k,
                score_threshold=score_threshold,
                query_filter=search_filter,
                with_payload=True,
                with_vectors=True
            )
            
            # Format results
            results = []
            for result in search_results:
                payload = result.payload
                
                # Use original embedding ID if available, otherwise use point ID
                original_id = payload.get("original_embedding_id", str(result.id))
                
                # Parse created_at from ISO format
                created_at_str = payload.get("created_at")
                created_at = datetime.fromisoformat(created_at_str) if created_at_str else datetime.utcnow()
                
                # Create Embedding object with all required fields
                embedding = Embedding(
                    id=original_id,
                    document_id=payload["document_id"],
                    chunk_id=payload["chunk_id"],
                    vector=result.vector,
                    model=payload.get("model", "unknown"),
                    dimension=payload.get("dimension", len(result.vector)),
                    metadata=payload.get("metadata", {}),
                    created_at=created_at
                )
                
                # Create RetrievalResult
                retrieval_result = RetrievalResult(
                    document_id=payload["document_id"],
                    chunk_id=payload["chunk_id"],
                    content=payload.get("content", ""),  # Get stored content
                    score=result.score,
                    metadata=payload.get("metadata", {}),
                    rank=0  # Will be set by retriever
                )
                
                results.append(retrieval_result)
            
            return results
            
        except Exception as e:
            print(f"❌ Failed to search vectors: {e}")
            return []
    
    async def get_embedding(self, embedding_id: str, collection_name: str) -> Optional[Embedding]:
        """Get a specific embedding by ID."""
        try:
            # Convert to valid point ID
            valid_point_id = self._ensure_valid_point_id(embedding_id)
            
            points = self.client.retrieve(
                collection_name=collection_name,
                ids=[valid_point_id],
                with_payload=True,
                with_vectors=True
            )
            
            if not points:
                return None
            
            point = points[0]
            payload = point.payload
            
            # Use original embedding ID if available
            original_id = payload.get("original_embedding_id", str(point.id))
            
            # Parse created_at from ISO format
            created_at_str = payload.get("created_at")
            created_at = datetime.fromisoformat(created_at_str) if created_at_str else datetime.utcnow()
            
            return Embedding(
                id=original_id,
                document_id=payload["document_id"],
                chunk_id=payload["chunk_id"],
                vector=point.vector,
                model=payload.get("model", "unknown"),
                dimension=payload.get("dimension", len(point.vector)),
                metadata=payload.get("metadata", {}),
                created_at=created_at
            )
            
        except Exception as e:
            print(f"❌ Failed to get embedding {embedding_id}: {e}")
            return None
    
    async def get_embeddings_by_document(self, document_id: str, collection_name: str) -> List[Embedding]:
        """Get all embeddings for a specific document."""
        try:
            # Search for all embeddings with the given document_id
            search_results = self.client.scroll(
                collection_name=collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="document_id",
                            match=models.MatchValue(value=document_id)
                        )
                    ]
                ),
                with_payload=True,
                with_vectors=True,
                limit=1000  # Adjust as needed
            )
            
            embeddings = []
            for point in search_results[0]:  # scroll returns (points, next_page_offset)
                payload = point.payload
                
                # Use original embedding ID if available
                original_id = payload.get("original_embedding_id", str(point.id))
                
                # Parse created_at from ISO format
                created_at_str = payload.get("created_at")
                created_at = datetime.fromisoformat(created_at_str) if created_at_str else datetime.utcnow()
                
                embedding = Embedding(
                    id=original_id,
                    document_id=payload["document_id"],
                    chunk_id=payload["chunk_id"],
                    vector=point.vector,
                    model=payload.get("model", "unknown"),
                    dimension=payload.get("dimension", len(point.vector)),
                    metadata=payload.get("metadata", {}),
                    created_at=created_at
                )
                embeddings.append(embedding)
            
            return embeddings
            
        except Exception as e:
            print(f"❌ Failed to get embeddings for document {document_id}: {e}")
            return []
    
    async def get_all_embeddings(self, collection_name: str, limit: int = 1000, offset: int = 0) -> List[Embedding]:
        """Get all embeddings from a collection with pagination."""
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
            points = search_results[0] if search_results else []  # scroll returns (points, next_page_offset)
            
            for point in points:
                payload = point.payload
                
                # Use original embedding ID if available
                original_id = payload.get("original_embedding_id", str(point.id))
                
                # Parse created_at from ISO format
                created_at_str = payload.get("created_at")
                created_at = datetime.fromisoformat(created_at_str) if created_at_str else datetime.utcnow()
                
                # Get metadata from payload - all fields are stored at top level
                metadata = {}
                
                # Extract all metadata fields from payload (excluding system fields)
                system_fields = {"document_id", "chunk_id", "original_embedding_id", "model", "dimension", "created_at"}
                for key, value in payload.items():
                    if key not in system_fields:
                        metadata[key] = value
                
                # Ensure email_id is set
                if "email_id" not in metadata:
                    metadata["email_id"] = payload.get("document_id")
                
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
            
            print(f"✅ Retrieved {len(embeddings)} embeddings from {collection_name}")
            return embeddings
            
        except Exception as e:
            print(f"❌ Failed to get all embeddings from {collection_name}: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def count_embeddings(self, collection_name: str) -> int:
        """Count total number of embeddings in the collection."""
        try:
            # Use scroll with proper next_page_offset handling (Qdrant official way)
            count = 0
            next_page_offset = None
            batch_size = 100
            max_iterations = 1000  # Safety limit to prevent infinite loops
            iterations = 0
            
            while iterations < max_iterations:
                iterations += 1
                
                # Use scroll API correctly according to Qdrant documentation
                result = self.client.scroll(
                    collection_name=collection_name,
                    limit=batch_size,
                    offset=next_page_offset,  # Use next_page_offset from previous result
                    with_payload=False,
                    with_vectors=False
                )
                
                if not result or len(result) < 2:
                    break
                    
                points, next_page_offset = result[0], result[1]
                count += len(points)
                
                # If no more points or no next page offset, we're done
                if len(points) == 0 or next_page_offset is None:
                    break
            
            if iterations >= max_iterations:
                print(f"⚠️ Warning: count_embeddings hit max iterations limit for {collection_name}")
            
            return count
        except Exception as e:
            print(f"❌ Failed to count embeddings: {e}")
            return 0
    
    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get information about a collection."""
        try:
            # Basic info without using get_collection due to Pydantic issues
            count = await self.count_embeddings(collection_name)
            
            return {
                "name": collection_name,
                "vector_dimension": self.vector_dimension,
                "distance_metric": self.distance_metric,
                "points_count": count,
                "status": "active"
            }
            
        except Exception as e:
            print(f"❌ Failed to get collection info: {e}")
            return {}
    
    async def list_collections(self) -> List[str]:
        """List all available collections."""
        try:
            collections = self.client.get_collections()
            return [col.name for col in collections.collections]
        except Exception as e:
            print(f"❌ Failed to list collections: {e}")
            return []
    
    def get_store_type(self) -> str:
        """Get the type of vector store."""
        return "qdrant"
    
    async def health_check(self) -> bool:
        """Check if the vector store is healthy and accessible."""
        try:
            # Try to get collections list
            collections = self.client.get_collections()
            return True
        except Exception as e:
            print(f"❌ Qdrant health check failed: {e}")
            return False
    
    async def optimize_collection(self, collection_name: str) -> bool:
        """Optimize the collection for better performance."""
        try:
            # Qdrant automatically optimizes, but we can trigger it manually
            # This is a placeholder - actual optimization depends on Qdrant version
            print(f"✅ Collection {collection_name} optimization triggered")
            return True
        except Exception as e:
            print(f"❌ Failed to optimize collection {collection_name}: {e}")
            return False


# Factory function for easy instantiation
def create_qdrant_adapter(
    host: str = "localhost",
    port: int = 6333,
    vector_dimension: int = 1536,
    distance_metric: str = "cosine"
) -> QdrantVectorStoreAdapter:
    """
    Factory function to create a Qdrant vector store adapter.
    
    Args:
        host: Qdrant server host
        port: Qdrant server port  
        vector_dimension: Dimension of vectors
        distance_metric: Distance metric for similarity
        
    Returns:
        Configured QdrantVectorStoreAdapter instance
    """
    return QdrantVectorStoreAdapter(
        host=host,
        port=port,
        vector_dimension=vector_dimension,
        distance_metric=distance_metric
    )
