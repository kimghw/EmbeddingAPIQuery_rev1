#!/usr/bin/env python3
"""
Check Qdrant data directly.
"""

from qdrant_client import QdrantClient

def check_qdrant():
    print("🔍 CHECKING QDRANT DATA")
    print("=" * 50)
    
    client = QdrantClient(host="localhost", port=6333)
    
    # 1. List collections
    print("\n1. Collections:")
    try:
        collections = client.get_collections()
        for col in collections.collections:
            print(f"   - {col.name}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # 2. Check emails collection
    print("\n2. Emails Collection:")
    try:
        # Use scroll to count points
        result = client.scroll(
            collection_name="emails",
            limit=100,
            with_payload=True,
            with_vectors=False
        )
        
        points = result[0] if result else []
        print(f"   Total points: {len(points)}")
        
        if points:
            print("\n   Sample points:")
            for i, point in enumerate(points[:3]):
                print(f"\n   Point {i+1}:")
                print(f"     ID: {point.id}")
                payload = point.payload
                print(f"     Document ID: {payload.get('document_id')}")
                print(f"     Chunk ID: {payload.get('chunk_id')}")
                print(f"     Content preview: {payload.get('content', '')[:100]}...")
                
                # Check metadata structure
                metadata = payload.get('metadata', {})
                print(f"     Metadata keys: {list(metadata.keys())}")
                
                # Check email-specific fields
                if 'email_id' in metadata:
                    print(f"     Email ID: {metadata.get('email_id')}")
                if 'embedding_type' in metadata:
                    print(f"     Embedding type: {metadata.get('embedding_type')}")
                if 'subject' in metadata:
                    print(f"     Subject: {metadata.get('subject')}")
                    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_qdrant()
