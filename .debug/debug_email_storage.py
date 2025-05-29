"""Debug email storage to check if emails are actually stored."""

import asyncio
import os
from config.adapter_factory import get_vector_store

async def debug_storage():
    # Show current configuration
    print(f"VECTOR_STORE_TYPE: {os.getenv('VECTOR_STORE_TYPE', 'default: qdrant')}")
    print(f"ENVIRONMENT: {os.getenv('ENVIRONMENT', 'default: development')}")
    print()
    
    # Get vector store
    vector_store = await anext(get_vector_store())
    print(f"Vector store type: {vector_store.get_store_type()}")
    
    print("=== DEBUG EMAIL STORAGE ===")
    
    # Check if emails collection exists
    exists = await vector_store.collection_exists("emails")
    print(f"1. Emails collection exists: {exists}")
    
    if exists:
        # Count embeddings
        count = await vector_store.count_embeddings("emails")
        print(f"2. Total embeddings in emails collection: {count}")
        
        # Get all embeddings
        all_embeddings = await vector_store.get_all_embeddings("emails")
        print(f"3. Retrieved embeddings: {len(all_embeddings)}")
        
        # Show first few embeddings
        print("\n4. First few embeddings:")
        for i, emb in enumerate(all_embeddings[:5]):
            print(f"   - ID: {emb.id}")
            print(f"     Document ID: {emb.document_id}")
            print(f"     Metadata: {emb.metadata}")
            print()
    
    # Check MockVectorStore internal state
    if hasattr(vector_store, 'collections'):
        print("\n5. MockVectorStore collections:")
        for name, info in vector_store.collections.items():
            print(f"   - {name}: {info}")
        
        print("\n6. MockVectorStore embeddings count per collection:")
        for name, embeddings in vector_store.embeddings.items():
            print(f"   - {name}: {len(embeddings)} embeddings")

if __name__ == "__main__":
    asyncio.run(debug_storage())
