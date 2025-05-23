"""
OpenAI embedding adapter implementation.
"""

from typing import List, Optional, Dict, Any
import asyncio
import openai
from openai import AsyncOpenAI

from core.entities.document import DocumentChunk, Embedding
from core.ports.embedding_model import EmbeddingModelPort
from config.settings import ConfigPort


class OpenAIEmbeddingAdapter(EmbeddingModelPort):
    """OpenAI embedding model adapter."""
    
    def __init__(self, config: ConfigPort):
        """
        Initialize OpenAI embedding adapter.
        
        Args:
            config: Configuration port
        """
        self.config = config
        self.client = AsyncOpenAI(api_key=config.get_openai_api_key())
        self.model_name = config.get_embedding_model()
        self.dimension = config.get_vector_dimension()
        self.max_input_length = 8191  # OpenAI text-embedding-3-small limit
    
    async def embed_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[float]:
        """Generate embedding for a single text."""
        if not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Truncate text if too long
        if len(text) > self.max_input_length:
            text = text[:self.max_input_length]
        
        try:
            response = await self.client.embeddings.create(
                model=self.model_name,
                input=text,
                encoding_format="float"
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate embedding: {str(e)}")
    
    async def embed_texts(self, texts: List[str], metadata: Optional[Dict[str, Any]] = None) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        if not texts:
            return []
        
        # Filter out empty texts and truncate long ones
        processed_texts = []
        for text in texts:
            if text.strip():
                if len(text) > self.max_input_length:
                    text = text[:self.max_input_length]
                processed_texts.append(text)
        
        if not processed_texts:
            return []
        
        try:
            # OpenAI allows batch processing up to 2048 inputs
            batch_size = 100  # Conservative batch size
            all_embeddings = []
            
            for i in range(0, len(processed_texts), batch_size):
                batch = processed_texts[i:i + batch_size]
                
                response = await self.client.embeddings.create(
                    model=self.model_name,
                    input=batch,
                    encoding_format="float"
                )
                
                batch_embeddings = [data.embedding for data in response.data]
                all_embeddings.extend(batch_embeddings)
            
            return all_embeddings
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate embeddings: {str(e)}")
    
    async def embed_chunk(self, chunk: DocumentChunk) -> Embedding:
        """Generate embedding for a document chunk."""
        vector = await self.embed_text(chunk.content)
        
        return Embedding.create(
            document_id=chunk.document_id,
            vector=vector,
            model=self.model_name,
            chunk_id=chunk.id,
            metadata={
                **chunk.metadata,
                "chunk_index": chunk.chunk_index,
                "chunk_length": len(chunk.content),
                "embedding_model": self.model_name
            }
        )
    
    async def embed_chunks(self, chunks: List[DocumentChunk]) -> List[Embedding]:
        """Generate embeddings for multiple document chunks."""
        if not chunks:
            return []
        
        # Extract texts from chunks
        texts = [chunk.content for chunk in chunks]
        
        # Generate embeddings
        vectors = await self.embed_texts(texts)
        
        # Create embedding entities
        embeddings = []
        for chunk, vector in zip(chunks, vectors):
            embedding = Embedding.create(
                document_id=chunk.document_id,
                vector=vector,
                model=self.model_name,
                chunk_id=chunk.id,
                metadata={
                    **chunk.metadata,
                    "chunk_index": chunk.chunk_index,
                    "chunk_length": len(chunk.content),
                    "embedding_model": self.model_name
                }
            )
            embeddings.append(embedding)
        
        return embeddings
    
    async def embed_query(self, query_text: str) -> List[float]:
        """Generate embedding for a query text."""
        return await self.embed_text(query_text)
    
    def get_model_name(self) -> str:
        """Get the name of the embedding model."""
        return self.model_name
    
    def get_dimension(self) -> int:
        """Get the dimension of the embedding vectors."""
        return self.dimension
    
    def get_max_input_length(self) -> int:
        """Get the maximum input length for the model."""
        return self.max_input_length
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Get detailed information about the model."""
        return {
            "model_name": self.model_name,
            "dimension": self.dimension,
            "max_input_length": self.max_input_length,
            "provider": "OpenAI",
            "model_type": "text-embedding",
            "available": await self._check_availability()
        }
    
    def is_available(self) -> bool:
        """Check if the embedding model is available."""
        try:
            # Simple check - we have API key and client is initialized
            return bool(self.config.get_openai_api_key() and self.client)
        except Exception:
            return False
    
    async def _check_availability(self) -> bool:
        """Async check if the model is available."""
        try:
            # Try a simple embedding request
            test_response = await self.client.embeddings.create(
                model=self.model_name,
                input="test",
                encoding_format="float"
            )
            return len(test_response.data) > 0
        except Exception:
            return False


class HuggingFaceEmbeddingAdapter(EmbeddingModelPort):
    """HuggingFace embedding model adapter (placeholder implementation)."""
    
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        """
        Initialize HuggingFace embedding adapter.
        
        Args:
            model_name: Name of the HuggingFace model
        """
        self.model_name = model_name
        self.dimension = 384  # BGE small model dimension
        self.max_input_length = 512
        
        # Note: This is a placeholder. In a real implementation, you would:
        # from sentence_transformers import SentenceTransformer
        # self.model = SentenceTransformer(model_name)
    
    async def embed_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[float]:
        """Generate embedding for a single text."""
        raise NotImplementedError("HuggingFace embedding not implemented yet")
    
    async def embed_texts(self, texts: List[str], metadata: Optional[Dict[str, Any]] = None) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        raise NotImplementedError("HuggingFace embedding not implemented yet")
    
    async def embed_chunk(self, chunk: DocumentChunk) -> Embedding:
        """Generate embedding for a document chunk."""
        raise NotImplementedError("HuggingFace embedding not implemented yet")
    
    async def embed_chunks(self, chunks: List[DocumentChunk]) -> List[Embedding]:
        """Generate embeddings for multiple document chunks."""
        raise NotImplementedError("HuggingFace embedding not implemented yet")
    
    async def embed_query(self, query_text: str) -> List[float]:
        """Generate embedding for a query text."""
        raise NotImplementedError("HuggingFace embedding not implemented yet")
    
    def get_model_name(self) -> str:
        """Get the name of the embedding model."""
        return self.model_name
    
    def get_dimension(self) -> int:
        """Get the dimension of the embedding vectors."""
        return self.dimension
    
    def get_max_input_length(self) -> int:
        """Get the maximum input length for the model."""
        return self.max_input_length
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Get detailed information about the model."""
        return {
            "model_name": self.model_name,
            "dimension": self.dimension,
            "max_input_length": self.max_input_length,
            "provider": "HuggingFace",
            "model_type": "sentence-transformer",
            "available": False,
            "note": "Not implemented yet"
        }
    
    def is_available(self) -> bool:
        """Check if the embedding model is available."""
        return False  # Not implemented yet
