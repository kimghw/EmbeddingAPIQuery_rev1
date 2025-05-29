#!/usr/bin/env python3
"""
Debug email count issue.
"""

import asyncio
from qdrant_client import QdrantClient

async def check_email_count():
    print("🔍 CHECKING EMAIL COUNT")
    print("=" * 50)
    
    client = QdrantClient(host="localhost", port=6333)
    
    # Method 1: Using scroll to count
    print("\n1. Count using scroll:")
    try:
        count = 0
        offset = 0
        batch_size = 100
        
        while True:
            result = client.scroll(
                collection_name="emails",
                limit=batch_size,
                offset=offset,
                with_payload=False,
                with_vectors=False
            )
            
            points = result[0] if result else []
            count += len(points)
            
            if len(points) < batch_size:
                break
                
            offset += batch_size
        
        print(f"   Total points: {count}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Method 2: Get unique email IDs
    print("\n2. Unique email IDs:")
    try:
        result = client.scroll(
            collection_name="emails",
            limit=1000,
            with_payload=True,
            with_vectors=False
        )
        
        points = result[0] if result else []
        email_ids = set()
        
        for point in points:
            email_id = point.payload.get("metadata", {}).get("email_id")
            if email_id:
                email_ids.add(email_id)
        
        print(f"   Unique emails: {len(email_ids)}")
        print(f"   Total embeddings: {len(points)}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Method 3: Try get_collection (might fail due to Pydantic)
    print("\n3. Get collection info:")
    try:
        collection_info = client.get_collection("emails")
        print(f"   Points count: {collection_info.points_count}")
    except Exception as e:
        print(f"   ❌ Error (expected): {type(e).__name__}")

if __name__ == "__main__":
    asyncio.run(check_email_count())
