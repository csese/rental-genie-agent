"""
Supabase client for Rental Genie
Replaces Airtable functionality with better performance and real-time capabilities
"""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import httpx
from dotenv import load_dotenv

load_dotenv()

class SupabaseClient:
    def __init__(self):
        self.supabase_url = os.environ.get("SUPABASE_URL")
        self.supabase_key = os.environ.get("SUPABASE_ANON_KEY")
        self.service_key = os.environ.get("SUPABASE_SERVICE_KEY")
        
        if not all([self.supabase_url, self.supabase_key]):
            raise ValueError("Missing Supabase environment variables")
        
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json"
        }
        
        self.service_headers = {
            "apikey": self.service_key,
            "Authorization": f"Bearer {self.service_key}",
            "Content-Type": "application/json"
        }
    
    async def _make_request(self, method: str, endpoint: str, data: Dict = None, use_service_key: bool = False) -> Dict:
        """Make HTTP request to Supabase"""
        headers = self.service_headers if use_service_key else self.headers
        url = f"{self.supabase_url}/rest/v1/{endpoint}"
        
        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(url, headers=headers)
            elif method == "POST":
                response = await client.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = await client.put(url, headers=headers, json=data)
            elif method == "DELETE":
                response = await client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code >= 400:
                raise Exception(f"Supabase API error: {response.status_code} - {response.text}")
            
            return response.json() if response.content else {}
    
    # Tenant Management
    async def create_tenant(self, session_id: str, tenant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new tenant profile"""
        data = {
            "session_id": session_id,
            "status": tenant_data.get("status", "prospect"),
            "age": tenant_data.get("age"),
            "sex": tenant_data.get("sex"),
            "occupation": tenant_data.get("occupation"),
            "move_in_date": tenant_data.get("move_in_date"),
            "rental_duration": tenant_data.get("rental_duration"),
            "guarantor_status": tenant_data.get("guarantor_status"),
            "guarantor_details": tenant_data.get("guarantor_details"),
            "viewing_interest": tenant_data.get("viewing_interest", False),
            "availability": tenant_data.get("availability"),
            "language_preference": tenant_data.get("language_preference"),
            "property_interest": tenant_data.get("property_interest"),
            "notes": tenant_data.get("notes"),
            "profile_data": tenant_data.get("profile_data", {}),
            "conversation_turns": tenant_data.get("conversation_turns", 0)
        }
        
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}
        
        return await self._make_request("POST", "tenants", data)
    
    async def get_tenant(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get tenant profile by session ID"""
        try:
            result = await self._make_request("GET", f"tenants?session_id=eq.{session_id}")
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting tenant: {e}")
            return None
    
    async def update_tenant(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update tenant profile"""
        try:
            await self._make_request("PUT", f"tenants?session_id=eq.{session_id}", updates)
            return True
        except Exception as e:
            print(f"Error updating tenant: {e}")
            return False
    
    async def get_tenants_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get all tenants with a specific status"""
        try:
            return await self._make_request("GET", f"tenants?status=eq.{status}")
        except Exception as e:
            print(f"Error getting tenants by status: {e}")
            return []
    
    async def get_all_tenants(self) -> List[Dict[str, Any]]:
        """Get all tenants"""
        try:
            return await self._make_request("GET", "tenants")
        except Exception as e:
            print(f"Error getting all tenants: {e}")
            return []
    
    # Chat Session Management
    async def create_chat_session(self, session_id: str, platform: str, user_id: str = None) -> Dict[str, Any]:
        """Create a new chat session"""
        data = {
            "session_id": session_id,
            "platform": platform,
            "user_id": user_id,
            "status": "active"
        }
        
        return await self._make_request("POST", "chat_sessions", data)
    
    async def get_chat_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get chat session by session ID"""
        try:
            result = await self._make_request("GET", f"chat_sessions?session_id=eq.{session_id}")
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting chat session: {e}")
            return None
    
    async def update_chat_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update chat session"""
        try:
            await self._make_request("PUT", f"chat_sessions?session_id=eq.{session_id}", updates)
            return True
        except Exception as e:
            print(f"Error updating chat session: {e}")
            return False
    
    # Conversation Messages
    async def add_message(self, session_id: str, message_type: str, content: str, 
                         extracted_info: Dict = None, confidence: float = None) -> Dict[str, Any]:
        """Add a message to the conversation"""
        data = {
            "session_id": session_id,
            "message_type": message_type,
            "content": content,
            "extracted_info": extracted_info or {},
            "confidence": confidence
        }
        
        return await self._make_request("POST", "conversation_messages", data)
    
    async def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for a session"""
        try:
            return await self._make_request("GET", f"conversation_messages?session_id=eq.{session_id}&order=created_at.asc")
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            return []
    
    # Property Management
    async def get_all_properties(self) -> List[Dict[str, Any]]:
        """Get all properties"""
        try:
            return await self._make_request("GET", "properties")
        except Exception as e:
            print(f"Error getting properties: {e}")
            return []
    
    async def get_available_properties(self) -> List[Dict[str, Any]]:
        """Get available properties"""
        try:
            return await self._make_request("GET", "properties?status=eq.available")
        except Exception as e:
            print(f"Error getting available properties: {e}")
            return []
    
    async def search_properties(self, search_term: str) -> List[Dict[str, Any]]:
        """Search properties by name or address"""
        try:
            # Use PostgreSQL full-text search
            return await self._make_request("GET", f"properties?or=(name.ilike.*{search_term}*,address_street.ilike.*{search_term}*)")
        except Exception as e:
            print(f"Error searching properties: {e}")
            return []
    
    # Advanced Queries
    async def get_tenant_with_history(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get tenant with full conversation history using the database function"""
        try:
            result = await self._make_request("GET", f"rpc/get_tenant_with_history?p_session_id={session_id}")
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting tenant with history: {e}")
            return None
    
    async def get_tenant_summary(self) -> List[Dict[str, Any]]:
        """Get tenant summary using the view"""
        try:
            return await self._make_request("GET", "tenant_summary")
        except Exception as e:
            print(f"Error getting tenant summary: {e}")
            return []
    
    # Utility Methods
    async def increment_conversation_turns(self, session_id: str) -> bool:
        """Increment conversation turns for a tenant"""
        try:
            # Get current turns
            tenant = await self.get_tenant(session_id)
            if tenant:
                current_turns = tenant.get("conversation_turns", 0)
                await self.update_tenant(session_id, {"conversation_turns": current_turns + 1})
                return True
            return False
        except Exception as e:
            print(f"Error incrementing conversation turns: {e}")
            return False
    
    async def mark_handoff_completed(self, session_id: str, reason: str = None) -> bool:
        """Mark a chat session as handed off"""
        try:
            updates = {"handoff_completed": True}
            if reason:
                updates["handoff_reason"] = reason
            
            await self.update_chat_session(session_id, updates)
            return True
        except Exception as e:
            print(f"Error marking handoff: {e}")
            return False

# Global client instance
supabase_client = None

def get_supabase_client() -> SupabaseClient:
    """Get or create Supabase client instance"""
    global supabase_client
    if supabase_client is None:
        supabase_client = SupabaseClient()
    return supabase_client
