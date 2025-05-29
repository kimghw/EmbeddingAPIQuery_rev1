"""
Fixed Email retrieval use cases for Document Embedding & Retrieval System.
"""

from typing import List, Optional, Dict, Any
from core.entities.email import Email, EmailEmbedding
from core.ports.embedding_model import EmbeddingModelPort
from core.ports.vector_store import VectorStorePort
from core.ports.retriever import RetrieverPort
from config.settings import ConfigPort


class EmailRetrievalUseCase:
    """Use case for retrieving and searching emails."""
    
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
        self._email_collection_name = "emails"
    
    async def search_emails(
        self, 
        query_text: str, 
        top_k: int = 5,
        search_type: str = "both",  # "subject", "body", "both"
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search emails using text query.
        
        Args:
            query_text: Search query text
            top_k: Number of results to return
            search_type: Type of search ("subject", "body", "both")
            filters: Optional filters for search
        """
        try:
            # Check if collection exists
            if not await self._vector_store.collection_exists(self._email_collection_name):
                return {
                    "success": False,
                    "query": query_text,
                    "search_type": search_type,
                    "error": f"Email collection '{self._email_collection_name}' does not exist",
                    "results": [],
                    "total_results": 0,
                    "collection_name": self._email_collection_name
                }
            
            # Generate query embedding
            query_vector = await self._embedding_model.embed_text(query_text)
            
            # Search using vector store directly (simpler approach)
            search_results = await self._vector_store.search_similar(
                query_vector=query_vector,
                collection_name=self._email_collection_name,
                top_k=top_k * 2  # Get more to filter by type
            )
            
            # Filter by search type if specified
            filtered_results = []
            if search_type != "both":
                for result in search_results:
                    if hasattr(result, 'embedding'):
                        embedding_type = result.embedding.metadata.get("embedding_type")
                    else:
                        embedding_type = result.metadata.get("embedding_type")
                    
                    if embedding_type == search_type:
                        filtered_results.append(result)
                        if len(filtered_results) >= top_k:
                            break
            else:
                filtered_results = search_results[:top_k]
            
            # Format results
            formatted_results = self._format_search_results(filtered_results, query_text)
            
            return {
                "success": True,
                "query": query_text,
                "search_type": search_type,
                "total_results": len(formatted_results),
                "collection_name": self._email_collection_name,
                "results": formatted_results,
                "filters_applied": filters or {}
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query_text,
                "results": [],
                "total_results": 0
            }
    
    async def search_by_correspondence_thread(
        self, 
        thread_id: str, 
        top_k: int = 10
    ) -> Dict[str, Any]:
        """Search emails by correspondence thread."""
        try:
            # Get all embeddings and filter by thread
            all_embeddings = await self._vector_store.get_all_embeddings(
                collection_name=self._email_collection_name,
                limit=1000
            )
            
            # Filter by thread
            thread_emails = {}
            for embedding in all_embeddings:
                metadata = embedding.metadata
                if metadata.get("correspondence_thread") == thread_id:
                    email_id = metadata.get("email_id")
                    if email_id and email_id not in thread_emails:
                        thread_emails[email_id] = embedding
            
            # Convert to search result format
            results = []
            for email_id, embedding in list(thread_emails.items())[:top_k]:
                # Create a mock search result
                mock_result = type('MockResult', (), {
                    'score': 1.0,
                    'metadata': embedding.metadata
                })()
                results.append(mock_result)
            
            formatted_results = self._format_search_results(results, f"thread:{thread_id}")
            
            return {
                "success": True,
                "thread_id": thread_id,
                "total_results": len(formatted_results),
                "collection_name": self._email_collection_name,
                "results": formatted_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "thread_id": thread_id,
                "results": [],
                "total_results": 0
            }
    
    async def search_by_sender(
        self, 
        sender_address: str, 
        top_k: int = 10
    ) -> Dict[str, Any]:
        """Search emails by sender address."""
        try:
            # Get all embeddings and filter by sender
            all_embeddings = await self._vector_store.get_all_embeddings(
                collection_name=self._email_collection_name,
                limit=1000
            )
            
            # Filter by sender
            sender_emails = {}
            for embedding in all_embeddings:
                metadata = embedding.metadata
                if metadata.get("sender_address") == sender_address:
                    email_id = metadata.get("email_id")
                    if email_id and email_id not in sender_emails:
                        sender_emails[email_id] = embedding
            
            # Convert to search result format
            results = []
            for email_id, embedding in list(sender_emails.items())[:top_k]:
                # Create a mock search result
                mock_result = type('MockResult', (), {
                    'score': 1.0,
                    'metadata': embedding.metadata
                })()
                results.append(mock_result)
            
            formatted_results = self._format_search_results(results, f"sender:{sender_address}")
            
            return {
                "success": True,
                "sender_address": sender_address,
                "total_results": len(formatted_results),
                "collection_name": self._email_collection_name,
                "results": formatted_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "sender_address": sender_address,
                "results": [],
                "total_results": 0
            }
    
    def _format_search_results(self, results: List[Any], query: str) -> List[Dict[str, Any]]:
        """Format search results for API response."""
        formatted_results = []
        
        for i, result in enumerate(results):
            # Handle both RetrievalResult and SearchResult objects
            if hasattr(result, 'embedding'):
                # SearchResult from vector store
                metadata = result.embedding.metadata
                embedding_id = result.embedding.id
                model = result.embedding.model
                dimension = result.embedding.dimension
            else:
                # RetrievalResult from retriever or mock result
                metadata = result.metadata
                embedding_id = getattr(result, 'chunk_id', 'unknown')
                model = "unknown"
                dimension = 0
            
            formatted_result = {
                "rank": i + 1,
                "score": result.score,
                "email_id": metadata.get("email_id", "unknown"),
                "embedding_type": metadata.get("embedding_type", "unknown"),
                "subject": metadata.get("subject", ""),
                "sender_name": metadata.get("sender_name", ""),
                "sender_address": metadata.get("sender_address", ""),
                "created_time": metadata.get("created_time", ""),
                "correspondence_thread": metadata.get("correspondence_thread", ""),
                "web_link": metadata.get("web_link", ""),
                "has_attachments": metadata.get("has_attachments", False),
                "content_preview": self._get_content_preview(metadata.get("content", "")),
                "metadata": {
                    "embedding_id": embedding_id,
                    "model": model,
                    "dimension": dimension
                }
            }
            
            formatted_results.append(formatted_result)
        
        return formatted_results
    
    def _get_content_preview(self, content: str, max_length: int = 200) -> str:
        """Get content preview with truncation."""
        if not content:
            return ""
        
        if len(content) <= max_length:
            return content
        
        return content[:max_length] + "..."
    
    async def list_emails(
        self, 
        limit: int = 50, 
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """List emails with pagination and optional filters."""
        try:
            if not await self._vector_store.collection_exists(self._email_collection_name):
                return {
                    "success": True,
                    "emails": [],
                    "total": 0,
                    "limit": limit,
                    "offset": offset,
                    "collection_exists": False,
                    "collection_name": self._email_collection_name
                }
            
            # Get all embeddings with pagination
            all_embeddings = await self._vector_store.get_all_embeddings(
                collection_name=self._email_collection_name,
                limit=limit * 2,  # Get more to account for subject/body pairs
                offset=offset
            )
            
            # Group embeddings by email_id to get unique emails
            email_groups = {}
            for embedding in all_embeddings:
                email_id = embedding.metadata.get("email_id")
                if email_id:
                    if email_id not in email_groups:
                        email_groups[email_id] = []
                    email_groups[email_id].append(embedding)
            
            # Convert to email list format
            emails = []
            for email_id, embeddings in list(email_groups.items())[:limit]:
                # Find subject and body embeddings
                subject_embedding = None
                body_embedding = None
                
                for emb in embeddings:
                    if emb.metadata.get("embedding_type") == "subject":
                        subject_embedding = emb
                    elif emb.metadata.get("embedding_type") == "body":
                        body_embedding = emb
                
                # Use the first available embedding for metadata
                primary_embedding = subject_embedding or body_embedding or embeddings[0]
                metadata = primary_embedding.metadata
                
                email_info = {
                    "id": email_id,
                    "subject": metadata.get("subject", ""),
                    "sender_name": metadata.get("sender_name", ""),
                    "sender_address": metadata.get("sender_address", ""),
                    "created_time": metadata.get("created_time", ""),
                    "correspondence_thread": metadata.get("correspondence_thread", ""),
                    "web_link": metadata.get("web_link", ""),
                    "has_attachments": metadata.get("has_attachments", False),
                    "receiver_addresses": metadata.get("receiver_addresses", []),
                    "content_preview": self._get_content_preview(
                        body_embedding.metadata.get("content", "") if body_embedding else ""
                    ),
                    "embeddings_count": len(embeddings),
                    "has_subject_embedding": subject_embedding is not None,
                    "has_body_embedding": body_embedding is not None
                }
                
                # Apply filters if provided
                if filters:
                    match = True
                    for key, value in filters.items():
                        if email_info.get(key) != value:
                            match = False
                            break
                    if match:
                        emails.append(email_info)
                else:
                    emails.append(email_info)
            
            # Sort by created_time (newest first)
            emails.sort(key=lambda x: x.get("created_time", ""), reverse=True)
            
            return {
                "success": True,
                "emails": emails,
                "total": len(email_groups),
                "returned": len(emails),
                "limit": limit,
                "offset": offset,
                "collection_name": self._email_collection_name,
                "collection_exists": True,
                "filters_applied": filters or {}
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "emails": [],
                "total": 0,
                "limit": limit,
                "offset": offset
            }
    
    async def get_email_retrieval_stats(self) -> Dict[str, Any]:
        """Get email retrieval statistics."""
        try:
            if not await self._vector_store.collection_exists(self._email_collection_name):
                return {
                    "success": True,
                    "collection_exists": False,
                    "total_embeddings": 0,
                    "collection_name": self._email_collection_name
                }
            
            total_embeddings = await self._vector_store.count_embeddings(self._email_collection_name)
            collection_info = await self._vector_store.get_collection_info(self._email_collection_name)
            
            # Estimate unique emails (assuming 2 embeddings per email: subject + body)
            estimated_email_count = total_embeddings // 2
            
            return {
                "success": True,
                "collection_exists": True,
                "total_embeddings": total_embeddings,
                "estimated_email_count": estimated_email_count,
                "collection_name": self._email_collection_name,
                "collection_info": collection_info,
                "embedding_model": self._embedding_model.get_model_name(),
                "vector_dimension": self._embedding_model.get_dimension(),
                "retriever_type": self._retriever.__class__.__name__,
                "search_capabilities": [
                    "text_search",
                    "thread_search", 
                    "sender_search",
                    "similarity_search"
                ]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
