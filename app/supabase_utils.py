"""
Supabase utilities for Rental Genie
Replaces Airtable functionality with Supabase
"""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
from .supabase_client import get_supabase_client
from .conversation_memory import TenantStatus

# Global Supabase client
_supabase_client = None

def get_supabase():
    """Get Supabase client instance"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = get_supabase_client()
    return _supabase_client

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

# Property Management Functions
def get_all_property_info():
    """Get all property information from Supabase"""
    try:
        supabase = get_supabase()
        properties = run_async(supabase.get_all_properties())
        
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
        # Return fallback property data for testing
        return [{"fields": {"Name": "Sample Property", "Address": "123 Main St", "Rent": "$1500/month", "Available": "January 2024"}}]

def get_property_by_id(record_id):
    """Get a specific property by record ID"""
    try:
        supabase = get_supabase()
        # Note: This would need to be implemented in the Supabase client
        # For now, return None
        return None
        
    except Exception as e:
        print(f"Error getting property by ID: {e}")
        return None

def search_properties(search_term):
    """Search properties by name or address"""
    try:
        supabase = get_supabase()
        properties = run_async(supabase.search_properties(search_term))
        
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

def get_available_properties():
    """Get only available properties"""
    try:
        supabase = get_supabase()
        properties = run_async(supabase.get_available_properties())
        
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

# Tenant Management Functions
def store_tenant_profile(session_id: str, tenant_data: Dict[str, Any]) -> bool:
    """Store tenant profile in Supabase"""
    try:
        supabase = get_supabase()
        
        # Check if tenant already exists
        existing_tenant = run_async(supabase.get_tenant(session_id))
        
        if existing_tenant:
            # Update existing tenant
            success = run_async(supabase.update_tenant(session_id, tenant_data))
            if success:
                print(f"Updated tenant profile for session {session_id}")
                return True
        else:
            # Create new tenant
            result = run_async(supabase.create_tenant(session_id, tenant_data))
            if result is not None:
                print(f"Created tenant profile for session {session_id}")
                return True
        
        return False
        
    except Exception as e:
        print(f"Error storing tenant profile: {e}")
        return False

def get_tenant_profile(session_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve tenant profile from Supabase"""
    try:
        supabase = get_supabase()
        tenant = run_async(supabase.get_tenant(session_id))
        
        if tenant:
            # Convert back to our internal format
            tenant_data = {
                "age": tenant.get("age"),
                "sex": tenant.get("sex"),
                "occupation": tenant.get("occupation"),
                "move_in_date": tenant.get("move_in_date"),
                "rental_duration": tenant.get("rental_duration"),
                "guarantor_status": tenant.get("guarantor_status"),
                "guarantor_details": tenant.get("guarantor_details"),
                "viewing_interest": tenant.get("viewing_interest"),
                "availability": tenant.get("availability"),
                "language_preference": tenant.get("language_preference", "English"),
                "status": tenant.get("status", TenantStatus.PROSPECT.value),
                "property_interest": tenant.get("property_interest"),
                "application_date": tenant.get("application_date"),
                "lease_start_date": tenant.get("lease_start_date"),
                "lease_end_date": tenant.get("lease_end_date"),
                "notes": tenant.get("notes"),
                "created_at": tenant.get("created_at"),
                "last_updated": tenant.get("updated_at"),
                "conversation_turns": tenant.get("conversation_turns", 0),
                "profile_data": tenant.get("profile_data", {})
            }
            
            return tenant_data
        
        return None
        
    except Exception as e:
        print(f"Error retrieving tenant profile: {e}")
        return None

