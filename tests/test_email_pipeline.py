"""
Test email processing pipeline with mock components.
"""

import asyncio
import json
from typing import List, Dict, Any
from adapters.email.json_email_loader import JsonEmailLoaderAdapter
from core.usecases.email_processing import EmailProcessingUseCase
from adapters.vector_store.mock_vector_store import MockVectorStoreAdapter
from adapters.embedding.openai_embedding import OpenAIEmbeddingAdapter
from config.adapter_factory import AdapterFactory


class MockEmbeddingModel:
    """Mock embedding model for testing."""
    
    def __init__(self):
        self.model_name = "mock-embedding-model"
        self.dimension = 1536
        self.max_input_length = 8191
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate mock embeddings."""
        import random
        embeddings = []
        for text in texts:
            # Generate deterministic mock embedding based on text hash
            random.seed(hash(text) % 2**32)
            embedding = [random.uniform(-1, 1) for _ in range(self.dimension)]
            embeddings.append(embedding)
        return embeddings
    
    def get_model_name(self) -> str:
        return self.model_name
    
    def get_dimension(self) -> int:
        return self.dimension
    
    def get_max_input_length(self) -> int:
        return self.max_input_length


class MockConfig:
    """Mock configuration for testing."""
    
    def get_openai_api_key(self) -> str:
        return "mock-api-key"
    
    def get_qdrant_url(self) -> str:
        return "http://localhost:6333"
    
    def get_qdrant_api_key(self) -> str:
        return "mock-qdrant-key"


async def test_email_processing_pipeline():
    """Test the complete email processing pipeline."""
    
    print("🧪 Testing Email Processing Pipeline...\n")
    
    # Load sample JSON data
    with open("sample_emails.json", "r", encoding="utf-8") as f:
        sample_data = json.load(f)
    
    print(f"📧 Loaded {len(sample_data['value'])} sample emails")
    
    # Initialize components
    email_loader = JsonEmailLoaderAdapter()
    embedding_model = MockEmbeddingModel()
    vector_store = MockVectorStoreAdapter()
    config = MockConfig()
    
    # Create use case
    email_processor = EmailProcessingUseCase(
        email_loader=email_loader,
        embedding_model=embedding_model,
        vector_store=vector_store,
        config=config
    )
    
    # Test 1: Process emails from JSON
    print("\n📊 Test 1: Processing emails from JSON...")
    result = await email_processor.process_emails_from_json(sample_data)
    
    print(f"✅ Processing result: {result['success']}")
    print(f"📧 Processed emails: {result['processed_count']}")
    print(f"🔢 Generated embeddings: {result['embedded_count']}")
    print(f"📁 Collection: {result['collection_name']}")
    
    # Display email details
    print("\n📋 Processed Email Details:")
    for i, email_info in enumerate(result['emails'], 1):
        print(f"  {i}. {email_info['subject'][:60]}...")
        print(f"     From: {email_info['sender']}")
        print(f"     Thread: {email_info['correspondence_thread']}")
        print(f"     Reply: {email_info['is_reply']}, Forward: {email_info['is_forward']}")
        print(f"     Body length: {email_info['body_length']} chars")
        print()
    
    # Display statistics
    stats = result['statistics']
    print("📈 Processing Statistics:")
    print(f"  Email counts: {stats['email_counts']}")
    print(f"  Embedding counts: {stats['embedding_counts']}")
    print(f"  Content stats: {stats['content_statistics']}")
    print(f"  Top senders: {list(stats['sender_distribution'].keys())}")
    print(f"  Threads: {list(stats['thread_distribution'].keys())}")
    
    # Test 2: Get processing stats
    print("\n📊 Test 2: Getting processing statistics...")
    processing_stats = await email_processor.get_processing_stats()
    print(f"✅ Stats retrieval: {processing_stats['success']}")
    print(f"📁 Collection exists: {processing_stats['collection_exists']}")
    print(f"🔢 Total embeddings: {processing_stats['total_embeddings']}")
    print(f"📧 Estimated emails: {processing_stats['estimated_email_count']}")
    
    # Test 3: Test webhook processing
    print("\n📊 Test 3: Testing webhook processing...")
    webhook_data = {
        "id": "webhook-test-email",
        "subject": "FW: PL25008aKRd - Forwarded Maritime Safety Update",
        "body": {"content": "Forwarding important maritime safety information...", "contentType": "text"},
        "sender": {"emailAddress": {"name": "Test Forwarder", "address": "forwarder@test.com"}},
        "createdDateTime": "2025-05-29T16:00:00Z",
        "toRecipients": [{"emailAddress": {"name": "Test Recipient", "address": "recipient@test.com"}}],
        "ccRecipients": [],
        "bccRecipients": [],
        "hasAttachments": False,
        "importance": "normal",
        "isRead": False
    }
    
    webhook_result = await email_processor.process_emails_from_webhook(webhook_data)
    print(f"✅ Webhook processing: {webhook_result['success']}")
    print(f"📧 Processed emails: {webhook_result['processed_count']}")
    print(f"🔗 Webhook type: {webhook_result.get('webhook_type', 'unknown')}")
    
    if webhook_result['emails']:
        webhook_email = webhook_result['emails'][0]
        print(f"📧 Webhook email: {webhook_email['subject']}")
        print(f"🔄 Is forward: {webhook_email['is_forward']}")
        print(f"🧵 Thread: {webhook_email['correspondence_thread']}")
    
    # Test 4: Test email info retrieval
    print("\n📊 Test 4: Testing email info retrieval...")
    if result['emails']:
        first_email_id = result['emails'][0]['id']
        email_info = await email_processor.get_email_info(first_email_id)
        print(f"✅ Email info retrieval: {email_info['success']}")
        print(f"🔢 Embeddings for email: {email_info['embeddings_count']}")
        
        if email_info['embeddings']:
            for emb in email_info['embeddings']:
                print(f"  - {emb['type']}: {emb['content_preview']}")
    
    # Test 5: Test multiple JSON files
    print("\n📊 Test 5: Testing multiple JSON files processing...")
    
    # Create a second sample file
    second_sample = {
        "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users('test-user-2')/messages",
        "value": [
            {
                "id": "additional-email-1",
                "subject": "PL25008aKRd - Follow-up Discussion",
                "body": {"content": "Following up on our previous discussion...", "contentType": "text"},
                "sender": {"emailAddress": {"name": "Follow-up Sender", "address": "followup@test.com"}},
                "createdDateTime": "2025-05-29T18:00:00Z",
                "toRecipients": [{"emailAddress": {"name": "Test Recipient", "address": "recipient@test.com"}}],
                "ccRecipients": [],
                "bccRecipients": [],
                "hasAttachments": False,
                "importance": "normal",
                "isRead": False
            }
        ]
    }
    
    multiple_result = await email_processor.process_multiple_json_files([sample_data, second_sample])
    print(f"✅ Multiple files processing: {multiple_result['success']}")
    print(f"📧 Total processed emails: {multiple_result['processed_count']}")
    print(f"📁 Files processed: {multiple_result['files_processed']}")
    
    print("\n🎉 All email processing pipeline tests completed successfully!")
    
    return {
        "json_processing": result,
        "webhook_processing": webhook_result,
        "multiple_files": multiple_result,
        "processing_stats": processing_stats
    }


async def test_email_search_simulation():
    """Simulate email search functionality."""
    
    print("\n🔍 Testing Email Search Simulation...\n")
    
    # Initialize mock vector store with some data
    vector_store = MockVectorStoreAdapter()
    
    # Simulate search queries
    search_queries = [
        "maritime safety regulations",
        "PL25008aKRd correspondence",
        "SOLAS Chapter II-1",
        "emergency response procedures",
        "IMO MSC guidelines"
    ]
    
    print("🔍 Simulating email searches:")
    for query in search_queries:
        print(f"\n  Query: '{query}'")
        
        # Mock search results
        mock_results = [
            {
                "id": f"email_{i}_{query.replace(' ', '_')}",
                "score": 0.95 - (i * 0.1),
                "metadata": {
                    "email_id": f"email_{i}",
                    "embedding_type": "subject" if i % 2 == 0 else "body",
                    "correspondence_thread": "PL25008aKRd" if "PL25008aKRd" in query else "MSC 110/5",
                    "sender_address": "test@example.com",
                    "content": f"Mock content related to {query}..."
                }
            }
            for i in range(3)
        ]
        
        print(f"    Found {len(mock_results)} results:")
        for result in mock_results:
            print(f"      - Score: {result['score']:.2f}, Type: {result['metadata']['embedding_type']}")
            print(f"        Thread: {result['metadata']['correspondence_thread']}")
            print(f"        Content: {result['metadata']['content'][:50]}...")
    
    print("\n✅ Email search simulation completed!")


async def main():
    """Run all email processing tests."""
    
    print("🚀 Starting Email Processing System Tests\n")
    print("=" * 60)
    
    try:
        # Test basic pipeline
        pipeline_results = await test_email_processing_pipeline()
        
        print("\n" + "=" * 60)
        
        # Test search simulation
        await test_email_search_simulation()
        
        print("\n" + "=" * 60)
        print("🎉 All tests completed successfully!")
        
        # Summary
        print("\n📊 Test Summary:")
        print(f"✅ JSON Processing: {pipeline_results['json_processing']['processed_count']} emails")
        print(f"✅ Webhook Processing: {pipeline_results['webhook_processing']['processed_count']} emails")
        print(f"✅ Multiple Files: {pipeline_results['multiple_files']['processed_count']} emails")
        print(f"✅ Total Embeddings: {pipeline_results['processing_stats']['total_embeddings']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
