"""
Email processing use cases for Document Embedding & Retrieval System.
"""

from typing import List, Optional, Dict, Any
from core.entities.email import Email, EmailEmbedding
from core.ports.email_loader import EmailLoaderPort
from core.ports.embedding_model import EmbeddingModelPort
from core.ports.vector_store import VectorStorePort
from config.settings import ConfigPort


class EmailProcessingUseCase:
    """Use case for processing emails: loading, embedding, and storing."""
    
    def __init__(
        self,
        email_loader: EmailLoaderPort,
        embedding_model: EmbeddingModelPort,
        vector_store: VectorStorePort,
        config: ConfigPort
    ):
        self._email_loader = email_loader
        self._embedding_model = embedding_model
        self._vector_store = vector_store
        self._config = config
        self._email_collection_name = "emails"
    
    async def process_emails_from_json(
        self, 
        json_data: Dict[str, Any], 
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process emails from JSON data: load, embed, and store."""
        try:
            # Load emails from JSON
            emails = await self._email_loader.load_from_json(json_data, metadata)
            
            if not emails:
                return {
                    "success": True,
                    "message": "No emails found in JSON data",
                    "processed_count": 0,
                    "embedded_count": 0
                }
            
            # Process embeddings
            result = await self._process_emails(emails)
            
            # Add JSON statistics
            loader_stats = self._email_loader.get_statistics(json_data) if hasattr(self._email_loader, 'get_statistics') else {}
            result.update({
                "loader_statistics": loader_stats,
                "json_source": json_data.get("@odata.context", "unknown")
            })
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "processed_count": 0,
                "embedded_count": 0
            }
    
    async def process_emails_from_webhook(
        self, 
        webhook_data: Dict[str, Any], 
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process emails from webhook payload."""
        try:
            # Add webhook-specific metadata
            webhook_metadata = metadata or {}
            webhook_metadata.update({
                "processing_type": "webhook",
                "real_time": True
            })
            
            # Load emails from webhook
            emails = await self._email_loader.load_from_webhook(webhook_data, webhook_metadata)
            
            if not emails:
                return {
                    "success": True,
                    "message": "No emails found in webhook data",
                    "processed_count": 0,
                    "embedded_count": 0
                }
            
            # Process embeddings
            result = await self._process_emails(emails)
            result["webhook_type"] = self._email_loader._detect_webhook_type(webhook_data) if hasattr(self._email_loader, '_detect_webhook_type') else "unknown"
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "processed_count": 0,
                "embedded_count": 0,
                "webhook_type": "unknown"
            }
    
    async def process_multiple_json_files(
        self, 
        json_files: List[Dict[str, Any]], 
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process emails from multiple JSON files."""
        try:
            # Load emails from all files
            all_emails = await self._email_loader.load_multiple_json_files(json_files, metadata)
            
            if not all_emails:
                return {
                    "success": True,
                    "message": "No emails found in JSON files",
                    "processed_count": 0,
                    "embedded_count": 0,
                    "files_processed": len(json_files)
                }
            
            # Process embeddings
            result = await self._process_emails(all_emails)
            result["files_processed"] = len(json_files)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "processed_count": 0,
                "embedded_count": 0,
                "files_processed": 0
            }
    
    async def _process_emails(self, emails: List[Email]) -> Dict[str, Any]:
        """Internal method to process a list of emails."""
        # Ensure email collection exists
        await self._ensure_email_collection()
        
        # Generate embeddings for all emails
        email_embeddings = await self._create_email_embeddings(emails)
        
        # Store embeddings in vector store
        await self._store_email_embeddings(email_embeddings)
        
        # Generate processing statistics
        stats = self._generate_processing_stats(emails, email_embeddings)
        
        return {
            "success": True,
            "processed_count": len(emails),
            "embedded_count": len(email_embeddings),
            "collection_name": self._email_collection_name,
            "statistics": stats,
            "emails": [
                {
                    "id": email.id,
                    "original_id": email.original_id,
                    "subject": email.get_display_subject(),
                    "sender": f"{email.sender.name} <{email.sender.address}>",
                    "recipients_count": len(email.get_all_recipients()),
                    "created_datetime": email.created_datetime.isoformat() if email.created_datetime else None,
                    "correspondence_thread": email.correspondence_thread,
                    "is_reply": email.is_reply(),
                    "is_forward": email.is_forward(),
                    "has_attachments": email.has_attachments,
                    "body_length": len(email.body_content),
                    "embeddings": [
                        {"type": "subject", "dimension": self._embedding_model.get_dimension()},
                        {"type": "body", "dimension": self._embedding_model.get_dimension()}
                    ]
                }
                for email in emails
            ]
        }
    
    async def _ensure_email_collection(self):
        """Ensure email collection exists in vector store."""
        if not await self._vector_store.collection_exists(self._email_collection_name):
            await self._vector_store.create_collection(
                collection_name=self._email_collection_name,
                dimension=self._embedding_model.get_dimension(),
                metadata={
                    "type": "emails",
                    "description": "Email embeddings for subject and body content",
                    "embedding_model": self._embedding_model.get_model_name(),
                    "created_by": "EmailProcessingUseCase"
                }
            )
    
    async def _create_email_embeddings(self, emails: List[Email]) -> List[EmailEmbedding]:
        """Create embeddings for all emails (both subject and body)."""
        all_embeddings = []
        
        # Prepare texts for batch embedding
        subjects = []
        bodies = []
        email_refs = []
        
        for email in emails:
            if email.subject.strip():
                subjects.append(email.subject)
                email_refs.append((email, "subject"))
            
            if email.body_content.strip():
                # Truncate body if too long
                body_content = email.body_content
                max_length = self._embedding_model.get_max_input_length()
                if len(body_content) > max_length:
                    body_content = body_content[:max_length]
                
                bodies.append(body_content)
                email_refs.append((email, "body"))
        
        # Generate embeddings in batches
        all_texts = subjects + bodies
        if all_texts:
            vectors = await self._embedding_model.embed_texts(all_texts)
            
            # Create EmailEmbedding entities
            for i, (vector, (email, embedding_type)) in enumerate(zip(vectors, email_refs)):
                if embedding_type == "subject":
                    embedding = EmailEmbedding.create_subject_embedding(
                        email=email,
                        vector=vector,
                        model=self._embedding_model.get_model_name()
                    )
                else:  # body
                    embedding = EmailEmbedding.create_body_embedding(
                        email=email,
                        vector=vector,
                        model=self._embedding_model.get_model_name()
                    )
                
                all_embeddings.append(embedding)
        
        return all_embeddings
    
    async def _store_email_embeddings(self, email_embeddings: List[EmailEmbedding]):
        """Store email embeddings in vector store."""
        if not email_embeddings:
            return
        
        # Convert EmailEmbedding to standard Embedding format
        from core.entities.document import Embedding
        
        standard_embeddings = []
        for email_emb in email_embeddings:
            # Create flattened payload for Qdrant with all email fields at top level
            payload = {
                "email_id": email_emb.email_id,
                "embedding_type": email_emb.embedding_type,
                "content": email_emb.content,
                "model": email_emb.model,
                "dimension": email_emb.dimension,
                "created_at": email_emb.created_at.isoformat(),
                # Flatten all metadata fields to top level
                "correspondence_thread": email_emb.metadata.get("correspondence_thread"),
                "created_time": email_emb.metadata.get("created_time"),
                "sender_name": email_emb.metadata.get("sender_name"),
                "sender_address": email_emb.metadata.get("sender_address"),
                "subject": email_emb.metadata.get("subject"),
                "web_link": email_emb.metadata.get("web_link"),
                "has_attachments": email_emb.metadata.get("has_attachments"),
                "receiver_addresses": email_emb.metadata.get("receiver_addresses", []),
                "is_reply": email_emb.metadata.get("is_reply"),
                "is_forward": email_emb.metadata.get("is_forward"),
                "importance": email_emb.metadata.get("importance"),
                "content_length": email_emb.metadata.get("content_length")
            }
            
            # Remove None values to keep payload clean
            payload = {k: v for k, v in payload.items() if v is not None}
            
            standard_embedding = Embedding.create(
                document_id=email_emb.email_id,
                vector=email_emb.vector,
                model=email_emb.model,
                chunk_id=email_emb.id,
                metadata=payload,
                embedding_id=email_emb.id
            )
            standard_embeddings.append(standard_embedding)
        
        # Store in vector database
        await self._vector_store.add_embeddings(standard_embeddings, self._email_collection_name)
    
    def _generate_processing_stats(self, emails: List[Email], embeddings: List[EmailEmbedding]) -> Dict[str, Any]:
        """Generate processing statistics."""
        # Email statistics
        total_emails = len(emails)
        reply_count = sum(1 for email in emails if email.is_reply())
        forward_count = sum(1 for email in emails if email.is_forward())
        
        # Sender statistics
        senders = {}
        for email in emails:
            sender = email.sender.address
            senders[sender] = senders.get(sender, 0) + 1
        
        # Thread statistics
        threads = {}
        for email in emails:
            thread = email.correspondence_thread or "unthreaded"
            threads[thread] = threads.get(thread, 0) + 1
        
        # Embedding statistics
        subject_embeddings = sum(1 for emb in embeddings if emb.embedding_type == "subject")
        body_embeddings = sum(1 for emb in embeddings if emb.embedding_type == "body")
        
        # Content statistics
        total_subject_chars = sum(len(email.subject) for email in emails)
        total_body_chars = sum(len(email.body_content) for email in emails)
        avg_subject_length = total_subject_chars / total_emails if total_emails > 0 else 0
        avg_body_length = total_body_chars / total_emails if total_emails > 0 else 0
        
        return {
            "email_counts": {
                "total": total_emails,
                "replies": reply_count,
                "forwards": forward_count,
                "regular": total_emails - reply_count - forward_count
            },
            "sender_distribution": dict(list(senders.items())[:10]),  # Top 10 senders
            "thread_distribution": dict(list(threads.items())[:10]),  # Top 10 threads
            "embedding_counts": {
                "total": len(embeddings),
                "subjects": subject_embeddings,
                "bodies": body_embeddings
            },
            "content_statistics": {
                "avg_subject_length": round(avg_subject_length),
                "avg_body_length": round(avg_body_length),
                "total_characters": total_subject_chars + total_body_chars
            }
        }
    
    async def delete_email(self, email_id: str) -> Dict[str, Any]:
        """Delete an email and all its embeddings."""
        try:
            success = await self._vector_store.delete_embeddings_by_document(
                email_id, 
                self._email_collection_name
            )
            
            return {
                "success": success,
                "email_id": email_id,
                "collection_name": self._email_collection_name
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "email_id": email_id
            }
    
    async def get_email_info(self, email_id: str) -> Dict[str, Any]:
        """Get information about an email's embeddings."""
        try:
            embeddings = await self._vector_store.get_embeddings_by_document(
                email_id, 
                self._email_collection_name
            )
            
            return {
                "success": True,
                "email_id": email_id,
                "embeddings_count": len(embeddings),
                "collection_name": self._email_collection_name,
                "embeddings": [
                    {
                        "id": emb.id,
                        "type": emb.metadata.get("embedding_type", "unknown"),
                        "model": emb.model,
                        "dimension": emb.dimension,
                        "content_preview": emb.metadata.get("content", "")[:100] + "..." if len(emb.metadata.get("content", "")) > 100 else emb.metadata.get("content", ""),
                        "correspondence_thread": emb.metadata.get("correspondence_thread"),
                        "sender": emb.metadata.get("sender_address"),
                        "created_at": emb.created_at.isoformat()
                    }
                    for emb in embeddings
                ]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "email_id": email_id
            }
    
    async def get_processing_stats(self) -> Dict[str, Any]:
        """Get email processing statistics."""
        try:
            if not await self._vector_store.collection_exists(self._email_collection_name):
                return {
                    "success": True,
                    "collection_exists": False,
                    "total_embeddings": 0,
                    "estimated_email_count": 0,
                    "collection_name": self._email_collection_name,
                    "embedding_model": self._embedding_model.get_model_name(),
                    "vector_dimension": self._embedding_model.get_dimension(),
                    "loader_type": self._email_loader.get_loader_type()
                }
            
            total_embeddings = await self._vector_store.count_embeddings(self._email_collection_name)
            collection_info = await self._vector_store.get_collection_info(self._email_collection_name)
            
            # Estimate email count (assuming 2 embeddings per email: subject + body)
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
                "loader_type": self._email_loader.get_loader_type()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
