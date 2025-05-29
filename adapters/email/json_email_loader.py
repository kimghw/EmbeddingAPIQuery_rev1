"""
Email loader port interface and adapter implementation.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import asyncio
from datetime import datetime
from core.ports.email_loader import EmailLoaderPort


# Adapter implementation
class JsonEmailLoaderAdapter(EmailLoaderPort):
    """JSON email loader adapter for Microsoft Graph API format."""
    
    def __init__(self):
        """Initialize JSON email loader."""
        self.loader_type = "microsoft_graph_json"
        self.required_fields = ["id", "subject", "body", "sender", "createdDateTime"]
    
    async def load_from_json(self, json_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> List['Email']:
        """Load emails from JSON data."""
        try:
            # Validate JSON structure
            if not self.validate_json_structure(json_data):
                raise ValueError("Invalid email JSON structure")
            
            # Import here to avoid circular imports
            from core.entities.email import Email
            
            emails = []
            email_data_list = json_data.get("value", [])
            
            # Process each email in the list
            for email_data in email_data_list:
                try:
                    # Add loader metadata
                    if metadata:
                        email_data.setdefault("loader_metadata", {}).update(metadata)
                    
                    # Create Email entity from Graph API data
                    email = Email.from_graph_api(email_data)
                    emails.append(email)
                    
                except Exception as e:
                    print(f"Error processing email {email_data.get('id', 'unknown')}: {e}")
                    continue
            
            return emails
            
        except Exception as e:
            raise RuntimeError(f"Failed to load emails from JSON: {str(e)}")
    
    async def load_from_webhook(self, webhook_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> List['Email']:
        """Load emails from webhook payload."""
        # Webhook data might have different structure, normalize it
        webhook_metadata = metadata or {}
        webhook_metadata.update({
            "source": "webhook",
            "received_at": datetime.utcnow().isoformat()
        })
        
        # For webhook, we might receive single email or array
        if "value" not in webhook_data and "id" in webhook_data:
            # Single email in webhook, wrap in Graph API format
            webhook_data = {
                "@odata.context": "webhook",
                "value": [webhook_data]
            }
        
        return await self.load_from_json(webhook_data, webhook_metadata)
    
    async def load_multiple_json_files(self, json_files: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> List['Email']:
        """Load emails from multiple JSON files."""
        all_emails = []
        
        for i, json_data in enumerate(json_files):
            try:
                file_metadata = metadata.copy() if metadata else {}
                file_metadata["file_index"] = i
                
                emails = await self.load_from_json(json_data, file_metadata)
                all_emails.extend(emails)
                
            except Exception as e:
                print(f"Error loading JSON file {i}: {e}")
                continue
        
        return all_emails
    
    def validate_json_structure(self, json_data: Dict[str, Any]) -> bool:
        """Validate if JSON has expected email structure."""
        try:
            # Check for Microsoft Graph structure
            if "@odata.context" not in json_data:
                return False
            
            # Check for value array
            if "value" not in json_data or not isinstance(json_data["value"], list):
                return False
            
            # Check if we have at least one email
            if len(json_data["value"]) == 0:
                return True  # Empty is valid
            
            # Validate first email structure
            first_email = json_data["value"][0]
            for field in self.required_fields:
                if field not in first_email:
                    return False
            
            # Check sender structure
            if "emailAddress" not in first_email.get("sender", {}):
                return False
            
            # Check body structure
            body = first_email.get("body", {})
            if "content" not in body:
                return False
            
            return True
            
        except Exception:
            return False
    
    def get_loader_type(self) -> str:
        """Get the type of email loader."""
        return self.loader_type
    
    def extract_odata_context(self, json_data: Dict[str, Any]) -> Optional[str]:
        """Extract OData context information."""
        return json_data.get("@odata.context")
    
    def extract_user_id(self, json_data: Dict[str, Any]) -> Optional[str]:
        """Extract user ID from OData context."""
        context = self.extract_odata_context(json_data)
        if not context:
            return None
        
        # Extract user ID from context URL
        # Format: https://graph.microsoft.com/v1.0/$metadata#users('USER_ID')/messages
        import re
        match = re.search(r"users\('([^']+)'\)", context)
        return match.group(1) if match else None
    
    def get_statistics(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get statistics about the loaded emails."""
        try:
            emails = json_data.get("value", [])
            
            # Count by sender
            sender_counts = {}
            # Count by subject patterns
            subject_patterns = {}
            # Count by date
            date_counts = {}
            
            for email in emails:
                # Sender stats
                sender = email.get("sender", {}).get("emailAddress", {}).get("address", "unknown")
                sender_counts[sender] = sender_counts.get(sender, 0) + 1
                
                # Subject patterns (correspondence threads)
                subject = email.get("subject", "")
                # Look for thread patterns
                import re
                patterns = [
                    r'([A-Z]{2}\d{5}[a-zA-Z]+)',  # PL25008aKRd pattern
                    r'(MSC\s+\d+/\d+)',           # MSC 110/5 pattern
                ]
                
                thread_found = False
                for pattern in patterns:
                    match = re.search(pattern, subject)
                    if match:
                        thread = match.group(1)
                        subject_patterns[thread] = subject_patterns.get(thread, 0) + 1
                        thread_found = True
                        break
                
                if not thread_found:
                    subject_patterns["other"] = subject_patterns.get("other", 0) + 1
                
                # Date stats (by day)
                created_date = email.get("createdDateTime", "")
                if created_date:
                    date_key = created_date[:10]  # YYYY-MM-DD
                    date_counts[date_key] = date_counts.get(date_key, 0) + 1
            
            return {
                "total_emails": len(emails),
                "sender_distribution": sender_counts,
                "thread_distribution": subject_patterns,
                "date_distribution": date_counts,
                "user_id": self.extract_user_id(json_data),
                "odata_context": self.extract_odata_context(json_data)
            }
            
        except Exception as e:
            return {"error": f"Failed to generate statistics: {str(e)}"}


