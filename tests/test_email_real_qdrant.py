"""
Test email processing pipeline with real Qdrant vector store.
"""

import asyncio
import json
from adapters.email.json_email_loader import JsonEmailLoaderAdapter
from core.usecases.email_processing import EmailProcessingUseCase
from config.adapter_factory import get_vector_store_adapter, get_embedding_adapter
from config.settings import config


async def test_real_email_processing():
    """Test email processing with real Qdrant."""
    
    print("🚀 Testing Email Processing with Real Qdrant\n")
    print("=" * 60)
    
    # Load sample JSON data
    with open("sample_emails.json", "r", encoding="utf-8") as f:
        sample_data = json.load(f)
    
    print(f"📧 Loaded {len(sample_data['value'])} sample emails")
    
    # Initialize real components
    email_loader = JsonEmailLoaderAdapter()
    embedding_model = get_embedding_adapter(config)
    vector_store = get_vector_store_adapter(config)
    
    print(f"✅ Vector Store: {type(vector_store).__name__}")
    print(f"✅ Embedding Model: {type(embedding_model).__name__}")
    
    # Create use case
    email_processor = EmailProcessingUseCase(
        email_loader=email_loader,
        embedding_model=embedding_model,
        vector_store=vector_store,
        config=config
    )
    
    # Process emails
    print("\n📊 Processing emails to real Qdrant...")
    result = await email_processor.process_emails_from_json(sample_data)
    
    print(f"✅ Processing result: {result['success']}")
    print(f"📧 Processed emails: {result['processed_count']}")
    print(f"🔢 Generated embeddings: {result['embedded_count']}")
    print(f"📁 Collection: {result['collection_name']}")
    
    if result['success']:
        print("\n📋 Processed Email Details:")
        for i, email_info in enumerate(result['emails'], 1):
            print(f"  {i}. {email_info['subject'][:60]}...")
            print(f"     From: {email_info['sender']}")
            print(f"     Thread: {email_info['correspondence_thread']}")
            print(f"     Reply: {email_info['is_reply']}, Forward: {email_info['is_forward']}")
            print(f"     Body length: {email_info['body_length']} chars")
            print()
    
    # Verify collection exists
    print("🔍 Verifying collection in Qdrant...")
    collection_exists = await vector_store.collection_exists("emails")
    print(f"✅ Collection 'emails' exists: {collection_exists}")
    
    if collection_exists:
        count = await vector_store.count_embeddings("emails")
        print(f"✅ Total embeddings in collection: {count}")
        
        # Get collection info
        try:
            info = await vector_store.get_collection_info("emails")
            print(f"✅ Collection info: {info}")
        except Exception as e:
            print(f"⚠️ Could not get collection info: {e}")
    
    return result


async def verify_qdrant_direct():
    """Verify data directly in Qdrant."""
    
    print("\n🔍 Direct Qdrant Verification")
    print("-" * 40)
    
    try:
        from qdrant_client import QdrantClient
        
        # Connect to Qdrant
        qdrant_url = config.get_qdrant_url()
        if qdrant_url.startswith('http://'):
            url_parts = qdrant_url.replace('http://', '').split(':')
            host = url_parts[0]
            port = int(url_parts[1]) if len(url_parts) > 1 else 6333
        else:
            host = 'localhost'
            port = 6333
        
        client = QdrantClient(host=host, port=port)
        
        # List all collections
        collections = client.get_collections()
        print(f"📁 All collections:")
        for collection in collections.collections:
            print(f"  - {collection.name}")
            if collection.name == 'emails':
                count = client.count('emails')
                print(f"    📊 Points: {count.count}")
        
        # Check if emails collection exists
        try:
            info = client.get_collection('emails')
            print(f"✅ emails collection info: {info}")
            
            # Get sample points
            result = client.scroll(
                collection_name='emails',
                limit=3,
                with_payload=True,
                with_vectors=False
            )
            
            points = result[0] if result else []
            print(f"✅ Sample points: {len(points)}")
            
            for i, point in enumerate(points):
                print(f"  Point {i+1}:")
                print(f"    ID: {point.id}")
                print(f"    Email ID: {point.payload.get('email_id', 'N/A')}")
                print(f"    Type: {point.payload.get('embedding_type', 'N/A')}")
                print(f"    Sender: {point.payload.get('sender_address', 'N/A')}")
                print(f"    Thread: {point.payload.get('correspondence_thread', 'N/A')}")
                print()
                
        except Exception as e:
            print(f"❌ emails collection not found: {e}")
            
    except Exception as e:
        print(f"❌ Direct Qdrant verification failed: {e}")


async def main():
    """Run real email processing test."""
    
    try:
        # Test with real Qdrant
        result = await test_real_email_processing()
        
        # Direct verification
        await verify_qdrant_direct()
        
        print("\n" + "=" * 60)
        print("🎉 Real Qdrant email processing test completed!")
        
        return result['success'] if result else False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
