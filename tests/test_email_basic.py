"""
Basic test for email processing functionality.
"""

import asyncio
import json
from datetime import datetime
from core.entities.email import Email, EmailAddress, EmailEmbedding
from adapters.email.json_email_loader import JsonEmailLoaderAdapter


def test_email_entity_creation():
    """Test Email entity creation from Graph API data."""
    
    # Sample Microsoft Graph API email data
    sample_email_data = {
        "id": "AAMkAGVmMDEzMTM4LTZmYWUtNDdkNC1hMDZiLTU1OGY5OTZhYmY4OABGAAAAAAAiQ8W967B7TKBjgx9rVEURBwAiIsqMbYjsT5e-T7KzowPTAAAAAAEMAAAiIsqMbYjsT5e-T7KzowPTAAAYNKvwAAA=",
        "createdDateTime": "2025-05-29T02:01:56Z",
        "lastModifiedDateTime": "2025-05-29T02:01:56Z",
        "changeKey": "CQAAABYAAAA=",
        "categories": [],
        "receivedDateTime": "2025-05-29T02:01:56Z",
        "sentDateTime": "2025-05-29T02:01:56Z",
        "hasAttachments": False,
        "internetMessageId": "<example@outlook.com>",
        "subject": "PL25008aKRd - Test Email Subject",
        "bodyPreview": "This is a test email body preview...",
        "importance": "normal",
        "parentFolderId": "AQMkAGVmMDEzMTM4LTZmYWUtNDdkNC1hMDZiLTU1OGY5OTZhYmY4OAAuAAADIkPFveuwe0ygY4Mfa1RFEQEAIiLKjG2I7E-Xvk-ys6MD0wAAAAABDAAAAA==",
        "conversationId": "AAQkAGVmMDEzMTM4LTZmYWUtNDdkNC1hMDZiLTU1OGY5OTZhYmY4OAAQAOnUfbQv7EtIoNLvVkumUiA=",
        "conversationIndex": "AQHbEdFg6dR9tC/sS0ig0u9WS6ZSIA==",
        "isDeliveryReceiptRequested": False,
        "isReadReceiptRequested": False,
        "isRead": False,
        "isDraft": False,
        "webLink": "https://outlook.office365.com/owa/?ItemID=AAMkAGVmMDEzMTM4LTZmYWUtNDdkNC1hMDZiLTU1OGY5OTZhYmY4OABGAAAAAAAiQ8W967B7TKBjgx9rVEURBwAiIsqMbYjsT5e-T7KzowPTAAAAAAEMAAAiIsqMbYjsT5e-T7KzowPTAAAYNKvwAAA%3D&exvsurl=1&viewmodel=ReadMessageItem",
        "sender": {
            "emailAddress": {
                "name": "Darko Dominovic",
                "address": "Darko.Dominovic@crs.hr"
            }
        },
        "from": {
            "emailAddress": {
                "name": "Darko Dominovic",
                "address": "Darko.Dominovic@crs.hr"
            }
        },
        "toRecipients": [
            {
                "emailAddress": {
                    "name": "KR SDTP",
                    "address": "krsdtp@krs.co.kr"
                }
            }
        ],
        "ccRecipients": [],
        "bccRecipients": [],
        "replyTo": [],
        "body": {
            "contentType": "html",
            "content": "<html><head></head><body><p>This is a test email body with <strong>HTML</strong> content.</p><p>Best regards,<br>Darko</p></body></html>"
        }
    }
    
    # Create Email entity
    email = Email.from_graph_api(sample_email_data)
    
    # Verify basic properties
    assert email.original_id == sample_email_data["id"]
    assert email.subject == "PL25008aKRd - Test Email Subject"
    assert email.sender.name == "Darko Dominovic"
    assert email.sender.address == "Darko.Dominovic@crs.hr"
    assert len(email.to_recipients) == 1
    assert email.to_recipients[0].address == "krsdtp@krs.co.kr"
    assert email.has_attachments == False
    assert email.correspondence_thread == "PL25008aKRd"  # Extracted from subject
    
    # Verify HTML content was cleaned
    assert "<html>" not in email.body_content
    assert "This is a test email body with HTML content." in email.body_content
    
    # Verify helper methods
    assert email.is_reply() == False
    assert email.is_forward() == False
    assert len(email.get_all_recipients()) == 1
    
    print("✅ Email entity creation test passed")


def test_email_address_creation():
    """Test EmailAddress entity creation."""
    
    address_data = {
        "name": "Test User",
        "address": "test@example.com"
    }
    
    email_address = EmailAddress.from_dict(address_data)
    
    assert email_address.name == "Test User"
    assert email_address.address == "test@example.com"
    
    print("✅ EmailAddress entity creation test passed")


