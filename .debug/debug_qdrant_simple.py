#!/usr/bin/env python3
"""
Simple Qdrant debugging script using scroll only.
"""

import asyncio
from qdrant_client import QdrantClient

async def debug_qdrant_simple():
    print("🔍 QDRANT SIMPLE DEBUG")
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
        
        # 2. Check emails collection using scroll (avoid get_collection)
        collection_name = "emails"
        if any(col.name == collection_name for col in collections.collections):
            print(f"\n2. EMAILS COLLECTION DATA:")
            
            # Use scroll to get points without collection info
            try:
                scroll_result = client.scroll(
                    collection_name=collection_name,
                    limit=10,
                    with_payload=True,
                    with_vectors=False
                )
                
                points = scroll_result[0]
                print(f"   Retrieved {len(points)} points:")
                
                if points:
                    for i, point in enumerate(points):
                        print(f"\n   Point {i+1}:")
                        print(f"     ID: {point.id}")
                        payload = point.payload
                        print(f"     Document ID: {payload.get('document_id', 'N/A')}")
                        print(f"     Chunk ID: {payload.get('chunk_id', 'N/A')}")
                        print(f"     Model: {payload.get('model', 'N/A')}")
                        print(f"     Content: {payload.get('content', 'N/A')[:50]}...")
                        
                        # Check metadata
                        metadata = payload.get('metadata', {})
                        print(f"     Metadata keys: {list(metadata.keys())}")
                        if 'embedding_type' in metadata:
                            print(f"     Embedding type: {metadata['embedding_type']}")
                        if 'sender_name' in metadata:
                            print(f"     Sender: {metadata['sender_name']}")
                        if 'email_id' in metadata:
                            print(f"     Email ID: {metadata['email_id']}")
                else:
                    print("   ❌ No points found in emails collection!")
                    
            except Exception as e:
                print(f"   ❌ Error scrolling collection: {e}")
        else:
            print(f"\n❌ Collection '{collection_name}' not found!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_qdrant_simple())
