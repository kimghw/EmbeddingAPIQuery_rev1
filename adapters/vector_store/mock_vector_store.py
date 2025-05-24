"""
Mock vector store adapter for testing purposes.
"""

from typing import List, Optional, Dict, Any
from core.entities.document import Embedding, RetrievalResult
from core.ports.vector_store import VectorStorePort


class MockVectorStoreAdapter(VectorStorePort):
    """Mock vector store adapter for testing without external dependencies."""
    
    def __init__(self):
        """Initialize mock vector store."""
        self.collections: Dict[str, Dict[str, Any]] = {}
        self.embeddings: Dict[str, Dict[str, Embedding]] = {}
    
    async def create_collection(self, collection_name: str, dimension: int, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Create a new collection in the vector store."""
        self.collections[collection_name] = {
            "dimension": dimension,
            "metadata": metadata or {},
            "created_at": "2024-01-01T00:00:00Z"
        }
        self.embeddings[collection_name] = {}
        return True
    
    async def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection from the vector store."""
        if collection_name in self.collections:
            del self.collections[collection_name]
            del self.embeddings[collection_name]
            return True
        return False
    
    async def collection_exists(self, collection_name: str) -> bool:
        """Check if a collection exists."""
        return collection_name in self.collections
    
    async def add_embedding(self, embedding: Embedding, collection_name: str) -> bool:
        """Add a single embedding to the collection."""
        if collection_name not in self.collections:
            return False
        
        self.embeddings[collection_name][embedding.id] = embedding
        return True
    
    async def add_embeddings(self, embeddings: List[Embedding], collection_name: str) -> bool:
        """Add multiple embeddings to the collection."""
        if collection_name not in self.collections:
            return False
        
        for embedding in embeddings:
            self.embeddings[collection_name][embedding.id] = embedding
        return True
    
    async def update_embedding(self, embedding: Embedding, collection_name: str) -> bool:
        """Update an existing embedding in the collection."""
        if collection_name not in self.collections:
            return False
        
        if embedding.id in self.embeddings[collection_name]:
            self.embeddings[collection_name][embedding.id] = embedding
            return True
        return False
    
    async def delete_embedding(self, embedding_id: str, collection_name: str) -> bool:
        """Delete an embedding from the collection."""
        if collection_name not in self.collections:
            return False
        
        if embedding_id in self.embeddings[collection_name]:
            del self.embeddings[collection_name][embedding_id]
            return True
        return False
    
    async def delete_embeddings_by_document(self, document_id: str, collection_name: str) -> bool:
        """Delete all embeddings for a specific document."""
        if collection_name not in self.collections:
            return False
        
        to_delete = []
        for emb_id, embedding in self.embeddings[collection_name].items():
            if embedding.document_id == document_id:
                to_delete.append(emb_id)
        
        for emb_id in to_delete:
            del self.embeddings[collection_name][emb_id]
        
        return len(to_delete) > 0
    
    async def search_similar(
        self, 
        query_vector: List[float], 
        collection_name: str, 
        top_k: int = 10,
        score_threshold: Optional[float] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResult]:
        """Search for similar vectors (mock implementation)."""
        if collection_name not in self.collections:
            return []
        
        # Mock similarity search - return embeddings with mock scores
        results = []
        embeddings_list = list(self.embeddings[collection_name].values())
        
        # 메타데이터 필터링 적용
        if filter_metadata:
            filtered_embeddings = []
            for embedding in embeddings_list:
                match = True
                for key, value in filter_metadata.items():
                    if embedding.metadata.get(key) != value:
                        match = False
                        break
                if match:
                    filtered_embeddings.append(embedding)
            embeddings_list = filtered_embeddings
        
        # top_k만큼 결과 생성
        for i, embedding in enumerate(embeddings_list[:top_k]):
            # Mock similarity score (높은 점수부터 낮은 점수로)
            score = 0.95 - (i * 0.05)  # 0.95, 0.90, 0.85, ...
            
            # 점수 임계값 필터링
            if score_threshold is not None and score < score_threshold:
                continue
            
            # 메타데이터에서 content 가져오기 (있으면)
            content = embedding.metadata.get('content', f"Mock content for chunk {embedding.chunk_id}")
            
            result = RetrievalResult.create(
                document_id=embedding.document_id,
                chunk_id=embedding.chunk_id,
                content=content,
                score=score,
                rank=i + 1,
                metadata=embedding.metadata
            )
            results.append(result)
        
        return results
    
    async def get_embedding(self, embedding_id: str, collection_name: str) -> Optional[Embedding]:
        """Get a specific embedding by ID."""
        if collection_name not in self.collections:
            return None
        
        return self.embeddings[collection_name].get(embedding_id)
    
    async def get_embeddings_by_document(self, document_id: str, collection_name: str) -> List[Embedding]:
        """Get all embeddings for a specific document."""
        if collection_name not in self.collections:
            return []
        
        results = []
        for embedding in self.embeddings[collection_name].values():
            if embedding.document_id == document_id:
                results.append(embedding)
        
        return results
    
    async def count_embeddings(self, collection_name: str) -> int:
        """Count total number of embeddings in the collection."""
        if collection_name not in self.collections:
            return 0
        
        return len(self.embeddings[collection_name])
    
    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get information about a collection."""
        if collection_name not in self.collections:
            return {}
        
        collection_info = self.collections[collection_name].copy()
        collection_info["embedding_count"] = len(self.embeddings[collection_name])
        collection_info["store_type"] = "mock"
        
        return collection_info
    
    async def list_collections(self) -> List[str]:
        """List all available collections."""
        return list(self.collections.keys())
    
    def get_store_type(self) -> str:
        """Get the type of vector store."""
        return "mock"
    
    async def health_check(self) -> bool:
        """Check if the vector store is healthy and accessible."""
        return True  # Mock is always healthy
    
    async def optimize_collection(self, collection_name: str) -> bool:
        """Optimize the collection for better performance."""
        return collection_name in self.collections