def test_email_embedding_creation():
    """Test EmailEmbedding entity creation."""
    
    # Create a sample email first
    sample_email_data = {
        "id": "test-email-id",
        "subject": "Test Subject",
        "body": {"content": "Test body content", "contentType": "text"},
        "sender": {"emailAddress": {"name": "Test", "address": "test@example.com"}},
        "createdDateTime": "2025-05-29T02:01:56Z",
        "toRecipients": []
    }
    
    email = Email.from_graph_api(sample_email_data)
    
    # Create subject embedding
    subject_vector = [0.1, 0.2, 0.3, 0.4, 0.5]
    subject_embedding = EmailEmbedding.create_subject_embedding(
        email=email,
        vector=subject_vector,
        model="text-embedding-3-small"
    )
    
    assert subject_embedding.email_id == email.id
    assert subject_embedding.embedding_type == "subject"
    assert subject_embedding.content == "Test Subject"
    assert subject_embedding.vector == subject_vector
    assert subject_embedding.model == "text-embedding-3-small"
    assert subject_embedding.dimension == 5
    
    # Create body embedding
    body_vector = [0.6, 0.7, 0.8, 0.9, 1.0]
    body_embedding = EmailEmbedding.create_body_embedding(
        email=email,
        vector=body_vector,
        model="text-embedding-3-small"
    )
    
    assert body_embedding.email_id == email.id
    assert body_embedding.embedding_type == "body"
    assert body_embedding.content == "Test body content"
    assert body_embedding.vector == body_vector
    
    print("✅ EmailEmbedding entity creation test passed")


async def test_json_email_loader():
    """Test JsonEmailLoaderAdapter functionality."""
    
    # Sample Microsoft Graph API JSON response
    sample_json = {
        "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users('test-user-id')/messages",
        "value": [
            {
                "id": "email-1",
                "subject": "PL25008aKRd - First Email",
                "body": {"content": "First email content", "contentType": "text"},
                "sender": {"emailAddress": {"name": "Sender 1", "address": "sender1@example.com"}},
                "createdDateTime": "2025-05-29T02:01:56Z",
                "toRecipients": [{"emailAddress": {"name": "Recipient 1", "address": "recipient1@example.com"}}],
                "ccRecipients": [],
                "bccRecipients": [],
                "hasAttachments": False,
                "importance": "normal",
                "isRead": False
            },
            {
                "id": "email-2",
                "subject": "MSC 110/5 - Second Email",
                "body": {"content": "Second email content", "contentType": "text"},
                "sender": {"emailAddress": {"name": "Sender 2", "address": "sender2@example.com"}},
                "createdDateTime": "2025-05-29T03:01:56Z",
                "toRecipients": [{"emailAddress": {"name": "Recipient 2", "address": "recipient2@example.com"}}],
                "ccRecipients": [],
                "bccRecipients": [],
                "hasAttachments": True,
                "importance": "high",
                "isRead": True
            }
        ]
    }
    
    # Test JSON loader
    loader = JsonEmailLoaderAdapter()
    
    # Test validation
    assert loader.validate_json_structure(sample_json) == True
    
    # Test loading emails
    emails = await loader.load_from_json(sample_json)
    
    assert len(emails) == 2
    
    # Verify first email
    email1 = emails[0]
    assert email1.original_id == "email-1"
    assert email1.subject == "PL25008aKRd - First Email"
    assert email1.correspondence_thread == "PL25008aKRd"
    assert email1.sender.address == "sender1@example.com"
    
    # Verify second email
    email2 = emails[1]
    assert email2.original_id == "email-2"
    assert email2.subject == "MSC 110/5 - Second Email"
    assert email2.correspondence_thread == "MSC 110/5"
    assert email2.has_attachments == True
    
    # Test statistics
    stats = loader.get_statistics(sample_json)
    assert stats["total_emails"] == 2
    assert "PL25008aKRd" in stats["thread_distribution"]
    assert "MSC 110/5" in stats["thread_distribution"]
    
    print("✅ JsonEmailLoaderAdapter test passed")


async def test_webhook_processing():
    """Test webhook email processing."""
    
    # Sample webhook data (single email)
    webhook_data = {
        "id": "webhook-email-1",
        "subject": "RE: PL25008aKRd - Webhook Email",
        "body": {"content": "Webhook email content", "contentType": "text"},
        "sender": {"emailAddress": {"name": "Webhook Sender", "address": "webhook@example.com"}},
        "createdDateTime": "2025-05-29T04:01:56Z",
        "toRecipients": [{"emailAddress": {"name": "Webhook Recipient", "address": "recipient@example.com"}}],
        "ccRecipients": [],
        "bccRecipients": [],
        "hasAttachments": False,
        "importance": "normal",
        "isRead": False
    }
    
    loader = JsonEmailLoaderAdapter()
    
    # Test webhook loading (should wrap single email in array)
    emails = await loader.load_from_webhook(webhook_data)
    
    assert len(emails) == 1
    email = emails[0]
    assert email.original_id == "webhook-email-1"
    assert email.subject == "RE: PL25008aKRd - Webhook Email"
    assert email.is_reply() == True
    assert email.correspondence_thread == "PL25008aKRd"
    
    print("✅ Webhook processing test passed")


def main():
    """Run all basic tests."""
    print("🧪 Running basic email processing tests...\n")
    
    # Synchronous tests
    test_email_entity_creation()
    test_email_address_creation()
    test_email_embedding_creation()
    
    # Asynchronous tests
    asyncio.run(test_json_email_loader())
    asyncio.run(test_webhook_processing())
    
    print("\n✅ All basic tests passed!")
    print("\n📊 Test Summary:")
    print("- Email entity creation: ✅")
    print("- EmailAddress entity creation: ✅")
    print("- EmailEmbedding entity creation: ✅")
    print("- JSON email loader: ✅")
    print("- Webhook processing: ✅")


if __name__ == "__main__":
    main()
