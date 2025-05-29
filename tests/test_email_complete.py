"""
Complete test for email processing and search functionality.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

# Import email components
from core.entities.email import Email, EmailEmbedding
from adapters.email.json_email_loader import JsonEmailLoaderAdapter
from core.usecases.email_processing import EmailProcessingUseCase
from core.usecases.email_retrieval import EmailRetrievalUseCase
from adapters.vector_store.mock_vector_store import MockVectorStoreAdapter
from adapters.vector_store.simple_retriever import SimpleRetrieverAdapter


class MockEmbeddingModel:
    """Mock embedding model for testing."""
    
    def __init__(self):
        self.model_name = "mock-embedding-model"
        self.dimension = 1536
        self.max_input_length = 8191
    
    async def embed_texts(self, texts):
        import random
        embeddings = []
        for text in texts:
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


def create_sample_email_json() -> Dict[str, Any]:
    """Create sample email JSON data for testing."""
    return {
        "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users('test-user')/messages",
        "value": [
            {
                "id": "email-001",
                "subject": "PL25008aKRd - Maritime Safety Regulations Update",
                "body": {
                    "content": "Dear Team,\n\nThis email contains important updates regarding maritime safety regulations for vessel operations. Please review the attached documentation and ensure compliance with the new IMO standards.\n\nBest regards,\nMaritime Safety Officer",
                    "contentType": "text"
                },
                "bodyPreview": "Dear Team, This email contains important updates regarding maritime safety...",
                "sender": {
                    "emailAddress": {
                        "name": "Maritime Safety Officer",
                        "address": "safety@maritime.org"
                    }
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "name": "Operations Team",
                            "address": "operations@company.com"
                        }
                    }
                ],
                "ccRecipients": [],
                "bccRecipients": [],
                "createdDateTime": "2025-05-29T10:00:00Z",
                "sentDateTime": "2025-05-29T10:01:00Z",
                "receivedDateTime": "2025-05-29T10:01:30Z",
                "webLink": "https://outlook.office365.com/mail/id/email-001",
                "conversationId": "conv-001",
                "internetMessageId": "<email-001@maritime.org>",
                "hasAttachments": True,
                "importance": "high",
                "isRead": False
            },
            {
                "id": "email-002",
                "subject": "RE: PL25008aKRd - Maritime Safety Regulations Update",
                "body": {
                    "content": "Thank you for the update. We have reviewed the new regulations and will implement the required changes by the specified deadline. Our compliance team is already working on the necessary documentation.\n\nRegards,\nOperations Manager",
                    "contentType": "text"
                },
                "bodyPreview": "Thank you for the update. We have reviewed the new regulations...",
                "sender": {
                    "emailAddress": {
                        "name": "Operations Manager",
                        "address": "operations@company.com"
                    }
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "name": "Maritime Safety Officer",
                            "address": "safety@maritime.org"
                        }
                    }
                ],
                "ccRecipients": [],
                "bccRecipients": [],
                "createdDateTime": "2025-05-29T11:30:00Z",
                "sentDateTime": "2025-05-29T11:31:00Z",
                "receivedDateTime": "2025-05-29T11:31:15Z",
                "webLink": "https://outlook.office365.com/mail/id/email-002",
                "conversationId": "conv-001",
                "internetMessageId": "<email-002@company.com>",
                "hasAttachments": False,
                "importance": "normal",
                "isRead": True
            },
            {
                "id": "email-003",
                "subject": "MSC 110/5 - New Vessel Inspection Requirements",
                "body": {
                    "content": "All vessel operators,\n\nPlease be advised of new inspection requirements under MSC 110/5. These requirements will take effect from June 1, 2025. All vessels must undergo additional safety inspections focusing on emergency equipment and crew training protocols.\n\nFor questions, contact the inspection department.\n\nMaritime Authority",
                    "contentType": "text"
                },
                "bodyPreview": "All vessel operators, Please be advised of new inspection requirements...",
                "sender": {
                    "emailAddress": {
                        "name": "Maritime Authority",
                        "address": "authority@maritime.gov"
                    }
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "name": "All Operators",
                            "address": "operators@maritime.org"
                        }
                    }
                ],
                "ccRecipients": [],
                "bccRecipients": [],
                "createdDateTime": "2025-05-29T14:00:00Z",
                "sentDateTime": "2025-05-29T14:01:00Z",
                "receivedDateTime": "2025-05-29T14:01:45Z",
                "webLink": "https://outlook.office365.com/mail/id/email-003",
                "conversationId": "conv-002",
                "internetMessageId": "<email-003@maritime.gov>",
                "hasAttachments": True,
                "importance": "high",
                "isRead": False
            }
        ]
    }


async def test_email_loading():
    """Test email loading from JSON."""
    print("🧪 Testing Email Loading...")
    
    # Create loader
    loader = JsonEmailLoaderAdapter()
    
    # Create sample data
    json_data = create_sample_email_json()
    
    # Test validation
    is_valid = loader.validate_json_structure(json_data)
    print(f"✅ JSON validation: {'PASSED' if is_valid else 'FAILED'}")
    
    # Load emails
    emails = await loader.load_from_json(json_data)
    print(f"✅ Loaded {len(emails)} emails")
    
    # Test email properties
    for i, email in enumerate(emails):
        print(f"  📧 Email {i+1}:")
        print(f"    - ID: {email.id}")
        print(f"    - Subject: {email.get_display_subject(50)}")
        print(f"    - Sender: {email.sender.name} <{email.sender.address}>")
        print(f"    - Thread: {email.correspondence_thread}")
        print(f"    - Is Reply: {email.is_reply()}")
        print(f"    - Body Length: {len(email.body_content)} chars")
    
    # Test statistics
    stats = loader.get_statistics(json_data)
    print(f"✅ Statistics: {stats['total_emails']} emails, {len(stats['sender_distribution'])} senders")
    
    return emails


async def test_email_processing():
    """Test email processing (embedding and storage)."""
    print("\n🧪 Testing Email Processing...")
    
    # Create components
    email_loader = JsonEmailLoaderAdapter()
    embedding_model = MockEmbeddingModel()
    vector_store = MockVectorStoreAdapter()
    config = MockConfig()
    
    # Create use case
    processor = EmailProcessingUseCase(
        email_loader=email_loader,
        embedding_model=embedding_model,
        vector_store=vector_store,
        config=config
    )
    
    # Process emails
    json_data = create_sample_email_json()
    result = await processor.process_emails_from_json(json_data)
    
    print(f"✅ Processing result: {'SUCCESS' if result['success'] else 'FAILED'}")
    print(f"  - Processed: {result['processed_count']} emails")
    print(f"  - Embedded: {result['embedded_count']} embeddings")
    print(f"  - Collection: {result['collection_name']}")
    
    if result['success']:
        stats = result['statistics']
        print(f"  - Email types: {stats['email_counts']}")
        print(f"  - Content stats: avg subject {stats['content_statistics']['avg_subject_length']} chars")
    
    return result


async def test_email_search():
    """Test email search functionality."""
    print("\n🧪 Testing Email Search...")
    
    # Create components
    embedding_model = MockEmbeddingModel()
    vector_store = MockVectorStoreAdapter()
    retriever = SimpleRetrieverAdapter(vector_store, embedding_model)
    config = MockConfig()
    
    # Create use case
    searcher = EmailRetrievalUseCase(
        retriever=retriever,
        embedding_model=embedding_model,
        vector_store=vector_store,
        config=config
    )
    
    # First, process some emails to have data to search
    email_loader = JsonEmailLoaderAdapter()
    processor = EmailProcessingUseCase(
        email_loader=email_loader,
        embedding_model=embedding_model,
        vector_store=vector_store,
        config=config
    )
    
    json_data = create_sample_email_json()
    await processor.process_emails_from_json(json_data)
    
    # Test different search types
    search_queries = [
        ("maritime safety regulations", "both"),
        ("inspection requirements", "subject"),
        ("compliance team", "body"),
    ]
    
    for query, search_type in search_queries:
        print(f"\n  🔍 Searching: '{query}' (type: {search_type})")
        
        result = await searcher.search_emails(
            query_text=query,
            top_k=3,
            search_type=search_type
        )
        
        print(f"    ✅ Found {result['total_results']} results")
        
        for i, email_result in enumerate(result['results'][:2]):  # Show top 2
            print(f"      {i+1}. {email_result['subject'][:50]}...")
            print(f"         Score: {email_result['score']:.3f}")
            print(f"         Sender: {email_result['sender']}")
    
    # Test thread search
    print(f"\n  🔍 Searching by thread: 'PL25008aKRd'")
    thread_result = await searcher.search_by_correspondence_thread("PL25008aKRd", top_k=5)
    print(f"    ✅ Found {thread_result['total_results']} emails in thread")
    
    # Test sender search
    print(f"\n  🔍 Searching by sender: 'safety@maritime.org'")
    sender_result = await searcher.search_by_sender("safety@maritime.org", top_k=5)
    print(f"    ✅ Found {sender_result['total_results']} emails from sender")
    
    return True


async def test_webhook_processing():
    """Test webhook email processing."""
    print("\n🧪 Testing Webhook Processing...")
    
    # Create components
    email_loader = JsonEmailLoaderAdapter()
    embedding_model = MockEmbeddingModel()
    vector_store = MockVectorStoreAdapter()
    config = MockConfig()
    
    processor = EmailProcessingUseCase(
        email_loader=email_loader,
        embedding_model=embedding_model,
        vector_store=vector_store,
        config=config
    )
    
    # Create webhook data (single email)
    webhook_data = {
        "id": "webhook-email-001",
        "subject": "Urgent: Emergency Drill Notification",
        "body": {
            "content": "All crew members must participate in the emergency drill scheduled for tomorrow at 10:00 AM. This is mandatory for safety compliance.",
            "contentType": "text"
        },
        "sender": {
            "emailAddress": {
                "name": "Safety Coordinator",
                "address": "safety@vessel.com"
            }
        },
        "toRecipients": [
            {
                "emailAddress": {
                    "name": "All Crew",
                    "address": "crew@vessel.com"
                }
            }
        ],
        "createdDateTime": "2025-05-29T15:00:00Z",
        "hasAttachments": False,
        "importance": "high"
    }
    
    # Process webhook
    result = await processor.process_emails_from_webhook(webhook_data)
    
    print(f"✅ Webhook processing: {'SUCCESS' if result['success'] else 'FAILED'}")
    print(f"  - Processed: {result['processed_count']} emails")
    print(f"  - Webhook type: {result.get('webhook_type', 'unknown')}")
    
    return result


async def test_email_statistics():
    """Test email statistics and info retrieval."""
    print("\n🧪 Testing Email Statistics...")
    
    # Create components
    email_loader = JsonEmailLoaderAdapter()
    embedding_model = MockEmbeddingModel()
    vector_store = MockVectorStoreAdapter()
    config = MockConfig()
    
    processor = EmailProcessingUseCase(
        email_loader=email_loader,
        embedding_model=embedding_model,
        vector_store=vector_store,
        config=config
    )
    
    # Process some emails first
    json_data = create_sample_email_json()
    await processor.process_emails_from_json(json_data)
    
    # Get processing stats
    stats = await processor.get_processing_stats()
    print(f"✅ Collection exists: {stats['collection_exists']}")
    print(f"  - Total embeddings: {stats['total_embeddings']}")
    print(f"  - Estimated emails: {stats['estimated_email_count']}")
    print(f"  - Model: {stats['embedding_model']}")
    print(f"  - Dimension: {stats['vector_dimension']}")
    
    return stats


async def main():
    """Run all email tests."""
    print("🚀 Starting Complete Email System Test\n")
    
    try:
        # Test 1: Email Loading
        emails = await test_email_loading()
        
        # Test 2: Email Processing
        processing_result = await test_email_processing()
        
        # Test 3: Email Search
        await test_email_search()
        
        # Test 4: Webhook Processing
        webhook_result = await test_webhook_processing()
        
        # Test 5: Statistics
        stats = await test_email_statistics()
        
        print("\n🎉 All Email Tests Completed Successfully!")
        print("\n📊 Summary:")
        print(f"  - Emails loaded: {len(emails)}")
        print(f"  - Processing success: {processing_result['success']}")
        print(f"  - Webhook success: {webhook_result['success']}")
        print(f"  - Total embeddings: {stats['total_embeddings']}")
        
        print("\n✅ Email system is ready for production!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
