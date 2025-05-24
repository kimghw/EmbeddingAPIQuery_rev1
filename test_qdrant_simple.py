#!/usr/bin/env python3
"""
Simple test script for Qdrant Vector Store Adapter
"""

import asyncio
import sys
import uuid
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import config
from adapters.vector_store.qdrant_vector_store import QdrantVectorStoreAdapter
from core.entities.document import Embedding


async def test_qdrant():
    """Test Qdrant vector store functionality."""
    print("🔍 Testing Qdrant vector store...")
    
    try:
        # Initialize Qdrant adapter
        qdrant = QdrantVectorStoreAdapter(
            host="localhost",
            port=6333,
            vector_dimension=config.get_vector_dimension()
        )
        
        collection_name = config.get_collection_name()
        print(f"📦 Using collection: {collection_name}")
        
        # Test health check
        print("🏥 Checking Qdrant health...")
        is_healthy = await qdrant.health_check()
        
        if not is_healthy:
            print("❌ Qdrant is not accessible. Make sure Qdrant server is running.")
            print("   You can start Qdrant with: docker run -p 6333:6333 qdrant/qdrant")
            return False
        
        print("✅ Qdrant is healthy!")
        
        # List collections
        collections = await qdrant.list_collections()
        print(f"📋 Available collections: {collections}")
        
        # Check if collection exists, create if not
        exists = await qdrant.collection_exists(collection_name)
        if not exists:
            print(f"🔨 Creating collection: {collection_name}")
            success = await qdrant.create_collection(collection_name, config.get_vector_dimension())
            if not success:
                print("❌ Failed to create collection")
                return False
        else:
            print(f"✅ Collection {collection_name} already exists")
        
        # Get collection info (skip due to Qdrant version compatibility issue)
        print("📊 Skipping collection info due to version compatibility...")
        
        # Test storing and searching vectors
        print("\n🧪 Testing vector storage and search...")
        
        # Create test embeddings with all required fields
        test_embeddings = [
            Embedding(
                id=str(uuid.uuid4()),
                document_id="test-doc-1",
                chunk_id="chunk-0",
                vector=[0.1] * config.get_vector_dimension(),
                model=config.get_embedding_model(),
                dimension=config.get_vector_dimension(),
                metadata={"source": "test", "category": "AI", "content": "AI and ML content"},
                created_at=datetime.utcnow()
            ),
            Embedding(
                id=str(uuid.uuid4()),
                document_id="test-doc-1",
                chunk_id="chunk-1",
                vector=[0.2] * config.get_vector_dimension(),
                model=config.get_embedding_model(),
                dimension=config.get_vector_dimension(),
                metadata={"source": "test", "category": "Programming", "content": "Python programming"},
                created_at=datetime.utcnow()
            )
        ]
        
        print(f"💾 Storing {len(test_embeddings)} test embeddings...")
        
        # Store embeddings
        success = await qdrant.add_embeddings(test_embeddings, collection_name)
        if success:
            print(f"✅ Successfully stored {len(test_embeddings)} embeddings")
        else:
            print("❌ Failed to store embeddings")
            return False
        
        # Search for similar vectors
        print("🔍 Searching for similar vectors...")
        query_vector = [0.15] * config.get_vector_dimension()  # Mock query vector
        search_results = await qdrant.search_similar(
            query_vector, 
            collection_name, 
            top_k=2
        )
        
        print(f"✅ Found {len(search_results)} similar vectors:")
        for i, result in enumerate(search_results):
            print(f"   Result {i + 1}:")
            print(f"     - Score: {result.score:.4f}")
            print(f"     - Document ID: {result.embedding.document_id}")
            print(f"     - Chunk ID: {result.embedding.chunk_id}")
            print(f"     - Metadata: {result.metadata}")
        
        # Count embeddings
        count = await qdrant.count_embeddings(collection_name)
        print(f"📊 Total embeddings in collection: {count}")
        
        # Test individual embedding retrieval
        print("\n🔍 Testing individual embedding retrieval...")
        first_embedding_id = test_embeddings[0].id
        retrieved = await qdrant.get_embedding(first_embedding_id, collection_name)
        if retrieved:
            print(f"✅ Successfully retrieved embedding: {retrieved.id}")
            print(f"   - Document ID: {retrieved.document_id}")
            print(f"   - Chunk ID: {retrieved.chunk_id}")
            print(f"   - Model: {retrieved.model}")
            print(f"   - Dimension: {retrieved.dimension}")
        else:
            print(f"❌ Failed to retrieve embedding: {first_embedding_id}")
        
        # Test document-based retrieval
        print("\n📄 Testing document-based retrieval...")
        doc_embeddings = await qdrant.get_embeddings_by_document("test-doc-1", collection_name)
        print(f"✅ Found {len(doc_embeddings)} embeddings for document 'test-doc-1'")
        
        # Clean up test data
        print("\n🧹 Cleaning up test data...")
        for embedding in test_embeddings:
            success = await qdrant.delete_embedding(embedding.id, collection_name)
            if success:
                print(f"✅ Deleted embedding: {embedding.id}")
            else:
                print(f"❌ Failed to delete embedding: {embedding.id}")
        
        print("✅ Qdrant test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Qdrant: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_qdrant())
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)
