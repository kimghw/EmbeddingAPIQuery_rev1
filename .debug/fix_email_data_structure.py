"""
Fix email data structure in Qdrant - flatten metadata fields to top level.
"""

import asyncio
import json
from qdrant_client import QdrantClient
from adapters.email.json_email_loader import JsonEmailLoaderAdapter
from core.usecases.email_processing import EmailProcessingUseCase
from config.adapter_factory import get_vector_store_adapter, get_embedding_adapter
from config.settings import config


async def fix_email_data_structure():
    """Fix email data structure by recreating with flattened metadata."""
    
    print("🔧 Fixing Email Data Structure in Qdrant\n")
    print("=" * 60)
    
    # Initialize components
    vector_store = get_vector_store_adapter(config)
    
    # Step 1: Delete existing emails collection
    print("1️⃣ Deleting existing emails collection...")
    try:
        if await vector_store.collection_exists("emails"):
            success = await vector_store.delete_collection("emails")
            print(f"✅ Deleted emails collection: {success}")
        else:
            print("✅ No existing emails collection found")
    except Exception as e:
        print(f"⚠️ Error deleting collection: {e}")
    
    # Step 2: Load sample data
    print("\n2️⃣ Loading sample email data...")
    with open("sample_emails.json", "r", encoding="utf-8") as f:
        sample_data = json.load(f)
    
    print(f"✅ Loaded {len(sample_data['value'])} sample emails")
    
    # Step 3: Process emails with corrected structure
    print("\n3️⃣ Processing emails with corrected structure...")
    
    email_loader = JsonEmailLoaderAdapter()
    embedding_model = get_embedding_adapter(config)
    
    # Create custom email processor with fixed metadata handling
    email_processor = EmailProcessingUseCase(
        email_loader=email_loader,
        embedding_model=embedding_model,
        vector_store=vector_store,
        config=config
    )
    
    # Process emails
    result = await email_processor.process_emails_from_json(sample_data)
    
    print(f"✅ Processing result: {result['success']}")
    print(f"📧 Processed emails: {result['processed_count']}")
    print(f"🔢 Generated embeddings: {result['embedded_count']}")
    
    # Step 4: Verify the fix
    print("\n4️⃣ Verifying fixed data structure...")
    
    # Get sample embeddings to check structure
    embeddings = await vector_store.get_all_embeddings("emails", limit=3)
    
    if embeddings:
        print(f"✅ Retrieved {len(embeddings)} sample embeddings")
        
        for i, emb in enumerate(embeddings):
            print(f"\n📧 Email {i+1}:")
            print(f"   ID: {emb.id}")
            print(f"   Document ID: {emb.document_id}")
            
            # Check if email fields are accessible
            metadata = emb.metadata
            print(f"   Email ID: {metadata.get('email_id', 'N/A')}")
            print(f"   Embedding Type: {metadata.get('embedding_type', 'N/A')}")
            print(f"   Sender: {metadata.get('sender_address', 'N/A')}")
            print(f"   Subject: {metadata.get('subject', 'N/A')[:50]}...")
            print(f"   Thread: {metadata.get('correspondence_thread', 'N/A')}")
    
    # Step 5: Direct Qdrant verification
    print("\n5️⃣ Direct Qdrant verification...")
    
    try:
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
            print(f"\n🔍 Point {i+1} payload keys:")
            payload_keys = list(point.payload.keys())
            print(f"   Keys: {payload_keys}")
            
            # Check for email-specific fields at top level
            email_fields = ['email_id', 'embedding_type', 'sender_address', 'correspondence_thread']
            for field in email_fields:
                value = point.payload.get(field, 'N/A')
                print(f"   {field}: {value}")
                
    except Exception as e:
        print(f"❌ Direct verification failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Email data structure fix completed!")
    
    return result


async def main():
    """Run the email data structure fix."""
    
    try:
        result = await fix_email_data_structure()
        return result['success'] if result else False
        
    except Exception as e:
        print(f"❌ Fix failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
