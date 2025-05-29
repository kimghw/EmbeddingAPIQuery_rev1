#!/usr/bin/env python3
"""
Comprehensive test script for all email-related API endpoints.
Tests all functionality including processing, listing, searching, and chat.
"""

import asyncio
import aiohttp
import json
from datetime import datetime
import sys
from typing import Dict, Any, List

# API base URL
BASE_URL = "http://localhost:8000"

# Test data
SAMPLE_EMAIL_JSON = {
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users('user@example.com')/messages",
    "value": [
        {
            "id": "AAMkAGI2TG93AAA=",
            "createdDateTime": "2025-01-15T10:30:00Z",
            "lastModifiedDateTime": "2025-01-15T10:30:00Z",
            "receivedDateTime": "2025-01-15T10:30:00Z",
            "sentDateTime": "2025-01-15T10:30:00Z",
            "hasAttachments": False,
            "internetMessageId": "<message1@example.com>",
            "subject": "Project Update: Q1 2025 Milestones",
            "bodyPreview": "Here's the latest update on our Q1 milestones...",
            "importance": "normal",
            "parentFolderId": "AAMkAGI2TG93AAAA=",
            "conversationId": "AAQkAGI2TG93AAA=",
            "isRead": True,
            "isDraft": False,
            "webLink": "https://outlook.office365.com/owa/?ItemID=AAMkAGI2TG93AAA%3D",
            "body": {
                "contentType": "html",
                "content": "<html><body><p>Here's the latest update on our Q1 milestones. We've made significant progress on the following items:</p><ul><li>Completed API design</li><li>Implemented core features</li><li>Started testing phase</li></ul></body></html>"
            },
            "sender": {
                "emailAddress": {
                    "name": "John Doe",
                    "address": "john.doe@example.com"
                }
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "name": "Team",
                        "address": "team@example.com"
                    }
                }
            ],
            "ccRecipients": [],
            "bccRecipients": []
        },
        {
            "id": "AAMkAGI2TG94AAA=",
            "createdDateTime": "2025-01-16T14:20:00Z",
            "lastModifiedDateTime": "2025-01-16T14:20:00Z",
            "receivedDateTime": "2025-01-16T14:20:00Z",
            "sentDateTime": "2025-01-16T14:20:00Z",
            "hasAttachments": True,
            "internetMessageId": "<message2@example.com>",
            "subject": "RE: Project Update: Q1 2025 Milestones",
            "bodyPreview": "Thanks for the update. I have a few questions...",
            "importance": "high",
            "parentFolderId": "AAMkAGI2TG93AAAA=",
            "conversationId": "AAQkAGI2TG93AAA=",
            "isRead": False,
            "isDraft": False,
            "webLink": "https://outlook.office365.com/owa/?ItemID=AAMkAGI2TG94AAA%3D",
            "body": {
                "contentType": "text",
                "content": "Thanks for the update. I have a few questions about the testing phase:\n\n1. What's the timeline for completion?\n2. Do we need additional resources?\n3. Are there any blockers we should address?\n\nLet's discuss in tomorrow's meeting."
            },
            "sender": {
                "emailAddress": {
                    "name": "Jane Smith",
                    "address": "jane.smith@example.com"
                }
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "name": "John Doe",
                        "address": "john.doe@example.com"
                    }
                }
            ],
            "ccRecipients": [
                {
                    "emailAddress": {
                        "name": "Team",
                        "address": "team@example.com"
                    }
                }
            ],
            "bccRecipients": []
        }
    ]
}


class EmailAPITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        print(f"{status} - {test_name}")
        if details:
            print(f"    Details: {details}")
    
    async def test_health_check(self):
        """Test the health check endpoint."""
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                data = await response.json()
                success = response.status == 200 and data.get("status") == "healthy"
                self.log_result("Health Check", success, f"Status: {response.status}")
                return success
        except Exception as e:
            self.log_result("Health Check", False, str(e))
            return False
    
    async def test_process_emails(self):
        """Test email processing endpoint."""
        try:
            # Wrap the email JSON in the expected request format
            request_data = {
                "json_data": SAMPLE_EMAIL_JSON,
                "metadata": {
                    "source": "test",
                    "test_run": True
                }
            }
            
            async with self.session.post(
                f"{self.base_url}/emails/process",
                json=request_data
            ) as response:
                data = await response.json()
                success = response.status == 200 and data.get("success", False)
                details = f"Processed: {data.get('processed_count', 0)}, Embedded: {data.get('embedded_count', 0)}"
                self.log_result("Process Emails", success, details)
                return success
        except Exception as e:
            self.log_result("Process Emails", False, str(e))
            return False
    
    async def test_process_webhook(self):
        """Test webhook processing endpoint."""
        try:
            # Simulate webhook with single email
            single_email = {
                "id": "AAMkAGI2TG95AAA=",
                "createdDateTime": "2025-01-17T09:00:00Z",
                "subject": "Webhook Test Email",
                "body": {
                    "contentType": "text",
                    "content": "This is a test email from webhook"
                },
                "sender": {
                    "emailAddress": {
                        "name": "Webhook Sender",
                        "address": "webhook@example.com"
                    }
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "name": "Recipient",
                            "address": "recipient@example.com"
                        }
                    }
                ],
                "ccRecipients": [],
                "bccRecipients": []
            }
            
            # Wrap in the expected request format
            request_data = {
                "webhook_data": single_email,
                "metadata": {
                    "webhook_source": "test",
                    "real_time": True
                }
            }
            
            async with self.session.post(
                f"{self.base_url}/emails/webhook",
                json=request_data
            ) as response:
                data = await response.json()
                success = response.status == 200 and data.get("success", False)
                details = f"Webhook type: {data.get('webhook_type', 'unknown')}"
                self.log_result("Process Webhook", success, details)
                return success
        except Exception as e:
            self.log_result("Process Webhook", False, str(e))
            return False
    
    async def test_list_emails(self):
        """Test email listing endpoint."""
        try:
            # Test basic listing
            async with self.session.get(f"{self.base_url}/emails/list") as response:
                data = await response.json()
                success = response.status == 200
                details = f"Total emails: {data.get('total', 0)}"
                self.log_result("List Emails (Basic)", success, details)
            
            # Test with pagination
            async with self.session.get(
                f"{self.base_url}/emails/list?limit=10&offset=0"
            ) as response:
                data = await response.json()
                success = response.status == 200
                self.log_result("List Emails (Pagination)", success)
            
            # Test with filters
            async with self.session.get(
                f"{self.base_url}/emails/list?sender=john.doe@example.com"
            ) as response:
                data = await response.json()
                success = response.status == 200
                self.log_result("List Emails (Filter by Sender)", success)
            
            # Test sorting
            async with self.session.get(
                f"{self.base_url}/emails/list?sort_by=created_at&sort_order=desc"
            ) as response:
                data = await response.json()
                success = response.status == 200
                self.log_result("List Emails (Sorting)", success)
                
            return True
        except Exception as e:
            self.log_result("List Emails", False, str(e))
            return False
    
    async def test_search_emails(self):
        """Test email search endpoint."""
        try:
            # Test subject search
            search_request = {
                "query": "Project Update",
                "search_type": "subject",
                "top_k": 5
            }
            
            async with self.session.post(
                f"{self.base_url}/emails/search",
                json=search_request
            ) as response:
                data = await response.json()
                success = response.status == 200
                details = f"Found {len(data.get('results', []))} results"
                self.log_result("Search Emails (Subject)", success, details)
            
            # Test body search
            search_request["search_type"] = "body"
            search_request["query"] = "testing phase"
            
            async with self.session.post(
                f"{self.base_url}/emails/search",
                json=search_request
            ) as response:
                data = await response.json()
                success = response.status == 200
                details = f"Found {len(data.get('results', []))} results"
                self.log_result("Search Emails (Body)", success, details)
            
            # Test combined search
            search_request["search_type"] = "combined"
            search_request["query"] = "milestones"
            
            async with self.session.post(
                f"{self.base_url}/emails/search",
                json=search_request
            ) as response:
                data = await response.json()
                success = response.status == 200
                details = f"Found {len(data.get('results', []))} results"
                self.log_result("Search Emails (Combined)", success, details)
                
            return True
        except Exception as e:
            self.log_result("Search Emails", False, str(e))
            return False
    
    async def test_email_stats(self):
        """Test email statistics endpoint."""
        try:
            async with self.session.get(f"{self.base_url}/emails/stats") as response:
                data = await response.json()
                success = response.status == 200 and data.get("success", False)
                if success:
                    stats = data.get("statistics", {})
                    details = f"Total: {stats.get('email_counts', {}).get('total', 0)}"
                else:
                    details = data.get("error", "Unknown error")
                self.log_result("Email Statistics", success, details)
                return success
        except Exception as e:
            self.log_result("Email Statistics", False, str(e))
            return False
    
    async def test_email_info(self):
        """Test email info endpoint."""
        try:
            # First, get list of emails to get a valid ID
            async with self.session.get(f"{self.base_url}/emails/list?limit=1") as response:
                if response.status == 200:
                    data = await response.json()
                    emails = data.get("emails", [])
                    if emails:
                        email_id = emails[0]["id"]
                        
                        # Test get email info
                        async with self.session.get(
                            f"{self.base_url}/emails/{email_id}"
                        ) as info_response:
                            info_data = await info_response.json()
                            success = info_response.status == 200
                            details = f"Email ID: {email_id[:8]}..."
                            self.log_result("Get Email Info", success, details)
                            return success
                    else:
                        self.log_result("Get Email Info", False, "No emails found to test")
                        return False
                else:
                    self.log_result("Get Email Info", False, "Failed to get email list")
                    return False
        except Exception as e:
            self.log_result("Get Email Info", False, str(e))
            return False
    
    async def test_email_chat(self):
        """Test email chat endpoint."""
        try:
            chat_request = {
                "message": "What are the main topics discussed in recent emails?",
                "context_emails": 5,
                "include_metadata": True
            }
            
            async with self.session.post(
                f"{self.base_url}/emails/chat",
                json=chat_request
            ) as response:
                data = await response.json()
                success = response.status == 200
                details = f"Response length: {len(data.get('response', ''))}"
                self.log_result("Email Chat", success, details)
                return success
        except Exception as e:
            self.log_result("Email Chat", False, str(e))
            return False
    
    async def test_delete_email(self):
        """Test email deletion endpoint."""
        try:
            # First, get list of emails to get a valid ID
            async with self.session.get(f"{self.base_url}/emails/list?limit=1") as response:
                if response.status == 200:
                    data = await response.json()
                    emails = data.get("emails", [])
                    if emails:
                        email_id = emails[0]["id"]
                        
                        # Test delete email
                        async with self.session.delete(
                            f"{self.base_url}/emails/{email_id}"
                        ) as delete_response:
                            delete_data = await delete_response.json()
                            success = delete_response.status == 200 and delete_data.get("success", False)
                            details = f"Deleted email ID: {email_id[:8]}..."
                            self.log_result("Delete Email", success, details)
                            return success
                    else:
                        self.log_result("Delete Email", False, "No emails found to test")
                        return False
                else:
                    self.log_result("Delete Email", False, "Failed to get email list")
                    return False
        except Exception as e:
            self.log_result("Delete Email", False, str(e))
            return False
    
    async def run_all_tests(self):
        """Run all email API tests."""
        print("\n" + "="*60)
        print("EMAIL API COMPREHENSIVE TEST SUITE")
        print("="*60 + "\n")
        
        # Run tests in order
        await self.test_health_check()
        print()
        
        print("1. EMAIL PROCESSING TESTS")
        print("-" * 30)
        await self.test_process_emails()
        await self.test_process_webhook()
        print()
        
        print("2. EMAIL RETRIEVAL TESTS")
        print("-" * 30)
        await self.test_list_emails()
        await self.test_email_info()
        await self.test_email_stats()
        print()
        
        print("3. EMAIL SEARCH TESTS")
        print("-" * 30)
        await self.test_search_emails()
        print()
        
        print("4. EMAIL CHAT TESTS")
        print("-" * 30)
        await self.test_email_chat()
        print()
        
        print("5. EMAIL MANAGEMENT TESTS")
        print("-" * 30)
        await self.test_delete_email()
        print()
        
        # Summary
        print("="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        return failed_tests == 0


async def main():
    """Main test runner."""
    # Check if server is running
    print("Checking if API server is running...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/health") as response:
                if response.status != 200:
                    print("❌ API server is not responding. Please start it with:")
                    print("   python -m uvicorn interfaces.api.main:app --reload")
                    return
    except Exception as e:
        print(f"❌ Cannot connect to API server: {e}")
        print("   Please start the server with:")
        print("   python -m uvicorn interfaces.api.main:app --reload")
        return
    
    print("✅ API server is running\n")
    
    # Run tests
    async with EmailAPITester(BASE_URL) as tester:
        success = await tester.run_all_tests()
        
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
