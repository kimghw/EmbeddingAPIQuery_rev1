#!/usr/bin/env python3
"""
Debug script for email search functionality.
"""

import asyncio
import sys
import traceback
from core.usecases.email_retrieval import EmailRetrievalUseCase
from adapters.vector_store.mock_vector_store import MockVectorStoreAdapter
from adapters.vector_store.simple_retriever import SimpleRetrieverAdapter


class MockEmbeddingModel:
    """Mock embedding model for search."""
    
    def __init__(self):
        self.model_name = "mock-embedding-model"
        self.dimension = 1536
        self.max_input_length = 8191
    
    async def embed_texts(self, texts):
        import random
        embeddings = []
        for text in texts:
            random.seed(hash(text) % 2**32)
            embedding = [random.uniform(-1, 1) for _ in range(self.dimension)]
            embeddings.append(embedding)
        return embeddings
    
    async def embed_text(self, text):
        """Embed single text."""
        embeddings = await self.embed_texts([text])
        return embeddings[0]
    
    def get_model_name(self) -> str:
        return self.model_name
    
    def get_dimension(self) -> int:
        return self.dimension
    
    def get_max_input_length(self) -> int:
        return self.max_input_length


class MockConfig:
    """Mock configuration for search."""
    
    def get_openai_api_key(self) -> str:
        return "mock-api-key"
    
    def get_qdrant_url(self) -> str:
        return "http://localhost:6333"
    
    def get_qdrant_api_key(self) -> str:
        return "mock-qdrant-key"


async def test_email_search():
    """Test email search functionality."""
    try:
        print("🔧 Setting up dependencies...")
        
        # Create dependencies
        embedding_model = MockEmbeddingModel()
        vector_store = MockVectorStoreAdapter()
        retriever = SimpleRetrieverAdapter(vector_store=vector_store, embedding_model=embedding_model)
        config = MockConfig()
        
        print("✅ Dependencies created successfully")
        
        # Create use case
        email_retriever = EmailRetrievalUseCase(
            retriever=retriever,
            embedding_model=embedding_model,
            vector_store=vector_store,
            config=config
        )
        
        print("✅ EmailRetrievalUseCase created successfully")
        
        # Test search
        print("🔍 Testing email search...")
        
        result = await email_retriever.search_emails(
            query_text="maritime safety regulations",
            top_k=5,
            search_type="both",
            filters=None
        )
        
        print("✅ Search completed successfully")
        print(f"📊 Result keys: {list(result.keys())}")
        print(f"📊 Success: {result.get('success')}")
        print(f"📊 Query: {result.get('query')}")
        print(f"📊 Error: {result.get('error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        print(f"📋 Traceback:")
        traceback.print_exc()
        return None


async def main():
    """Main function."""
    print("🚀 Starting email search debug...")
    
    result = await test_email_search()
    
    if result:
        print("\n📋 Final Result:")
        for key, value in result.items():
            if key == "results":
                print(f"  {key}: [{len(value)} items]")
            else:
                print(f"  {key}: {value}")
    else:
        print("\n❌ Test failed")
        sys.exit(1)
    
    print("\n✅ Debug completed successfully")


if __name__ == "__main__":
    asyncio.run(main())
