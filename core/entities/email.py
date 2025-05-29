"""
Email domain entities for Document Embedding & Retrieval System.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
import re


@dataclass
class EmailAddress:
    """Email address entity."""
    name: str
    address: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "EmailAddress":
        """Create EmailAddress from dictionary."""
        return cls(
            name=data.get("name", ""),
            address=data.get("address", "")
        )


@dataclass
class Email:
    """Core email entity."""
    
    id: str
    original_id: str  # Microsoft Graph ID
    subject: str
    body_content: str
    body_preview: str
    created_datetime: datetime
    sent_datetime: Optional[datetime]
    received_datetime: Optional[datetime]
    sender: EmailAddress
    to_recipients: List[EmailAddress]
    cc_recipients: List[EmailAddress]
    bcc_recipients: List[EmailAddress]
    web_link: Optional[str]
    conversation_id: Optional[str]
    internet_message_id: Optional[str]
    has_attachments: bool
    importance: str
    is_read: bool
    correspondence_thread: Optional[str]  # Extracted from subject
    raw_data: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    
    def __post_init__(self):
        """Post-initialization processing."""
        if not self.id:
            self.id = str(uuid.uuid4())
        
        if not self.created_at:
            self.created_at = datetime.utcnow()
        
        # Extract correspondence thread from subject if not set
        if not self.correspondence_thread:
            self.correspondence_thread = self._extract_correspondence_thread()
    
    @classmethod
    def from_graph_api(cls, data: Dict[str, Any]) -> "Email":
        """Create Email from Microsoft Graph API data."""
        
        # Parse datetime strings
        created_datetime = cls._parse_datetime(data.get("createdDateTime"))
        sent_datetime = cls._parse_datetime(data.get("sentDateTime"))
        received_datetime = cls._parse_datetime(data.get("receivedDateTime"))
        
        # Parse sender
        sender_data = data.get("sender", {}).get("emailAddress", {})
        sender = EmailAddress.from_dict(sender_data)
        
        # Parse recipients
        to_recipients = [
            EmailAddress.from_dict(recipient.get("emailAddress", {}))
            for recipient in data.get("toRecipients", [])
        ]
        
        cc_recipients = [
            EmailAddress.from_dict(recipient.get("emailAddress", {}))
            for recipient in data.get("ccRecipients", [])
        ]
        
        bcc_recipients = [
            EmailAddress.from_dict(recipient.get("emailAddress", {}))
            for recipient in data.get("bccRecipients", [])
        ]
        
        # Extract body content
        body_data = data.get("body", {})
        body_content = body_data.get("content", "")
        
        # Clean HTML content if present
        if body_data.get("contentType") == "html":
            body_content = cls._clean_html_content(body_content)
        
        return cls(
            id=str(uuid.uuid4()),
            original_id=data.get("id", ""),
            subject=data.get("subject", ""),
            body_content=body_content,
            body_preview=data.get("bodyPreview", ""),
            created_datetime=created_datetime,
            sent_datetime=sent_datetime,
            received_datetime=received_datetime,
            sender=sender,
            to_recipients=to_recipients,
            cc_recipients=cc_recipients,
            bcc_recipients=bcc_recipients,
            web_link=data.get("webLink"),
            conversation_id=data.get("conversationId"),
            internet_message_id=data.get("internetMessageId"),
            has_attachments=data.get("hasAttachments", False),
            importance=data.get("importance", "normal"),
            is_read=data.get("isRead", False),
            correspondence_thread=None,  # Will be extracted in __post_init__
            raw_data=data,
            metadata={
                "source": "microsoft_graph",
                "content_type": body_data.get("contentType", "text"),
                "inference_classification": data.get("inferenceClassification"),
                "parent_folder_id": data.get("parentFolderId")
            },
            created_at=datetime.utcnow()
        )
    
    def _extract_correspondence_thread(self) -> Optional[str]:
        """Extract correspondence thread identifier from subject."""
        # Look for patterns like PL25008aKRd, RE:, FW:, etc.
        patterns = [
            r'([A-Z]{2}\d{5}[a-zA-Z]+)',  # PL25008aKRd pattern
            r'(MSC\s+\d+/\d+)',           # MSC 110/5 pattern
            r'(IMO\s+MSC\s+[\d/]+)',      # IMO MSC pattern
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.subject)
            if match:
                return match.group(1)
        
        # Fallback: use conversation_id if available
        return self.conversation_id
    
    @staticmethod
    def _parse_datetime(datetime_str: Optional[str]) -> Optional[datetime]:
        """Parse ISO datetime string."""
        if not datetime_str:
            return None
        
        try:
            # Remove 'Z' and parse
            if datetime_str.endswith('Z'):
                datetime_str = datetime_str[:-1] + '+00:00'
            return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None
    
    @staticmethod
    def _clean_html_content(html_content: str) -> str:
        """Clean HTML tags from content."""
        import re
        
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', html_content)
        
        # Replace HTML entities
        html_entities = {
            '&nbsp;': ' ',
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&#39;': "'",
            '&apos;': "'",
            '&#x27;': "'",
            '&rdquo;': '"',
            '&ldquo;': '"',
            '&rsquo;': "'",
            '&lsquo;': "'",
        }
        
        for entity, replacement in html_entities.items():
            clean_text = clean_text.replace(entity, replacement)
        
        # Clean up whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text)
        clean_text = clean_text.strip()
        
        return clean_text
    
    def get_all_recipients(self) -> List[EmailAddress]:
        """Get all recipients (TO + CC + BCC)."""
        return self.to_recipients + self.cc_recipients + self.bcc_recipients
    
    def get_recipient_addresses(self) -> List[str]:
        """Get all recipient email addresses."""
        return [recipient.address for recipient in self.get_all_recipients()]
    
    def get_display_subject(self, max_length: int = 100) -> str:
        """Get truncated subject for display."""
        if len(self.subject) <= max_length:
            return self.subject
        return self.subject[:max_length] + "..."
    
    def get_display_body(self, max_length: int = 500) -> str:
        """Get truncated body for display."""
        if len(self.body_content) <= max_length:
            return self.body_content
        return self.body_content[:max_length] + "..."
    
    def is_reply(self) -> bool:
        """Check if this email is a reply."""
        reply_indicators = ['RE:', 'Re:', 'RE：', 'Automatic reply:']
        return any(self.subject.startswith(indicator) for indicator in reply_indicators)
    
    def is_forward(self) -> bool:
        """Check if this email is a forward."""
        forward_indicators = ['FW:', 'Fw:', 'FWD:', 'Fwd:']
        return any(self.subject.startswith(indicator) for indicator in forward_indicators)
    
    def get_thread_subject(self) -> str:
        """Get clean subject without RE:, FW: prefixes."""
        subject = self.subject
        
        # Remove common prefixes
        prefixes = ['RE:', 'Re:', 'FW:', 'Fw:', 'FWD:', 'Fwd:', 'Automatic reply:']
        for prefix in prefixes:
            if subject.startswith(prefix):
                subject = subject[len(prefix):].strip()
        
        return subject


@dataclass
class EmailEmbedding:
    """Email-specific embedding entity."""
    
    id: str
    email_id: str
    embedding_type: str  # 'subject' or 'body'
    vector: List[float]
    content: str  # The actual text that was embedded
    model: str
    dimension: int
    metadata: Dict[str, Any]
    created_at: datetime
    
    def __post_init__(self):
        """Post-initialization processing."""
        if not self.id:
            self.id = f"{self.email_id}_{self.embedding_type}"
        
        if not self.created_at:
            self.created_at = datetime.utcnow()
        
        if not self.dimension:
            self.dimension = len(self.vector)
    
    @classmethod
    def create_subject_embedding(
        cls,
        email: Email,
        vector: List[float],
        model: str
    ) -> "EmailEmbedding":
        """Create subject embedding."""
        return cls(
            id=f"{email.id}_subject",
            email_id=email.id,
            embedding_type="subject",
            vector=vector,
            content=email.subject,
            model=model,
            dimension=len(vector),
            metadata={
                "correspondence_thread": email.correspondence_thread,
                "created_time": email.created_datetime.isoformat() if email.created_datetime else None,
                "sender_name": email.sender.name,
                "sender_address": email.sender.address,
                "is_reply": email.is_reply(),
                "is_forward": email.is_forward(),
                "importance": email.importance
            },
            created_at=datetime.utcnow()
        )
    
    @classmethod
    def create_body_embedding(
        cls,
        email: Email,
        vector: List[float],
        model: str
    ) -> "EmailEmbedding":
        """Create body embedding."""
        return cls(
            id=f"{email.id}_body",
            email_id=email.id,
            embedding_type="body",
            vector=vector,
            content=email.body_content,
            model=model,
            dimension=len(vector),
            metadata={
                "correspondence_thread": email.correspondence_thread,
                "created_time": email.created_datetime.isoformat() if email.created_datetime else None,
                "sender_name": email.sender.name,
                "sender_address": email.sender.address,
                "recipient_addresses": email.get_recipient_addresses(),
                "web_link": email.web_link,
                "has_attachments": email.has_attachments,
                "content_length": len(email.body_content)
            },
            created_at=datetime.utcnow()
        )
