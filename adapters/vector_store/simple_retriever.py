"""
Simple retriever adapter that uses vector store directly.
"""

from typing import List, Optional, Dict, Any
from core.entities.document import Query, RetrievalResult
from core.ports.retriever import RetrieverPort
from core.ports.vector_store import VectorStorePort
from core.ports.embedding_model import EmbeddingModelPort


class SimpleRetrieverAdapter(RetrieverPort):
    """Simple retriever that uses vector store directly for similarity search."""
    
    def __init__(
        self,
        vector_store: VectorStorePort,
        embedding_model: EmbeddingModelPort
    ):
        self._vector_store = vector_store
        self._embedding_model = embedding_model
        self._collection_name = "documents"
    
    def set_collection_name(self, collection_name: str) -> None:
        """Set the collection name for retrieval."""
        self._collection_name = collection_name
    
    def get_collection_name(self) -> str:
        """Get the current collection name."""
        return self._collection_name
    
    def get_retriever_type(self) -> str:
        """Get the type of this retriever."""
        return "simple_vector_retriever"
    
    async def retrieve(
        self,
        query: Query,
        top_k: int = 10,
        score_threshold: Optional[float] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResult]:
        """Retrieve documents based on query."""
        try:
            # Generate embedding for query
            query_vector = await self._embedding_model.embed_query(query.text)
            
            # Search in vector store
            search_results = await self._vector_store.search_similar(
                query_vector=query_vector,
                collection_name=self._collection_name,
                top_k=top_k,
                score_threshold=score_threshold,
                filter_metadata=filter_metadata
            )
            
            # Convert to RetrievalResult
            results = []
            for i, result in enumerate(search_results):
                retrieval_result = RetrievalResult(
                    document_id=result.document_id,
                    chunk_id=result.chunk_id,
                    content=result.content,
                    score=result.score,
                    rank=i + 1,
                    metadata=result.metadata
                )
                results.append(retrieval_result)
            
            return results
            
        except Exception as e:
            raise Exception(f"Retrieval failed: {str(e)}")
    
    async def retrieve_by_text(
        self,
        query_text: str,
        top_k: int = 10,
        score_threshold: Optional[float] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResult]:
        """Retrieve relevant documents for a text query."""
        try:
            # Create Query entity from text
            query = Query.create(query_text)
            
            # Use the regular retrieve method
            return await self.retrieve(
                query=query,
                top_k=top_k,
                score_threshold=score_threshold,
                filter_metadata=filter_metadata
            )
            
        except Exception as e:
            raise Exception(f"Text retrieval failed: {str(e)}")
    
    async def retrieve_similar_documents(
        self,
        document_id: str,
        top_k: int = 10,
        score_threshold: Optional[float] = None
    ) -> List[RetrievalResult]:
        """Find documents similar to a given document."""
        try:
            # Get embeddings for the reference document
            doc_embeddings = await self._vector_store.get_embeddings_by_document(
                document_id, self._collection_name
            )
            
            if not doc_embeddings:
                return []
            
            # Use the first embedding as reference (could be improved)
            reference_vector = doc_embeddings[0].vector
            
            # Search for similar vectors
            search_results = await self._vector_store.search_similar(
                query_vector=reference_vector,
                collection_name=self._collection_name,
                top_k=top_k + 10,  # Get more to filter out self-matches
                score_threshold=score_threshold
            )
            
            # Filter out the reference document and convert to RetrievalResult
            results = []
            rank = 1
            for result in search_results:
                if result.document_id != document_id:
                    retrieval_result = RetrievalResult(
                        document_id=result.document_id,
                        chunk_id=result.chunk_id,
                        content=result.content,
                        score=result.score,
                        rank=rank,
                        metadata=result.metadata
                    )
                    results.append(retrieval_result)
                    rank += 1
                    
                    if len(results) >= top_k:
                        break
            
            return results
            
        except Exception as e:
            raise Exception(f"Similar document retrieval failed: {str(e)}")
    
    async def retrieve_with_reranking(
        self,
        query: Query,
        top_k: int = 10,
        rerank_top_k: int = 100,
        score_threshold: Optional[float] = None
    ) -> List[RetrievalResult]:
        """Retrieve with reranking (simplified - just returns regular retrieval)."""
        # For now, just return regular retrieval with higher top_k
        return await self.retrieve(
            query=query,
            top_k=min(top_k, rerank_top_k),
            score_threshold=score_threshold
        )
    
    async def get_retriever_info(self) -> Dict[str, Any]:
        """Get information about this retriever."""
        return {
            "type": self.get_retriever_type(),
            "collection_name": self._collection_name,
            "embedding_model": self._embedding_model.get_model_name(),
            "vector_dimension": self._embedding_model.get_dimension(),
            "capabilities": [
                "similarity_search",
                "document_similarity",
                "metadata_filtering"
            ]
        }
    
    async def health_check(self) -> bool:
        """Check if the retriever is healthy."""
        try:
            # Check vector store health
            vector_store_healthy = await self._vector_store.health_check()
            
            # Check embedding model availability
            embedding_available = self._embedding_model.is_available()
            
            # Check collection exists
            collection_exists = await self._vector_store.collection_exists(self._collection_name)
            
            return vector_store_healthy and embedding_available and collection_exists
            
        except Exception:
            return False
