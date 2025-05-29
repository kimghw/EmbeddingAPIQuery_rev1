#!/usr/bin/env python3
"""
Direct Qdrant debugging script to check what's actually stored.
"""

import asyncio
from qdrant_client import QdrantClient
from config.adapter_factory import get_vector_store
from adapters.vector_store.qdrant_vector_store import QdrantVectorStoreAdapter

async def debug_qdrant():
    print("🔍 QDRANT DIRECT DEBUG")
    print("=" * 50)
    
    # Initialize Qdrant client directly
    client = QdrantClient(host="localhost", port=6333)
    
    try:
        # 1. List all collections
        print("\n1. COLLECTIONS:")
        collections = client.get_collections()
        print(f"   Found {len(collections.collections)} collections:")
        for col in collections.collections:
            print(f"   - {col.name}")
        
        # 2. Check emails collection specifically
        collection_name = "emails"
        if any(col.name == collection_name for col in collections.collections):
            print(f"\n2. EMAILS COLLECTION INFO:")
            collection_info = client.get_collection(collection_name)
            print(f"   Points count: {collection_info.points_count}")
            print(f"   Vector size: {collection_info.config.params.vectors.size}")
            print(f"   Distance: {collection_info.config.params.vectors.distance}")
            
            # 3. Get some sample points
            print(f"\n3. SAMPLE POINTS:")
            scroll_result = client.scroll(
                collection_name=collection_name,
                limit=5,
                with_payload=True,
                with_vectors=False  # Don't need vectors for debugging
            )
            
            points = scroll_result[0]
            print(f"   Retrieved {len(points)} points:")
            
            for i, point in enumerate(points):
                print(f"\n   Point {i+1}:")
                print(f"     ID: {point.id}")
                payload = point.payload
                print(f"     Document ID: {payload.get('document_id', 'N/A')}")
                print(f"     Chunk ID: {payload.get('chunk_id', 'N/A')}")
                print(f"     Model: {payload.get('model', 'N/A')}")
                print(f"     Content preview: {payload.get('content', 'N/A')[:100]}...")
                
                # Check metadata structure
                metadata = payload.get('metadata', {})
                print(f"     Metadata keys: {list(metadata.keys())}")
                print(f"     Email ID: {metadata.get('email_id', 'N/A')}")
                print(f"     Embedding type: {metadata.get('embedding_type', 'N/A')}")
                print(f"     Sender: {metadata.get('sender_name', 'N/A')} <{metadata.get('sender_address', 'N/A')}>")
        else:
            print(f"\n❌ Collection '{collection_name}' not found!")
        
        # 4. Test our adapter
        print(f"\n4. TESTING ADAPTER:")
        vector_store = await get_vector_store()
        print(f"   Vector store type: {vector_store.get_store_type()}")
        
        if await vector_store.collection_exists(collection_name):
            print(f"   ✅ Collection exists via adapter")
            
            # Test get_all_embeddings
            embeddings = await vector_store.get_all_embeddings(collection_name, limit=5)
            print(f"   Retrieved {len(embeddings)} embeddings via adapter")
            
            for i, emb in enumerate(embeddings):
                print(f"\n   Embedding {i+1}:")
                print(f"     ID: {emb.id}")
                print(f"     Document ID: {emb.document_id}")
                print(f"     Chunk ID: {emb.chunk_id}")
                print(f"     Model: {emb.model}")
                print(f"     Metadata keys: {list(emb.metadata.keys())}")
                print(f"     Email ID: {emb.metadata.get('email_id', 'N/A')}")
                print(f"     Embedding type: {emb.metadata.get('embedding_type', 'N/A')}")
                print(f"     Content: {emb.metadata.get('content', 'N/A')[:50]}...")
        else:
            print(f"   ❌ Collection not found via adapter")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_qdrant())
