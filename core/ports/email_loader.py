"""
Email loader port interface and adapter implementation.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import asyncio
from datetime import datetime

# First, define the port interface
class EmailLoaderPort(ABC):
    """Port interface for email loading operations."""
    
    @abstractmethod
    async def load_from_json(self, json_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> List['Email']:
        """Load emails from JSON data."""
        pass
    
    @abstractmethod
    async def load_from_webhook(self, webhook_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> List['Email']:
        """Load emails from webhook payload."""
        pass
    
    @abstractmethod
    async def load_multiple_json_files(self, json_files: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> List['Email']:
        """Load emails from multiple JSON files."""
        pass
    
    @abstractmethod
    def validate_json_structure(self, json_data: Dict[str, Any]) -> bool:
        """Validate if JSON has expected email structure."""
        pass
    
    @abstractmethod
    def get_loader_type(self) -> str:
        """Get the type of email loader."""
        pass