def get_all_tenant_profiles(status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all tenant profiles from Supabase, optionally filtered by status"""
    try:
        supabase = get_supabase()
        
        if status_filter:
            tenants = run_async(supabase.get_tenants_by_status(status_filter))
        else:
            tenants = run_async(supabase.get_all_tenants())
        
        # Convert to expected format
        formatted_tenants = []
        for tenant in tenants:
            formatted_tenant = {
                "session_id": tenant.get("session_id"),
                "status": tenant.get("status"),
                "age": tenant.get("age"),
                "sex": tenant.get("sex"),
                "occupation": tenant.get("occupation"),
                "move_in_date": tenant.get("move_in_date"),
                "rental_duration": tenant.get("rental_duration"),
                "guarantor_status": tenant.get("guarantor_status"),
                "viewing_interest": tenant.get("viewing_interest"),
                "property_interest": tenant.get("property_interest"),
                "application_date": tenant.get("application_date"),
                "lease_start_date": tenant.get("lease_start_date"),
                "lease_end_date": tenant.get("lease_end_date"),
                "created_at": tenant.get("created_at"),
                "last_updated": tenant.get("updated_at"),
                "conversation_turns": tenant.get("conversation_turns", 0),
                "profile_data": tenant.get("profile_data", {})
            }
            formatted_tenants.append(formatted_tenant)
        
        return formatted_tenants
        
    except Exception as e:
        print(f"Error retrieving all tenant profiles: {e}")
        return []

def update_tenant_status(session_id: str, new_status: str, additional_data: Optional[Dict[str, Any]] = None) -> bool:
    """Update tenant status and optionally add additional data"""
    try:
        # Validate status
        if not TenantStatus.is_valid(new_status):
            print(f"Invalid status: {new_status}")
            return False
        
        supabase = get_supabase()
        
        # Prepare update data
        update_data = {
            "status": new_status,
            "updated_at": datetime.now().isoformat()
        }
        
        # Add additional data if provided
        if additional_data:
            for key, value in additional_data.items():
                if value is not None:
                    update_data[key] = value
        
        # Update the tenant
        success = run_async(supabase.update_tenant(session_id, update_data))
        
        if success:
            print(f"Updated tenant status to '{TenantStatus.get_display_name(new_status)}' for session {session_id}")
            return True
        else:
            print(f"Failed to update tenant status for session {session_id}")
            return False
        
    except Exception as e:
        print(f"Error updating tenant status: {e}")
        return False

def get_tenants_by_status(status: str) -> List[Dict[str, Any]]:
    """Get tenants by specific status"""
    return get_all_tenant_profiles(status)

def get_prospects() -> List[Dict[str, Any]]:
    """Get all prospects"""
    return get_all_tenant_profiles("prospect")

def get_qualified_prospects() -> List[Dict[str, Any]]:
    """Get all qualified prospects"""
    return get_all_tenant_profiles("qualified")

def get_active_tenants() -> List[Dict[str, Any]]:
    """Get all active tenants"""
    return get_all_tenant_profiles("active_tenant")

def get_tenant_status_info() -> Dict[str, Any]:
    """Get tenant status information"""
    return {
        "statuses": TenantStatus.get_all_values(),
        "display_names": {status: TenantStatus.get_display_name(status) for status in TenantStatus.get_all_values()},
        "descriptions": {status: TenantStatus.get_description(status) for status in TenantStatus.get_all_values()},
        "valid_values": TenantStatus.get_all_values()
    }

def delete_tenant_profile(session_id: str) -> bool:
    """Delete tenant profile from Supabase"""
    try:
        supabase = get_supabase()
        # Note: This would need to be implemented in the Supabase client
        # For now, return False
        print(f"Delete functionality not yet implemented for Supabase")
        return False
        
    except Exception as e:
        print(f"Error deleting tenant profile: {e}")
        return False

# Conversation Management Functions
def add_conversation_message(session_id: str, message_type: str, content: str, 
                           extracted_info: Dict = None, confidence: float = None) -> bool:
    """Add a message to the conversation"""
    try:
        supabase = get_supabase()
        result = run_async(supabase.add_message(session_id, message_type, content, extracted_info, confidence))
        return bool(result)
    except Exception as e:
        print(f"Error adding conversation message: {e}")
        return False

def get_conversation_history(session_id: str) -> List[Dict[str, Any]]:
    """Get conversation history for a session"""
    try:
        supabase = get_supabase()
        messages = run_async(supabase.get_conversation_history(session_id))
        return messages
    except Exception as e:
        print(f"Error getting conversation history: {e}")
        return []

def increment_conversation_turns(session_id: str) -> bool:
    """Increment conversation turns for a tenant"""
    try:
        supabase = get_supabase()
        success = run_async(supabase.increment_conversation_turns(session_id))
        return success
    except Exception as e:
        print(f"Error incrementing conversation turns: {e}")
        return False

def mark_handoff_completed(session_id: str, reason: str = None) -> bool:
    """Mark a chat session as handed off"""
    try:
        supabase = get_supabase()
        success = run_async(supabase.mark_handoff_completed(session_id, reason))
        return success
    except Exception as e:
        print(f"Error marking handoff: {e}")
        return False
