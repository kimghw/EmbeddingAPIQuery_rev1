"""
Test email system with fixed data structure using the new email-optimized adapter.
"""

import asyncio
import json
from adapters.email.json_email_loader import JsonEmailLoaderAdapter
from core.usecases.email_processing import EmailProcessingUseCase
from adapters.vector_store.qdrant_email_adapter import QdrantEmailVectorStoreAdapter
from adapters.embedding.openai_embedding import OpenAIEmbeddingAdapter
from config.settings import config


async def test_email_fixed_structure():
    """Test email processing with fixed data structure."""
    
    print("🧪 Testing Email System with Fixed Data Structure\n")
    print("=" * 60)
    
    # Step 1: Initialize components with email-optimized adapter
    print("1️⃣ Initializing components...")
    
    email_loader = JsonEmailLoaderAdapter()
    embedding_model = OpenAIEmbeddingAdapter(config=config)
    
    # Use the new email-optimized Qdrant adapter
    vector_store = QdrantEmailVectorStoreAdapter(
        host="localhost",
        port=6333,
        vector_dimension=1536,
        distance_metric="cosine"
    )
    
    print(f"✅ Vector store type: {vector_store.get_store_type()}")
    
    # Step 2: Delete existing collection and recreate
    print("\n2️⃣ Cleaning up existing data...")
    
    if await vector_store.collection_exists("emails"):
        success = await vector_store.delete_collection("emails")
        print(f"✅ Deleted existing collection: {success}")
    
    # Step 3: Load and process sample emails
    print("\n3️⃣ Loading sample email data...")
    
    with open("sample_emails.json", "r", encoding="utf-8") as f:
        sample_data = json.load(f)
    
    print(f"✅ Loaded {len(sample_data['value'])} sample emails")
    
    # Step 4: Process emails with new adapter
    print("\n4️⃣ Processing emails with fixed structure...")
    
    email_processor = EmailProcessingUseCase(
        email_loader=email_loader,
        embedding_model=embedding_model,
        vector_store=vector_store,
        config=config
    )
    
    result = await email_processor.process_emails_from_json(sample_data)
    
    print(f"✅ Processing result: {result['success']}")
    print(f"📧 Processed emails: {result['processed_count']}")
    print(f"🔢 Generated embeddings: {result['embedded_count']}")
    
    # Step 5: Verify the fixed structure
    print("\n5️⃣ Verifying fixed data structure...")
    
    # Get sample embeddings to check structure
    embeddings = await vector_store.get_all_embeddings("emails", limit=3)
    
    if embeddings:
        print(f"✅ Retrieved {len(embeddings)} sample embeddings")
        
        for i, emb in enumerate(embeddings):
            print(f"\n📧 Email {i+1}:")
            print(f"   ID: {emb.id}")
            print(f"   Document ID: {emb.document_id}")
            
            # Check if email fields are accessible at top level
            metadata = emb.metadata
            print(f"   Email ID: {metadata.get('email_id', 'N/A')}")
            print(f"   Embedding Type: {metadata.get('embedding_type', 'N/A')}")
            print(f"   Sender: {metadata.get('sender_address', 'N/A')}")
            print(f"   Subject: {metadata.get('subject', 'N/A')[:50]}...")
            print(f"   Thread: {metadata.get('correspondence_thread', 'N/A')}")
            print(f"   Created Time: {metadata.get('created_time', 'N/A')}")
    
    # Step 6: Direct Qdrant verification
    print("\n6️⃣ Direct Qdrant verification...")
    
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(host='localhost', port=6333)
        
        # Get sample points directly
        result = client.scroll(
            collection_name='emails',
            limit=2,
            with_payload=True,
            with_vectors=False
        )
        
        points = result[0] if result else []
        print(f"✅ Direct Qdrant check: {len(points)} points")
        
        for i, point in enumerate(points):
            print(f"\n🔍 Point {i+1} payload structure:")
            payload_keys = list(point.payload.keys())
            print(f"   Total keys: {len(payload_keys)}")
            print(f"   Keys: {payload_keys}")
            
            # Check for email-specific fields at top level
            email_fields = ['email_id', 'embedding_type', 'sender_address', 'correspondence_thread']
            print(f"   Email fields at top level:")
            for field in email_fields:
                value = point.payload.get(field, 'N/A')
                print(f"     {field}: {value}")
                
    except Exception as e:
        print(f"❌ Direct verification failed: {e}")
    
    # Step 7: Test email list API
    print("\n7️⃣ Testing email list functionality...")
    
    try:
        from core.usecases.email_retrieval import EmailRetrievalUseCase
        
        from adapters.vector_store.simple_retriever import SimpleRetrieverAdapter
        
        # Create retriever
        retriever = SimpleRetrieverAdapter(
            vector_store=vector_store,
            embedding_model=embedding_model
        )
        
        email_retrieval = EmailRetrievalUseCase(
            retriever=retriever,
            embedding_model=embedding_model,
            vector_store=vector_store,
            config=config
        )
        
        # Get email list
        email_list = await email_retrieval.list_emails(limit=5)
        
        print(f"✅ Email list result: {email_list['success']}")
        print(f"📧 Total emails found: {email_list.get('total', 0)}")
        print(f"📋 Returned emails: {len(email_list['emails'])}")
        
        if email_list['emails']:
            print(f"\n📧 Sample email from list:")
            sample_email = email_list['emails'][0]
            for key, value in sample_email.items():
                if isinstance(value, str) and len(value) > 50:
                    value = value[:50] + "..."
                print(f"   {key}: {value}")
                
    except Exception as e:
        print(f"❌ Email list test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🎉 Email system test with fixed structure completed!")
    
    return result


async def main():
    """Run the email system test."""
    
    try:
        result = await test_email_fixed_structure()
        # Handle both dict and other return types safely
        if isinstance(result, dict):
            return result.get('success', False)
        else:
            return bool(result)
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
