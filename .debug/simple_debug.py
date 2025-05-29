"""Simple debug script to check email storage."""

import asyncio
import os

# Set environment variable
os.environ['VECTOR_STORE_TYPE'] = 'mock'

async def main():
    try:
        print("Starting debug...")
        
        # Import after setting env var
        from config.adapter_factory import get_vector_store
        
        # Get vector store
        vector_store = await anext(get_vector_store())
        print(f"Vector store type: {vector_store.get_store_type()}")
        
        # Check collections
        exists = await vector_store.collection_exists("emails")
        print(f"Emails collection exists: {exists}")
        
        if exists:
            count = await vector_store.count_embeddings("emails")
            print(f"Total embeddings: {count}")
            
            # Get all embeddings
            embeddings = await vector_store.get_all_embeddings("emails")
            print(f"Retrieved {len(embeddings)} embeddings")
            
            # Show internal state for MockVectorStore
            if hasattr(vector_store, 'collections'):
                print("\nMockVectorStore state:")
                print(f"Collections: {list(vector_store.collections.keys())}")
                for name, embs in vector_store.embeddings.items():
                    print(f"  {name}: {len(embs)} embeddings")
                    # Show first embedding
                    if embs:
                        first_id = list(embs.keys())[0]
                        first_emb = embs[first_id]
                        print(f"    First embedding ID: {first_id}")
                        print(f"    Document ID: {first_emb.document_id}")
                        print(f"    Metadata keys: {list(first_emb.metadata.keys())}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