class WebhookEmailLoaderAdapter(EmailLoaderPort):
    """Specialized adapter for webhook email processing."""
    
    def __init__(self):
        """Initialize webhook email loader."""
        self.loader_type = "webhook"
        self.json_loader = JsonEmailLoaderAdapter()
    
    async def load_from_json(self, json_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> List['Email']:
        """Delegate to JSON loader."""
        return await self.json_loader.load_from_json(json_data, metadata)
    
    async def load_from_webhook(self, webhook_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> List['Email']:
        """Load emails from webhook with additional processing."""
        webhook_metadata = metadata or {}
        webhook_metadata.update({
            "source": "webhook",
            "received_at": datetime.utcnow().isoformat(),
            "webhook_type": self._detect_webhook_type(webhook_data)
        })
        
        # Process different webhook formats
        normalized_data = self._normalize_webhook_data(webhook_data)
        
        return await self.json_loader.load_from_json(normalized_data, webhook_metadata)
    
    async def load_multiple_json_files(self, json_files: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> List['Email']:
        """Delegate to JSON loader."""
        return await self.json_loader.load_multiple_json_files(json_files, metadata)
    
    def validate_json_structure(self, json_data: Dict[str, Any]) -> bool:
        """Validate webhook JSON structure."""
        return self.json_loader.validate_json_structure(json_data)
    
    def get_loader_type(self) -> str:
        """Get the type of email loader."""
        return self.loader_type
    
    def _detect_webhook_type(self, webhook_data: Dict[str, Any]) -> str:
        """Detect the type of webhook payload."""
        if "@odata.context" in webhook_data:
            return "microsoft_graph"
        elif "notification" in webhook_data:
            return "outlook_notification"
        elif "message" in webhook_data:
            return "generic_email"
        else:
            return "unknown"
    
    def _normalize_webhook_data(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize different webhook formats to standard structure."""
        webhook_type = self._detect_webhook_type(webhook_data)
        
        if webhook_type == "microsoft_graph":
            # Already in correct format
            return webhook_data
        
        elif webhook_type == "outlook_notification":
            # Extract email data from notification
            if "value" in webhook_data:
                return webhook_data
            else:
                # Single notification, wrap in array
                return {"value": [webhook_data]}
        
        elif webhook_type == "generic_email":
            # Convert generic email format
            message = webhook_data.get("message", {})
            return {
                "@odata.context": "webhook",
                "value": [message]
            }
        
        else:
            # Try to wrap single email
            if "id" in webhook_data and "subject" in webhook_data:
                return {
                    "@odata.context": "webhook",
                    "value": [webhook_data]
                }
            else:
                raise ValueError(f"Unsupported webhook format: {webhook_type}")
    
    async def process_real_time_webhook(
        self, 
        webhook_data: Dict[str, Any], 
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process webhook with real-time response."""
        try:
            emails = await self.load_from_webhook(webhook_data)
            
            result = {
                "success": True,
                "processed_count": len(emails),
                "emails": [
                    {
                        "id": email.id,
                        "original_id": email.original_id,
                        "subject": email.get_display_subject(),
                        "sender": email.sender.address,
                        "created_datetime": email.created_datetime.isoformat() if email.created_datetime else None,
                        "correspondence_thread": email.correspondence_thread,
                        "has_attachments": email.has_attachments
                    }
                    for email in emails
                ]
            }
            
            # Send callback if URL provided
            if callback_url:
                await self._send_webhook_callback(callback_url, result)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "processed_count": 0
            }
    
    async def _send_webhook_callback(self, callback_url: str, data: Dict[str, Any]):
        """Send callback to external URL."""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    callback_url, 
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status != 200:
                        print(f"Webhook callback failed: {response.status}")
                        
        except Exception as e:
            print(f"Error sending webhook callback: {e}")


# Factory function for creating appropriate loader
def create_email_loader(loader_type: str = "json") -> EmailLoaderPort:
    """Factory function to create appropriate email loader."""
    if loader_type == "json":
        return JsonEmailLoaderAdapter()
    elif loader_type == "webhook":
        return WebhookEmailLoaderAdapter()
    else:
        raise ValueError(f"Unsupported loader type: {loader_type}")
