"""
Document retrieval use cases for Document Embedding & Retrieval System.
"""

from typing import List, Optional, Dict, Any
from core.entities.document import Query, RetrievalResult
from core.ports.retriever import RetrieverPort
from core.ports.embedding_model import EmbeddingModelPort
from core.ports.vector_store import VectorStorePort
from config.settings import ConfigPort


class DocumentRetrievalUseCase:
    """Use case for retrieving documents based on queries."""
    
    def __init__(
        self,
        retriever: RetrieverPort,
        embedding_model: EmbeddingModelPort,
        vector_store: VectorStorePort,
        config: ConfigPort
    ):
        self._retriever = retriever
        self._embedding_model = embedding_model
        self._vector_store = vector_store
        self._config = config
        
        # Set collection name for retriever
        self._retriever.set_collection_name(self._config.get_collection_name())
    
    async def search_documents(
        self, 
        query_text: str, 
        top_k: int = 10,
        score_threshold: Optional[float] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Search for documents using text query."""
        try:
            # Create query entity
            query = Query.create(query_text)
            
            # Retrieve documents
            results = await self._retriever.retrieve(
                query=query,
                top_k=top_k,
                score_threshold=score_threshold,
                filter_metadata=filter_metadata
            )
            
            return {
                "success": True,
                "query_id": query.id,
                "query_text": query_text,
                "results_count": len(results),
                "results": [
                    {
                        "document_id": result.document_id,
                        "chunk_id": result.chunk_id,
                        "content": result.content,
                        "score": result.score,
                        "rank": result.rank,
                        "metadata": result.metadata,
                        "is_chunk_result": result.is_chunk_result()
                    }
                    for result in results
                ],
                "retriever_type": self._retriever.get_retriever_type(),
                "collection_name": self._retriever.get_collection_name()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query_text": query_text
            }
    
    async def search_similar_documents(
        self, 
        document_id: str, 
        top_k: int = 10,
        score_threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """Find documents similar to a given document."""
        try:
            results = await self._retriever.retrieve_similar_documents(
                document_id=document_id,
                top_k=top_k,
                score_threshold=score_threshold
            )
            
            return {
                "success": True,
                "reference_document_id": document_id,
                "results_count": len(results),
                "results": [
                    {
                        "document_id": result.document_id,
                        "chunk_id": result.chunk_id,
                        "content": result.content,
                        "score": result.score,
                        "rank": result.rank,
                        "metadata": result.metadata,
                        "is_chunk_result": result.is_chunk_result()
                    }
                    for result in results
                ],
                "retriever_type": self._retriever.get_retriever_type(),
                "collection_name": self._retriever.get_collection_name()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "document_id": document_id
            }
    
    async def search_with_reranking(
        self, 
        query_text: str, 
        top_k: int = 10,
        rerank_top_k: int = 100,
        score_threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """Search with reranking for better results."""
        try:
            # Create query entity
            query = Query.create(query_text)
            
            # Retrieve with reranking
            results = await self._retriever.retrieve_with_reranking(
                query=query,
                top_k=top_k,
                rerank_top_k=rerank_top_k,
                score_threshold=score_threshold
            )
            
            return {
                "success": True,
                "query_id": query.id,
                "query_text": query_text,
                "results_count": len(results),
                "rerank_top_k": rerank_top_k,
                "results": [
                    {
                        "document_id": result.document_id,
                        "chunk_id": result.chunk_id,
                        "content": result.content,
                        "score": result.score,
                        "rank": result.rank,
                        "metadata": result.metadata,
                        "is_chunk_result": result.is_chunk_result()
                    }
                    for result in results
                ],
                "retriever_type": self._retriever.get_retriever_type(),
                "collection_name": self._retriever.get_collection_name()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query_text": query_text
            }
    
    async def search_by_vector(
        self, 
        query_vector: List[float], 
        top_k: int = 10,
        score_threshold: Optional[float] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Search using a pre-computed query vector."""
        try:
            collection_name = self._config.get_collection_name()
            
            results = await self._vector_store.search_similar(
                query_vector=query_vector,
                collection_name=collection_name,
                top_k=top_k,
                score_threshold=score_threshold,
                filter_metadata=filter_metadata
            )
            
            return {
                "success": True,
                "vector_dimension": len(query_vector),
                "results_count": len(results),
                "results": [
                    {
                        "document_id": result.document_id,
                        "chunk_id": result.chunk_id,
                        "content": result.content,
                        "score": result.score,
                        "rank": result.rank,
                        "metadata": result.metadata,
                        "is_chunk_result": result.is_chunk_result()
                    }
                    for result in results
                ],
                "collection_name": collection_name
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "vector_dimension": len(query_vector) if query_vector else 0
            }
    
    async def get_query_embedding(self, query_text: str) -> Dict[str, Any]:
        """Get embedding vector for a query text."""
        try:
            vector = await self._embedding_model.embed_query(query_text)
            
            return {
                "success": True,
                "query_text": query_text,
                "vector": vector,
                "dimension": len(vector),
                "model": self._embedding_model.get_model_name()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query_text": query_text
            }
    
    async def get_retrieval_stats(self) -> Dict[str, Any]:
        """Get retrieval system statistics."""
        try:
            collection_name = self._config.get_collection_name()
            
            # Check if collection exists
            if not await self._vector_store.collection_exists(collection_name):
                return {
                    "success": True,
                    "collection_exists": False,
                    "collection_name": collection_name
                }
            
            # Get collection info
            collection_info = await self._vector_store.get_collection_info(collection_name)
            total_embeddings = await self._vector_store.count_embeddings(collection_name)
            retriever_info = await self._retriever.get_retriever_info()
            
            return {
                "success": True,
                "collection_exists": True,
                "collection_name": collection_name,
                "total_embeddings": total_embeddings,
                "collection_info": collection_info,
                "retriever_info": retriever_info,
                "embedding_model": self._embedding_model.get_model_name(),
                "vector_dimension": self._embedding_model.get_dimension(),
                "retriever_type": self._retriever.get_retriever_type()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the retrieval system."""
        try:
            # Check vector store health
            vector_store_healthy = await self._vector_store.health_check()
            
            # Check embedding model availability
            embedding_model_available = self._embedding_model.is_available()
            
            # Check collection existence
            collection_name = self._config.get_collection_name()
            collection_exists = await self._vector_store.collection_exists(collection_name)
            
            overall_healthy = vector_store_healthy and embedding_model_available and collection_exists
            
            return {
                "success": True,
                "overall_healthy": overall_healthy,
                "vector_store_healthy": vector_store_healthy,
                "embedding_model_available": embedding_model_available,
                "collection_exists": collection_exists,
                "collection_name": collection_name,
                "retriever_type": self._retriever.get_retriever_type()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "overall_healthy": False
            }
