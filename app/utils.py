from pyairtable import Api, Base, Table
from dotenv import load_dotenv
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from .enums import TenantStatus

load_dotenv()

# Get environment variables
AIRTABLE_PERSONAL_ACCESS_TOKEN = os.environ.get("AIRTABLE_PERSONAL_ACCESS_TOKEN")
BASE_ID = os.environ.get("BASE_ID")
PROPERTY_TABLE_NAME = os.environ.get("PROPERTY_TABLE_NAME")
TENANT_TABLE_NAME = os.environ.get("TENANT_TABLE_NAME", "Tenants")  # Single table for all tenants/prospects

def get_all_property_info():
    """Get all property information from Airtable using personal access token"""
    try:
        if not all([AIRTABLE_PERSONAL_ACCESS_TOKEN, BASE_ID, PROPERTY_TABLE_NAME]):
            raise ValueError("Missing required environment variables: AIRTABLE_PERSONAL_ACCESS_TOKEN, BASE_ID, or PROPERTY_TABLE_NAME")
        
        # Create API instance with personal access token
        api = Api(AIRTABLE_PERSONAL_ACCESS_TOKEN)
        
        # Get the table
        table = Table(AIRTABLE_PERSONAL_ACCESS_TOKEN, BASE_ID, PROPERTY_TABLE_NAME)
        
        # Get all records
        records = table.all()
        
        print(f"Successfully loaded {len(records)} property records from Airtable")
        return records
        
    except Exception as e:
        print(f"Error loading property data from Airtable: {e}")
        # Return fallback property data for testing
        return [{"fields": {"Name": "Sample Property", "Address": "123 Main St", "Rent": "$1500/month", "Available": "January 2024"}}]

def get_property_by_id(record_id):
    """Get a specific property by record ID"""
    try:
        if not all([AIRTABLE_PERSONAL_ACCESS_TOKEN, BASE_ID, PROPERTY_TABLE_NAME]):
            raise ValueError("Missing required environment variables")
        
        table = Table(AIRTABLE_PERSONAL_ACCESS_TOKEN, BASE_ID, PROPERTY_TABLE_NAME)
        record = table.get(record_id)
        return record
        
    except Exception as e:
        print(f"Error getting property by ID: {e}")
        return None

def search_properties(search_term):
    """Search properties by name or address"""
    try:
        if not all([AIRTABLE_PERSONAL_ACCESS_TOKEN, BASE_ID, PROPERTY_TABLE_NAME]):
            raise ValueError("Missing required environment variables")
        
        table = Table(AIRTABLE_PERSONAL_ACCESS_TOKEN, BASE_ID, PROPERTY_TABLE_NAME)
        
        # Search in property_name and address_street fields (based on actual field names)
        formula = f"OR(SEARCH('{search_term}', {{property_name}}), SEARCH('{search_term}', {{address_street}}))"
        records = table.all(formula=formula)
        
        return records
        
    except Exception as e:
        print(f"Error searching properties: {e}")
        return []

def get_available_properties():
    """Get only available properties"""
    try:
        if not all([AIRTABLE_PERSONAL_ACCESS_TOKEN, BASE_ID, PROPERTY_TABLE_NAME]):
            raise ValueError("Missing required environment variables")
        
        table = Table(AIRTABLE_PERSONAL_ACCESS_TOKEN, BASE_ID, PROPERTY_TABLE_NAME)
        
        # Filter for available properties
        formula = "SEARCH('available', LOWER({status}))"
        records = table.all(formula=formula)
        
        return records
        
    except Exception as e:
        print(f"Error getting available properties: {e}")
        return []

def get_tenant_table():
    """Get the tenant table from Airtable"""
    try:
        if not all([AIRTABLE_PERSONAL_ACCESS_TOKEN, BASE_ID, TENANT_TABLE_NAME]):
            raise ValueError("Missing required environment variables for tenant table")
        
        table = Table(AIRTABLE_PERSONAL_ACCESS_TOKEN, BASE_ID, TENANT_TABLE_NAME)
        return table
    except Exception as e:
        print(f"Error getting tenant table: {e}")
        return None

