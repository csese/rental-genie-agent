"""
Supabase storage implementation for Rental Genie
Implements the StorageProvider interface using Supabase
"""

import os
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from .storage_interface import StorageProvider, TenantProfile
from .supabase_client import get_supabase_client

def run_async(coro):
    """Helper to run async functions in sync context"""
    try:
        # Check if we're already in an event loop
        try:
            loop = asyncio.get_running_loop()
            # If we're in an event loop, we need to create a task
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()
        except RuntimeError:
            # No event loop running, we can use asyncio.run
            return asyncio.run(coro)
    except Exception as e:
        print(f"Error in run_async: {e}")
        return None

class SupabaseStorageProvider(StorageProvider):
    """Supabase implementation of StorageProvider"""
    
    def __init__(self):
        self.client = get_supabase_client()
    
    def store_tenant_profile(self, session_id: str, profile: Dict[str, Any]) -> bool:
        """Store tenant profile in Supabase"""
        try:
            # Check if tenant already exists
            existing = run_async(self.client.get_tenant(session_id))
            
            if existing:
                # Update existing tenant
                result = run_async(self.client.update_tenant(session_id, profile))
                return result
            else:
                # Create new tenant
                result = run_async(self.client.create_tenant(session_id, profile))
                return result is not None
        except Exception as e:
            print(f"Error storing tenant profile: {e}")
            return False
    
    def get_tenant_profile(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get tenant profile from Supabase"""
        try:
            return run_async(self.client.get_tenant(session_id))
        except Exception as e:
            print(f"Error getting tenant profile: {e}")
            return None
    
    def delete_tenant_profile(self, session_id: str) -> bool:
        """Delete tenant profile from Supabase"""
        try:
            # Note: This would need to be implemented in the Supabase client
            # For now, return True as a placeholder
            print(f"Would delete tenant profile for session {session_id}")
            return True
        except Exception as e:
            print(f"Error deleting tenant profile: {e}")
            return False
    
    def get_all_tenant_profiles(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all tenant profiles from Supabase"""
        try:
            if status_filter:
                return run_async(self.client.get_tenants_by_status(status_filter))
            else:
                return run_async(self.client.get_all_tenants())
        except Exception as e:
            print(f"Error getting all tenant profiles: {e}")
            return []
    
    def update_tenant_status(self, session_id: str, new_status: str, additional_data: Optional[Dict[str, Any]] = None) -> bool:
        """Update tenant status in Supabase"""
        try:
            updates = {"status": new_status}
            if additional_data:
                updates.update(additional_data)
            
            return run_async(self.client.update_tenant(session_id, updates))
        except Exception as e:
            print(f"Error updating tenant status: {e}")
            return False
    
    def get_all_properties(self) -> List[Dict[str, Any]]:
        """Get all properties from Supabase"""
        try:
            properties = run_async(self.client.get_all_properties())
            
            # Convert to the format expected by the rest of the application
            formatted_properties = []
            for prop in properties:
                formatted_prop = {
                    "id": prop.get("id"),
                    "fields": {
                        "Name": prop.get("name"),
                        "Address": f"{prop.get('address_street', '')}, {prop.get('city', '')} {prop.get('zip_code', '')}",
                        "Rent": f"{prop.get('rent_amount', 0)} {prop.get('rent_currency', 'EUR')}/month",
                        "Available": prop.get("availability_date"),
                        "Status": prop.get("status"),
                        "Description": prop.get("description"),
                        "Surface Area": prop.get("surface_area"),
                        "Room Count": prop.get("room_count"),
                        "Bathroom Type": prop.get("bathroom_type"),
                        "Deposit Amount": prop.get("deposit_amount"),
                        "Appliances": prop.get("appliances_included", [])
                    }
                }
                formatted_properties.append(formatted_prop)
            
            print(f"Successfully loaded {len(formatted_properties)} property records from Supabase")
            return formatted_properties
            
        except Exception as e:
            print(f"Error loading property data from Supabase: {e}")
            print("⚠️  WARNING: No property data available. Check your Supabase connection.")
            return []
    
    def get_available_properties(self) -> List[Dict[str, Any]]:
        """Get available properties from Supabase"""
        try:
            properties = run_async(self.client.get_available_properties())
            
            # Convert to expected format
            formatted_properties = []
            for prop in properties:
                formatted_prop = {
                    "id": prop.get("id"),
                    "fields": {
                        "Name": prop.get("name"),
                        "Address": f"{prop.get('address_street', '')}, {prop.get('city', '')} {prop.get('zip_code', '')}",
                        "Rent": f"{prop.get('rent_amount', 0)} {prop.get('rent_currency', 'EUR')}/month",
                        "Available": prop.get("availability_date"),
                        "Status": prop.get("status")
                    }
                }
                formatted_properties.append(formatted_prop)
            
            return formatted_properties
            
        except Exception as e:
            print(f"Error getting available properties: {e}")
            return []
    
    def search_properties(self, search_term: str) -> List[Dict[str, Any]]:
        """Search properties in Supabase"""
        try:
            properties = run_async(self.client.search_properties(search_term))
            
            # Convert to expected format
            formatted_properties = []
            for prop in properties:
                formatted_prop = {
                    "id": prop.get("id"),
                    "fields": {
                        "Name": prop.get("name"),
                        "Address": f"{prop.get('address_street', '')}, {prop.get('city', '')} {prop.get('zip_code', '')}",
                        "Rent": f"{prop.get('rent_amount', 0)} {prop.get('rent_currency', 'EUR')}/month",
                        "Available": prop.get("availability_date"),
                        "Status": prop.get("status")
                    }
                }
                formatted_properties.append(formatted_prop)
            
            return formatted_properties
            
        except Exception as e:
            print(f"Error searching properties: {e}")
            return []
    
    def add_conversation_message(self, session_id: str, message_type: str, content: str, 
                               extracted_info: Dict = None, confidence: float = None) -> bool:
        """Add conversation message to Supabase"""
        try:
            result = run_async(self.client.add_message(session_id, message_type, content, extracted_info, confidence))
            return result is not None
        except Exception as e:
            print(f"Error adding conversation message: {e}")
            return False
    
    def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history from Supabase"""
        try:
            return run_async(self.client.get_conversation_history(session_id))
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            return []
    
    def increment_conversation_turns(self, session_id: str) -> bool:
        """Increment conversation turns in Supabase"""
        try:
            return run_async(self.client.increment_conversation_turns(session_id))
        except Exception as e:
            print(f"Error incrementing conversation turns: {e}")
            return False
    
    def mark_handoff_completed(self, session_id: str, reason: str = None) -> bool:
        """Mark handoff as completed in Supabase"""
        try:
            return run_async(self.client.mark_handoff_completed(session_id, reason))
        except Exception as e:
            print(f"Error marking handoff completed: {e}")
            return False
