"""
Storage interface for Rental Genie
Defines abstract interfaces for data storage operations
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TenantProfile:
    """Structured tenant profile data"""
    # Basic information
    age: Optional[int] = None
    sex: Optional[str] = None
    occupation: Optional[str] = None
    
    # Rental preferences
    move_in_date: Optional[str] = None
    rental_duration: Optional[str] = None
    
    # Financial/legal
    guarantor_status: Optional[str] = None
    guarantor_details: Optional[str] = None
    
    # Additional context
    viewing_interest: Optional[bool] = None
    availability: Optional[str] = None
    language_preference: Optional[str] = None
    
    # Status and workflow
    status: str = "prospect"
    property_interest: Optional[str] = None
    application_date: Optional[str] = None
    lease_start_date: Optional[str] = None
    lease_end_date: Optional[str] = None
    notes: Optional[str] = None
    
    # Metadata
    created_at: Optional[str] = None
    last_updated: Optional[str] = None
    conversation_turns: int = 0

class StorageProvider(ABC):
    """Abstract interface for storage operations"""
    
    @abstractmethod
    def store_tenant_profile(self, session_id: str, profile: Dict[str, Any]) -> bool:
        """Store tenant profile"""
        pass
    
    @abstractmethod
    def get_tenant_profile(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get tenant profile by session ID"""
        pass
    
    @abstractmethod
    def delete_tenant_profile(self, session_id: str) -> bool:
        """Delete tenant profile"""
        pass
    
    @abstractmethod
    def get_all_tenant_profiles(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all tenant profiles"""
        pass
    
    @abstractmethod
    def update_tenant_status(self, session_id: str, new_status: str, additional_data: Optional[Dict[str, Any]] = None) -> bool:
        """Update tenant status"""
        pass
    
    @abstractmethod
    def get_all_properties(self) -> List[Dict[str, Any]]:
        """Get all properties"""
        pass
    
    @abstractmethod
    def get_available_properties(self) -> List[Dict[str, Any]]:
        """Get available properties"""
        pass
    
    @abstractmethod
    def search_properties(self, search_term: str) -> List[Dict[str, Any]]:
        """Search properties"""
        pass
    
    @abstractmethod
    def add_conversation_message(self, session_id: str, message_type: str, content: str, 
                               extracted_info: Dict = None, confidence: float = None) -> bool:
        """Add conversation message"""
        pass
    
    @abstractmethod
    def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history"""
        pass
    
    @abstractmethod
    def increment_conversation_turns(self, session_id: str) -> bool:
        """Increment conversation turns"""
        pass
    
    @abstractmethod
    def mark_handoff_completed(self, session_id: str, reason: str = None) -> bool:
        """Mark handoff as completed"""
        pass