def store_tenant_profile(session_id: str, tenant_data: Dict[str, Any]) -> bool:
    """Store tenant profile in Airtable"""
    try:
        table = get_tenant_table()
        if not table:
            return False
        
        # Prepare data for Airtable
        fields = {
            "Session ID": session_id,
            "Status": tenant_data.get("status", TenantStatus.PROSPECT.value),  # Use enum default
            "Age": tenant_data.get("age"),
            "Sex": tenant_data.get("sex"),
            "Occupation": tenant_data.get("occupation"),
            "Move In Date": tenant_data.get("move_in_date"),
            "Rental Duration": tenant_data.get("rental_duration"),
            "Guarantor Status": tenant_data.get("guarantor_status"),
            "Guarantor Details": tenant_data.get("guarantor_details"),
            "Viewing Interest": tenant_data.get("viewing_interest"),
            "Availability": tenant_data.get("availability"),
            "Language Preference": tenant_data.get("language_preference"),
            "Property Interest": tenant_data.get("property_interest"),
            "Application Date": tenant_data.get("application_date"),
            "Lease Start Date": tenant_data.get("lease_start_date"),
            "Lease End Date": tenant_data.get("lease_end_date"),
            "Notes": tenant_data.get("notes"),
            "Created At": tenant_data.get("created_at"),
            "Last Updated": datetime.now().isoformat(),
            "Conversation Turns": tenant_data.get("conversation_turns", 0)
        }
        
        # Remove None values
        fields = {k: v for k, v in fields.items() if v is not None}
        
        # Check if tenant already exists - try different field names
        existing_records = None
        for field_name in ['Session ID', 'session_id', 'SessionID', 'ID', 'Record ID', 'session id']:
            try:
                existing_records = table.all(formula=f"{{{field_name}}}='{session_id}'")
                if existing_records:
                    break
            except Exception as e:
                continue
        
        if existing_records:
            # Update existing record
            record_id = existing_records[0]['id']
            table.update(record_id, fields)
            print(f"Updated tenant profile for session {session_id}")
        else:
            # Create new record
            table.create(fields)
            print(f"Created new tenant profile for session {session_id}")
        
        return True
        
    except Exception as e:
        print(f"Error storing tenant profile: {e}")
        return False

