"""
Email retrieval use cases for Document Embedding & Retrieval System.
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
            
            # Prepare search filters
            search_filters = filters or {}
            
            # Search based on type
            if search_type == "subject":
                search_filters["embedding_type"] = "subject"
                results = await self._search_with_filters(query_vector, top_k, search_filters)
            elif search_type == "body":
                search_filters["embedding_type"] = "body"
                results = await self._search_with_filters(query_vector, top_k, search_filters)
            else:  # both
                # Search both subject and body, then merge results
                subject_filters = {**search_filters, "embedding_type": "subject"}
                body_filters = {**search_filters, "embedding_type": "body"}
                
                subject_results = await self._search_with_filters(query_vector, top_k, subject_filters)
                body_results = await self._search_with_filters(query_vector, top_k, body_filters)
                
                # Merge and deduplicate results by email_id
                results = self._merge_search_results(subject_results, body_results, top_k)
            
            # Format results
            formatted_results = self._format_search_results(results, query_text)
            
            return {
                "success": True,
                "query": query_text,
                "search_type": search_type,
                "total_results": len(formatted_results),
                "collection_name": self._email_collection_name,
                "results": formatted_results,
                "filters_applied": search_filters
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
            filters = {"correspondence_thread": thread_id}
            
            # Search without query vector (get all emails in thread)
            results = await self._vector_store.search_with_filter(
                collection_name=self._email_collection_name,
                filter_conditions=filters,
                limit=top_k
            )
            
            # Group by email_id and get unique emails
            unique_emails = {}
            for result in results:
                email_id = result.embedding.metadata.get("email_id")
                if email_id and email_id not in unique_emails:
                    unique_emails[email_id] = result
            
            formatted_results = self._format_search_results(list(unique_emails.values()), f"thread:{thread_id}")
            
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
            filters = {"sender_address": sender_address}
            
            results = await self._vector_store.search_with_filter(
                collection_name=self._email_collection_name,
                filter_conditions=filters,
                limit=top_k
            )
            
            # Group by email_id and get unique emails
            unique_emails = {}
            for result in results:
                email_id = result.embedding.metadata.get("email_id")
                if email_id and email_id not in unique_emails:
                    unique_emails[email_id] = result
            
            formatted_results = self._format_search_results(list(unique_emails.values()), f"sender:{sender_address}")
            
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
    
    async def search_by_date_range(
        self, 
        start_date: str, 
        end_date: str, 
        query_text: Optional[str] = None,
        top_k: int = 10
    ) -> Dict[str, Any]:
        """Search emails by date range."""
        try:
            # Note: This is a simplified implementation
            # In a real system, you'd need proper date filtering in the vector store
            
            if query_text:
                # Combine text search with date filtering
                base_result = await self.search_emails(query_text, top_k * 2)  # Get more results to filter
                
                if not base_result["success"]:
                    return base_result
                
                # Filter results by date range (simplified)
                filtered_results = []
                for result in base_result["results"]:
                    created_time = result.get("created_time", "")
                    if start_date <= created_time <= end_date:
                        filtered_results.append(result)
                
                filtered_results = filtered_results[:top_k]
                
                return {
                    "success": True,
                    "query": query_text,
                    "date_range": {"start": start_date, "end": end_date},
                    "total_results": len(filtered_results),
                    "collection_name": self._email_collection_name,
                    "results": filtered_results
                }
            else:
                # Date-only search (would need vector store support)
                return {
                    "success": False,
                    "error": "Date-only search not implemented yet",
                    "date_range": {"start": start_date, "end": end_date},
                    "results": [],
                    "total_results": 0
                }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "date_range": {"start": start_date, "end": end_date},
                "results": [],
                "total_results": 0
            }
    
    async def get_similar_emails(
        self, 
        email_id: str, 
        top_k: int = 5
    ) -> Dict[str, Any]:
        """Find emails similar to a given email."""
        try:
            # Get the email's embeddings
            email_embeddings = await self._vector_store.get_embeddings_by_document(
                email_id, 
                self._email_collection_name
            )
            
            if not email_embeddings:
                return {
                    "success": False,
                    "error": f"Email {email_id} not found",
                    "email_id": email_id,
                    "results": [],
                    "total_results": 0
                }
            
            # Use the first embedding (subject or body) as reference
            reference_embedding = email_embeddings[0]
            
            # Search for similar emails
            similar_results = await self._vector_store.search_similar(
                reference_embedding.vector,
                self._email_collection_name,
                top_k + 1  # +1 to exclude the original email
            )
            
            # Filter out the original email
            filtered_results = [
                result for result in similar_results 
                if result.embedding.metadata.get("email_id") != email_id
            ][:top_k]
            
            formatted_results = self._format_search_results(filtered_results, f"similar_to:{email_id}")
            
            return {
                "success": True,
                "reference_email_id": email_id,
                "total_results": len(formatted_results),
                "collection_name": self._email_collection_name,
                "results": formatted_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "email_id": email_id,
                "results": [],
                "total_results": 0
            }
    
    async def _search_with_filters(
        self, 
        query_vector: List[float], 
        top_k: int, 
        filters: Dict[str, Any]
    ) -> List[Any]:
        """Search with filters applied."""
        if filters:
            # Use filtered search if vector store supports it
            if hasattr(self._vector_store, 'search_with_filter'):
                return await self._vector_store.search_with_filter(
                    query_vector=query_vector,
                    collection_name=self._email_collection_name,
                    filter_conditions=filters,
                    limit=top_k
                )
            else:
                # Fallback: search all and filter results
                all_results = await self._vector_store.search_similar(
                    query_vector,
                    self._email_collection_name,
                    top_k * 3  # Get more results to filter
                )
                
                # Apply filters manually
                filtered_results = []
                for result in all_results:
                    metadata = result.embedding.metadata
                    match = True
                    for key, value in filters.items():
                        if metadata.get(key) != value:
                            match = False
                            break
                    if match:
                        filtered_results.append(result)
                
                return filtered_results[:top_k]
        else:
            return await self._vector_store.search_similar(
                query_vector,
                self._email_collection_name,
                top_k
            )
    
    def _merge_search_results(self, subject_results: List[Any], body_results: List[Any], top_k: int) -> List[Any]:
        """Merge subject and body search results, avoiding duplicates."""
        # Create a dictionary to store best result for each email
        email_results = {}
        
        # Process subject results
        for result in subject_results:
            email_id = result.embedding.metadata.get("email_id")
            if email_id:
                if email_id not in email_results or result.score > email_results[email_id].score:
                    email_results[email_id] = result
        
        # Process body results
        for result in body_results:
            email_id = result.embedding.metadata.get("email_id")
            if email_id:
                if email_id not in email_results or result.score > email_results[email_id].score:
                    email_results[email_id] = result
        
        # Sort by score and return top_k
        merged_results = list(email_results.values())
        merged_results.sort(key=lambda x: x.score, reverse=True)
        
        return merged_results[:top_k]
    
    def _format_search_results(self, results: List[Any], query: str) -> List[Dict[str, Any]]:
        """Format search results for API response."""
        formatted_results = []
        
        for i, result in enumerate(results):
            metadata = result.embedding.metadata
            
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
                "content_preview": self._get_content_preview(result.embedding.metadata.get("content", "")),
                "metadata": {
                    "embedding_id": result.embedding.id,
                    "model": result.embedding.model,
                    "dimension": result.embedding.dimension
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
            # Note: This is a simplified implementation
            # In production, you'd want more efficient pagination
            
            # Get embeddings from vector store
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
                    "similarity_search",
                    "date_range_search"
                ]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
