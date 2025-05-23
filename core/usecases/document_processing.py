"""
Document processing use cases for Document Embedding & Retrieval System.
"""

from typing import List, Optional, Dict, Any
from core.entities.document import Document, DocumentChunk, Embedding
from core.ports.document_loader import DocumentLoaderPort
from core.ports.text_chunker import TextChunkerPort
from core.ports.embedding_model import EmbeddingModelPort
from core.ports.vector_store import VectorStorePort
from config.settings import ConfigPort


class DocumentProcessingUseCase:
    """Use case for processing documents: loading, chunking, embedding, and storing."""
    
    def __init__(
        self,
        document_loader: DocumentLoaderPort,
        text_chunker: TextChunkerPort,
        embedding_model: EmbeddingModelPort,
        vector_store: VectorStorePort,
        config: ConfigPort
    ):
        self._document_loader = document_loader
        self._text_chunker = text_chunker
        self._embedding_model = embedding_model
        self._vector_store = vector_store
        self._config = config
    
    async def process_document_from_file(
        self, 
        file_path: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a document from file: load, chunk, embed, and store."""
        try:
            # Load document
            document = await self._document_loader.load_from_file(file_path, metadata)
            
            # Process the loaded document
            result = await self._process_document(document)
            
            return {
                "success": True,
                "document_id": document.id,
                "document_title": document.title,
                "chunks_count": result["chunks_count"],
                "embeddings_count": result["embeddings_count"],
                "collection_name": self._config.get_collection_name()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
    
    async def process_document_from_bytes(
        self, 
        content: bytes, 
        filename: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a document from bytes: load, chunk, embed, and store."""
        try:
            # Load document
            document = await self._document_loader.load_from_bytes(content, filename, metadata)
            
            # Process the loaded document
            result = await self._process_document(document)
            
            return {
                "success": True,
                "document_id": document.id,
                "document_title": document.title,
                "chunks_count": result["chunks_count"],
                "embeddings_count": result["embeddings_count"],
                "collection_name": self._config.get_collection_name()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "filename": filename
            }
    
    async def process_multiple_documents(
        self, 
        file_paths: List[str], 
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process multiple documents."""
        results = []
        total_chunks = 0
        total_embeddings = 0
        successful_count = 0
        failed_count = 0
        
        for file_path in file_paths:
            result = await self.process_document_from_file(file_path, metadata)
            results.append(result)
            
            if result["success"]:
                successful_count += 1
                total_chunks += result["chunks_count"]
                total_embeddings += result["embeddings_count"]
            else:
                failed_count += 1
        
        return {
            "success": failed_count == 0,
            "total_documents": len(file_paths),
            "successful_count": successful_count,
            "failed_count": failed_count,
            "total_chunks": total_chunks,
            "total_embeddings": total_embeddings,
            "results": results,
            "collection_name": self._config.get_collection_name()
        }
    
    async def _process_document(self, document: Document) -> Dict[str, Any]:
        """Internal method to process a single document."""
        # Ensure collection exists
        collection_name = self._config.get_collection_name()
        dimension = self._config.get_vector_dimension()
        
        if not await self._vector_store.collection_exists(collection_name):
            await self._vector_store.create_collection(collection_name, dimension)
        
        # Chunk the document
        chunks = await self._text_chunker.chunk_document(document)
        
        # Generate embeddings for chunks
        embeddings = await self._embedding_model.embed_chunks(chunks)
        
        # Store embeddings in vector store
        await self._vector_store.add_embeddings(embeddings, collection_name)
        
        return {
            "chunks_count": len(chunks),
            "embeddings_count": len(embeddings)
        }
    
    async def delete_document(self, document_id: str) -> Dict[str, Any]:
        """Delete a document and all its embeddings."""
        try:
            collection_name = self._config.get_collection_name()
            success = await self._vector_store.delete_embeddings_by_document(document_id, collection_name)
            
            return {
                "success": success,
                "document_id": document_id,
                "collection_name": collection_name
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "document_id": document_id
            }
    
    async def get_document_info(self, document_id: str) -> Dict[str, Any]:
        """Get information about a document's embeddings."""
        try:
            collection_name = self._config.get_collection_name()
            embeddings = await self._vector_store.get_embeddings_by_document(document_id, collection_name)
            
            return {
                "success": True,
                "document_id": document_id,
                "embeddings_count": len(embeddings),
                "collection_name": collection_name,
                "embeddings": [
                    {
                        "id": emb.id,
                        "chunk_id": emb.chunk_id,
                        "model": emb.model,
                        "dimension": emb.dimension,
                        "created_at": emb.created_at.isoformat()
                    }
                    for emb in embeddings
                ]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "document_id": document_id
            }
    
    async def get_supported_formats(self) -> List[str]:
        """Get list of supported document formats."""
        return self._document_loader.get_supported_formats()
    
    async def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        try:
            collection_name = self._config.get_collection_name()
            
            if not await self._vector_store.collection_exists(collection_name):
                return {
                    "success": True,
                    "collection_exists": False,
                    "total_embeddings": 0,
                    "collection_name": collection_name
                }
            
            total_embeddings = await self._vector_store.count_embeddings(collection_name)
            collection_info = await self._vector_store.get_collection_info(collection_name)
            
            return {
                "success": True,
                "collection_exists": True,
                "total_embeddings": total_embeddings,
                "collection_name": collection_name,
                "collection_info": collection_info,
                "embedding_model": self._embedding_model.get_model_name(),
                "vector_dimension": self._embedding_model.get_dimension(),
                "chunker_type": self._text_chunker.get_chunker_type(),
                "chunk_size": self._text_chunker.get_chunk_size(),
                "chunk_overlap": self._text_chunker.get_chunk_overlap()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