def get_tenant_profile(session_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve tenant profile from Airtable"""
    try:
        table = get_tenant_table()
        if not table:
            return None
        
        # Try different possible field names for session ID
        possible_fields = ['Session ID', 'session_id', 'SessionID', 'ID', 'Record ID', 'session id']
        records = None
        
        for field_name in possible_fields:
            try:
                records = table.all(formula=f"{{{field_name}}}='{session_id}'")
                if records:
                    print(f"Found session using field name: {field_name}")
                    break
            except Exception as e:
                print(f"Tried field '{field_name}', got error: {e}")
                continue
        
        if not records:
            print(f"Session ID '{session_id}' not found with any field name")
            return None
        
        if records:
            record = records[0]
            fields = record['fields']
            
            # Convert back to our internal format
            tenant_data = {
                "age": fields.get("Age"),
                "sex": fields.get("Sex"),
                "occupation": fields.get("Occupation"),
                "move_in_date": fields.get("Move In Date"),
                "rental_duration": fields.get("Rental Duration"),
                "guarantor_status": fields.get("Guarantor Status"),
                "guarantor_details": fields.get("Guarantor Details"),
                "viewing_interest": fields.get("Viewing Interest"),
                "availability": fields.get("Availability"),
                "language_preference": fields.get("Language Preference"),
                "status": fields.get("Status", TenantStatus.PROSPECT.value),  # Use enum default
                "property_interest": fields.get("Property Interest"),
                "application_date": fields.get("Application Date"),
                "lease_start_date": fields.get("Lease Start Date"),
                "lease_end_date": fields.get("Lease End Date"),
                "notes": fields.get("Notes"),
                "created_at": fields.get("Created At"),
                "last_updated": fields.get("Last Updated"),
                "conversation_turns": fields.get("Conversation Turns", 0)
            }
            
            return tenant_data
        
        return None
        
    except Exception as e:
        print(f"Error retrieving tenant profile: {e}")
        return None

def get_all_tenant_profiles(status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all tenant profiles from Airtable, optionally filtered by status"""
    try:
        table = get_tenant_table()
        if not table:
            return []
        
        if status_filter:
            # Validate status filter
            if not TenantStatus.is_valid(status_filter):
                print(f"Warning: Invalid status filter '{status_filter}'")
                return []
            
            # Filter by status
            records = table.all(formula=f"{{Status}}='{status_filter}'")
        else:
            # Get all records
            records = table.all()
        
        tenants = []
        
        for record in records:
            fields = record['fields']
            
            # Try to get session_id from various possible field names
            session_id = fields.get("Session ID") or fields.get("session_id") or fields.get("SessionID") or fields.get("ID") or record.get('id')
            
            tenant_data = {
                "session_id": session_id,
                "status": fields.get("Status", TenantStatus.ACTIVE_TENANT.value),  # Default to active_tenant since these are current tenants
                "age": fields.get("Age"),
                "sex": fields.get("Sex"),
                "occupation": fields.get("Occupation"),
                "move_in_date": fields.get("Move In Date"),
                "rental_duration": fields.get("Rental Duration"),
                "guarantor_status": fields.get("Guarantor Status"),
                "viewing_interest": fields.get("Viewing Interest"),
                "property_interest": fields.get("Property Interest"),
                "application_date": fields.get("Application Date"),
                "lease_start_date": fields.get("Lease Start Date"),
                "lease_end_date": fields.get("Lease End Date"),
                "created_at": fields.get("Created At"),
                "last_updated": fields.get("Last Updated")
            }
            tenants.append(tenant_data)
        
        return tenants
        
    except Exception as e:
        print(f"Error retrieving all tenant profiles: {e}")
        return []

def update_tenant_status(session_id: str, new_status: str, additional_data: Optional[Dict[str, Any]] = None) -> bool:
    """Update tenant status and optionally add additional data"""
    try:
        # Validate status
        if not TenantStatus.is_valid(new_status):
            print(f"Error: Invalid status '{new_status}'")
            return False
        
        table = get_tenant_table()
        if not table:
            return False
        
        # For now, since we're dealing with mock tenant IDs (tenant_0, tenant_1, etc.)
        # and the actual Airtable doesn't have these session IDs, we'll simulate the update
        # In a real implementation, you'd need to map these to actual Airtable records
        
        print(f"Simulating tenant status update: {session_id} -> {new_status}")
        
        # If this is a real session ID (not mock), try to find it in Airtable
        if not session_id.startswith('tenant_'):
            # Try different possible field names for session ID
            possible_fields = ['Session ID', 'session_id', 'SessionID', 'ID', 'Record ID']
            
            for field_name in possible_fields:
                try:
                    records = table.all(formula=f"{{{field_name}}}='{session_id}'")
                    if records:
                        record_id = records[0]['id']
                        current_fields = records[0]['fields']
                        
                        # Prepare update fields
                        update_fields = {
                            "Status": new_status,
                            "Last Updated": datetime.now().isoformat()
                        }
                        
                        # Add additional data if provided
                        if additional_data:
                            for key, value in additional_data.items():
                                if value is not None:
                                    update_fields[key] = value
                        
                        # Update the record
                        table.update(record_id, update_fields)
                        print(f"Updated tenant status to '{TenantStatus.get_display_name(new_status)}' for session {session_id}")
                        return True
                        
                except Exception as e:
                    print(f"Tried field '{field_name}', got error: {e}")
                    continue
        
        # For mock tenants, just return success (simulated update)
        if session_id.startswith('tenant_'):
            print(f"Mock tenant update successful: {session_id} -> {new_status}")
            return True
        
        print(f"Tenant profile not found for session {session_id}")
        return False
        
    except Exception as e:
        print(f"Error updating tenant status: {e}")
        return False

def get_tenants_by_status(status: str) -> List[Dict[str, Any]]:
    """Get all tenants with a specific status"""
    return get_all_tenant_profiles(status_filter=status)

def get_prospects() -> List[Dict[str, Any]]:
    """Get all prospect tenants (status = 'prospect')"""
    return get_tenants_by_status(TenantStatus.PROSPECT.value)

def get_active_tenants() -> List[Dict[str, Any]]:
    """Get all active tenants (status = 'active_tenant')"""
    return get_tenants_by_status(TenantStatus.ACTIVE_TENANT.value)

def get_qualified_prospects() -> List[Dict[str, Any]]:
    """Get all qualified prospects (status = 'qualified')"""
    return get_tenants_by_status(TenantStatus.QUALIFIED.value)

def get_tenant_status_info() -> Dict[str, Any]:
    """Get information about all available tenant statuses"""
    return {
        "statuses": [
            {
                "value": status.value,
                "display_name": TenantStatus.get_display_name(status.value),
                "description": TenantStatus.get_description(status.value)
            }
            for status in TenantStatus
        ],
        "valid_values": TenantStatus.get_all_values()
    }

def delete_tenant_profile(session_id: str) -> bool:
    """Delete tenant profile from Airtable"""
    try:
        table = get_tenant_table()
        if not table:
            return False
        
        # Try different possible field names for session ID
        records = None
        for field_name in ['Session ID', 'session_id', 'SessionID', 'ID', 'Record ID', 'session id']:
            try:
                records = table.all(formula=f"{{{field_name}}}='{session_id}'")
                if records:
                    break
            except Exception as e:
                continue
        
        if records:
            record_id = records[0]['id']
            table.delete(record_id)
            print(f"Deleted tenant profile for session {session_id}")
            return True
        
        return False
        
    except Exception as e:
        print(f"Error deleting tenant profile: {e}")
        return False