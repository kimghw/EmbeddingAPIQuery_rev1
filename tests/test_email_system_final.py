"""
Final comprehensive test for the email system.
Tests the complete pipeline: JSON loading → embedding → storage → retrieval.
"""

import asyncio
import json
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adapters.email.json_email_loader import JsonEmailLoaderAdapter
from core.usecases.email_processing import EmailProcessingUseCase
from core.usecases.email_retrieval import EmailRetrievalUseCase
from adapters.vector_store.qdrant_email_adapter import QdrantEmailVectorStoreAdapter
from adapters.vector_store.simple_retriever import SimpleRetrieverAdapter
from adapters.embedding.openai_embedding import OpenAIEmbeddingAdapter
from config.settings import config


async def test_complete_email_system():
    """Test the complete email system end-to-end."""
    
    print("🧪 Final Email System Test")
    print("=" * 60)
    
    # Step 1: Initialize all components
    print("1️⃣ Initializing components...")
    
    email_loader = JsonEmailLoaderAdapter()
    embedding_model = OpenAIEmbeddingAdapter(config=config)
    
    vector_store = QdrantEmailVectorStoreAdapter(
        host="localhost",
        port=6333,
        vector_dimension=1536,
        distance_metric="cosine"
    )
    
    retriever = SimpleRetrieverAdapter(
        vector_store=vector_store,
        embedding_model=embedding_model
    )
    
    print(f"✅ Components initialized")
    print(f"   - Email Loader: {email_loader.get_loader_type()}")
    print(f"   - Vector Store: {vector_store.get_store_type()}")
    print(f"   - Embedding Model: {embedding_model.get_model_name()}")
    
    # Step 2: Clean up and prepare
    print("\n2️⃣ Preparing test environment...")
    
    collection_name = "emails"
    if await vector_store.collection_exists(collection_name):
        await vector_store.delete_collection(collection_name)
        print(f"✅ Cleaned up existing collection: {collection_name}")
    
    # Step 3: Load sample data
    print("\n3️⃣ Loading sample email data...")
    
    sample_file = "sample_emails.json"
    if not os.path.exists(sample_file):
        print(f"❌ Sample file not found: {sample_file}")
        return False
    
    with open(sample_file, "r", encoding="utf-8") as f:
        sample_data = json.load(f)
    
    email_count = len(sample_data.get("value", []))
    print(f"✅ Loaded {email_count} sample emails")
    
    # Step 4: Process emails
    print("\n4️⃣ Processing emails...")
    
    email_processor = EmailProcessingUseCase(
        email_loader=email_loader,
        embedding_model=embedding_model,
        vector_store=vector_store,
        config=config
    )
    
    processing_result = await email_processor.process_emails_from_json(sample_data)
    
    if not processing_result.get("success"):
        print(f"❌ Email processing failed: {processing_result.get('error')}")
        return False
    
    print(f"✅ Email processing completed")
    print(f"   - Processed emails: {processing_result['processed_count']}")
    print(f"   - Generated embeddings: {processing_result['embedded_count']}")
    
    # Step 5: Test email retrieval
    print("\n5️⃣ Testing email retrieval...")
    
    email_retrieval = EmailRetrievalUseCase(
        retriever=retriever,
        embedding_model=embedding_model,
        vector_store=vector_store,
        config=config
    )
    
    # Test email list
    list_result = await email_retrieval.list_emails(limit=10)
    
    if not list_result.get("success"):
        print(f"❌ Email list failed: {list_result.get('error')}")
        return False
    
    print(f"✅ Email list retrieved")
    print(f"   - Total emails: {list_result.get('total', 0)}")
    print(f"   - Returned emails: {len(list_result.get('emails', []))}")
    
    # Step 6: Test search functionality
    print("\n6️⃣ Testing search functionality...")
    
    search_queries = [
        "maritime safety",
        "PL25008aKRd",
        "IMO"
    ]
    
    for query in search_queries:
        search_result = await email_retrieval.search_emails(
            query_text=query,
            top_k=3,
            search_type="both"
        )
        
        if search_result.get("success"):
            results_count = len(search_result.get("results", []))
            print(f"✅ Search '{query}': {results_count} results")
        else:
            print(f"❌ Search '{query}' failed: {search_result.get('error')}")
    
    # Step 7: Test correspondence thread search
    print("\n7️⃣ Testing correspondence thread search...")
    
    thread_result = await email_retrieval.search_by_correspondence_thread("PL25008aKRd")
    
    if thread_result.get("success"):
        thread_count = len(thread_result.get("emails", []))
        print(f"✅ Thread search: {thread_count} emails found")
        
        if thread_count > 0:
            sample_email = thread_result["emails"][0]
            print(f"   - Sample email: {sample_email.get('subject', 'No subject')[:50]}...")
    else:
        print(f"❌ Thread search failed: {thread_result.get('error')}")
    
    # Step 8: Test sender search
    print("\n8️⃣ Testing sender search...")
    
    sender_result = await email_retrieval.search_by_sender("krsdtp@krs.co.kr")
    
    if sender_result.get("success"):
        sender_count = len(sender_result.get("emails", []))
        print(f"✅ Sender search: {sender_count} emails found")
    else:
        print(f"❌ Sender search failed: {sender_result.get('error')}")
    
    # Step 9: Verify data structure
    print("\n9️⃣ Verifying data structure...")
    
    # Get sample embeddings to verify structure
    embeddings = await vector_store.get_all_embeddings(collection_name, limit=2)
    
    if embeddings:
        print(f"✅ Retrieved {len(embeddings)} sample embeddings")
        
        for i, emb in enumerate(embeddings):
            metadata = emb.metadata
            print(f"   📧 Email {i+1}:")
            print(f"      - ID: {emb.id}")
            print(f"      - Type: {metadata.get('embedding_type', 'N/A')}")
            print(f"      - Sender: {metadata.get('sender_address', 'N/A')}")
            print(f"      - Thread: {metadata.get('correspondence_thread', 'N/A')}")
    else:
        print("❌ No embeddings found for verification")
        return False
    
    # Step 10: Performance statistics
    print("\n🔟 Performance statistics...")
    
    stats_result = await email_processor.get_processing_stats()
    
    if stats_result.get("success"):
        print(f"✅ Statistics retrieved")
        print(f"   - Collection exists: {stats_result.get('collection_exists')}")
        print(f"   - Total embeddings: {stats_result.get('total_embeddings', 0)}")
        print(f"   - Estimated emails: {stats_result.get('estimated_email_count', 0)}")
    else:
        print(f"❌ Statistics failed: {stats_result.get('error')}")
    
    print("\n" + "=" * 60)
    print("🎉 Final email system test completed successfully!")
    
    return True


async def main():
    """Run the final email system test."""
    
    try:
        success = await test_complete_email_system()
        return success
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
