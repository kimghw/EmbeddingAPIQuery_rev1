"""
Test email processing API endpoints.
"""

import asyncio
import json
import aiohttp
from typing import Dict, Any
import time


class EmailAPITester:
    """Test client for email processing API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_health_check(self):
        """Test email health check endpoint."""
        print("🔍 Testing email health check...")
        
        try:
            async with self.session.get(f"{self.base_url}/emails/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health check passed")
                    print(f"   Status: {data['status']}")
                    print(f"   Components: {data['components']}")
                    print(f"   Version: {data['version']}")
                    return True
                else:
                    print(f"❌ Health check failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    async def test_validate_json(self, sample_data: Dict[str, Any]):
        """Test JSON validation endpoint."""
        print("\n🔍 Testing JSON validation...")
        
        try:
            payload = {"json_data": sample_data}
            
            async with self.session.post(
                f"{self.base_url}/emails/validate",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Validation passed")
                    print(f"   Valid: {data['valid']}")
                    print(f"   Message: {data['message']}")
                    
                    if 'statistics' in data:
                        stats = data['statistics']
                        print(f"   Total emails: {stats.get('total_emails', 0)}")
                        print(f"   User ID: {stats.get('user_id', 'unknown')}")
                    
                    return True
                else:
                    print(f"❌ Validation failed: {response.status}")
                    error_data = await response.json()
                    print(f"   Error: {error_data}")
                    return False
        except Exception as e:
            print(f"❌ Validation error: {e}")
            return False
    
    async def test_process_emails(self, sample_data: Dict[str, Any]):
        """Test email processing endpoint."""
        print("\n🔍 Testing email processing...")
        
        try:
            payload = {
                "json_data": sample_data,
                "metadata": {
                    "test_batch": "api_test_001",
                    "source": "test_suite"
                }
            }
            
            start_time = time.time()
            
            async with self.session.post(
                f"{self.base_url}/emails/process",
                json=payload
            ) as response:
                end_time = time.time()
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Processing completed")
                    print(f"   Success: {data['success']}")
                    print(f"   Processed emails: {data['processed_count']}")
                    print(f"   Generated embeddings: {data['embedded_count']}")
                    print(f"   Collection: {data['collection_name']}")
                    print(f"   Processing time: {data['processing_time']:.3f}s")
                    print(f"   API response time: {end_time - start_time:.3f}s")
                    
                    if 'statistics' in data:
                        stats = data['statistics']
                        print(f"   Email counts: {stats['email_counts']}")
                        print(f"   Embedding counts: {stats['embedding_counts']}")
                    
                    return data
                else:
                    print(f"❌ Processing failed: {response.status}")
                    error_data = await response.json()
                    print(f"   Error: {error_data}")
                    return None
        except Exception as e:
            print(f"❌ Processing error: {e}")
            return None
    
    async def test_webhook_processing(self):
        """Test webhook processing endpoint."""
        print("\n🔍 Testing webhook processing...")
        
        webhook_data = {
            "id": "webhook-test-email-001",
            "subject": "API Test - Webhook Email Processing",
            "body": {
                "content": "This is a test email sent via webhook for API testing purposes.",
                "contentType": "text"
            },
            "sender": {
                "emailAddress": {
                    "name": "API Test Sender",
                    "address": "api-test@example.com"
                }
            },
            "createdDateTime": "2025-05-29T14:30:00Z",
            "toRecipients": [
                {
                    "emailAddress": {
                        "name": "API Test Recipient",
                        "address": "recipient@example.com"
                    }
                }
            ],
            "ccRecipients": [],
            "bccRecipients": [],
            "hasAttachments": False,
            "importance": "normal",
            "isRead": False
        }
        
        try:
            payload = {
                "webhook_data": webhook_data,
                "metadata": {
                    "webhook_source": "api_test",
                    "real_time": True
                }
            }
            
            async with self.session.post(
                f"{self.base_url}/emails/webhook",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Webhook processing completed")
                    print(f"   Success: {data['success']}")
                    print(f"   Processed emails: {data['processed_count']}")
                    print(f"   Generated embeddings: {data['embedded_count']}")
                    print(f"   Processing time: {data['processing_time']:.3f}s")
                    
                    return data
                else:
                    print(f"❌ Webhook processing failed: {response.status}")
                    error_data = await response.json()
                    print(f"   Error: {error_data}")
                    return None
        except Exception as e:
            print(f"❌ Webhook processing error: {e}")
            return None
    
    async def test_get_stats(self):
        """Test statistics endpoint."""
        print("\n🔍 Testing statistics retrieval...")
        
        try:
            async with self.session.get(f"{self.base_url}/emails/stats") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Statistics retrieved")
                    print(f"   Success: {data['success']}")
                    print(f"   Collection exists: {data['collection_exists']}")
                    print(f"   Total embeddings: {data['total_embeddings']}")
                    print(f"   Estimated emails: {data['estimated_email_count']}")
                    print(f"   Collection name: {data['collection_name']}")
                    print(f"   Embedding model: {data['embedding_model']}")
                    print(f"   Vector dimension: {data['vector_dimension']}")
                    
                    return data
                else:
                    print(f"❌ Statistics retrieval failed: {response.status}")
                    error_data = await response.json()
                    print(f"   Error: {error_data}")
                    return None
        except Exception as e:
            print(f"❌ Statistics error: {e}")
            return None
    
    async def test_get_email_info(self, email_id: str):
        """Test email info endpoint."""
        print(f"\n🔍 Testing email info retrieval for {email_id}...")
        
        try:
            async with self.session.get(f"{self.base_url}/emails/info/{email_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Email info retrieved")
                    print(f"   Success: {data['success']}")
                    print(f"   Email ID: {data['email_id']}")
                    print(f"   Embeddings count: {data['embeddings_count']}")
                    
                    if 'embeddings' in data:
                        for emb in data['embeddings']:
                            print(f"     - {emb['type']}: {emb['content_preview'][:50]}...")
                    
                    return data
                elif response.status == 404:
                    print(f"⚠️ Email not found: {email_id}")
                    return None
                else:
                    print(f"❌ Email info retrieval failed: {response.status}")
                    error_data = await response.json()
                    print(f"   Error: {error_data}")
                    return None
        except Exception as e:
            print(f"❌ Email info error: {e}")
            return None
    
    async def test_api_root(self):
        """Test API root endpoint."""
        print("\n🔍 Testing API root endpoint...")
        
        try:
            async with self.session.get(f"{self.base_url}/") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ API root accessible")
                    print(f"   Message: {data['message']}")
                    print(f"   Version: {data['version']}")
                    print(f"   Status: {data['status']}")
                    return True
                else:
                    print(f"❌ API root failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ API root error: {e}")
            return False


async def load_sample_data():
    """Load sample email data."""
    try:
        with open("sample_emails.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ sample_emails.json not found. Creating sample data...")
        
        # Create minimal sample data
        sample_data = {
            "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users('api-test-user')/messages",
            "value": [
                {
                    "id": "api-test-email-1",
                    "createdDateTime": "2025-05-29T14:00:00Z",
                    "subject": "API Test Email - Sample Subject",
                    "bodyPreview": "This is a test email for API testing...",
                    "importance": "normal",
                    "hasAttachments": False,
                    "isRead": False,
                    "sender": {
                        "emailAddress": {
                            "name": "API Test Sender",
                            "address": "api-test@example.com"
                        }
                    },
                    "toRecipients": [
                        {
                            "emailAddress": {
                                "name": "API Test Recipient",
                                "address": "recipient@example.com"
                            }
                        }
                    ],
                    "ccRecipients": [],
                    "bccRecipients": [],
                    "body": {
                        "contentType": "text",
                        "content": "This is a test email content for API testing. It contains sample text to test the email processing functionality."
                    },
                    "webLink": "https://outlook.office365.com/owa/api-test-link",
                    "conversationId": "api-test-conversation-1"
                }
            ]
        }
        
        return sample_data


async def main():
    """Run all API tests."""
    print("🚀 Starting Email Processing API Tests")
    print("=" * 60)
    
    # Load sample data
    sample_data = await load_sample_data()
    print(f"📧 Loaded sample data with {len(sample_data['value'])} emails")
    
    async with EmailAPITester() as tester:
        try:
            # Test 1: API Root
            await tester.test_api_root()
            
            # Test 2: Health Check
            health_ok = await tester.test_health_check()
            if not health_ok:
                print("❌ Health check failed, stopping tests")
                return False
            
            # Test 3: JSON Validation
            validation_ok = await tester.test_validate_json(sample_data)
            if not validation_ok:
                print("❌ JSON validation failed, stopping tests")
                return False
            
            # Test 4: Email Processing
            processing_result = await tester.test_process_emails(sample_data)
            if not processing_result:
                print("❌ Email processing failed, stopping tests")
                return False
            
            # Test 5: Webhook Processing
            webhook_result = await tester.test_webhook_processing()
            
            # Test 6: Statistics
            stats_result = await tester.test_get_stats()
            
            # Test 7: Email Info (if we have processed emails)
            if processing_result and processing_result.get('emails'):
                first_email = processing_result['emails'][0]
                email_id = first_email['id']
                await tester.test_get_email_info(email_id)
            
            print("\n" + "=" * 60)
            print("🎉 All API tests completed!")
            
            # Summary
            print("\n📊 Test Summary:")
            print(f"✅ Health Check: Passed")
            print(f"✅ JSON Validation: Passed")
            print(f"✅ Email Processing: {processing_result['processed_count']} emails")
            print(f"✅ Webhook Processing: {webhook_result['processed_count'] if webhook_result else 0} emails")
            print(f"✅ Statistics: {stats_result['total_embeddings'] if stats_result else 0} total embeddings")
            
            return True
            
        except Exception as e:
            print(f"❌ Test suite failed: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    print("📝 Note: Make sure the FastAPI server is running:")
    print("   python -m uvicorn interfaces.api.main:app --reload")
    print("   or")
    print("   python main.py")
    print()
    
    success = asyncio.run(main())
    exit(0 if success else 1)
