"""
Property Management Module for Rental Genie
Handles property operations including status updates, CRUD operations, and property queries
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from .supabase_client import get_supabase_client

class PropertyStatus:
    """Property status constants"""
    AVAILABLE = "available"
    NOT_AVAILABLE = "not_available"
    RENTED = "rented"
    UNDER_MAINTENANCE = "under_maintenance"
    RESERVED = "reserved"
    
    @classmethod
    def get_all_statuses(cls) -> List[str]:
        """Get all available property statuses"""
        return [
            cls.AVAILABLE,
            cls.NOT_AVAILABLE,
            cls.RENTED,
            cls.UNDER_MAINTENANCE,
            cls.RESERVED
        ]
    
    @classmethod
    def is_valid(cls, status: str) -> bool:
        """Check if a status is valid"""
        return status in cls.get_all_statuses()

class PropertyManager:
    """Property management class"""
    
    def __init__(self):
        self.client = get_supabase_client()
    
    async def get_all_properties(self) -> List[Dict[str, Any]]:
        """Get all properties"""
        return await self.client.get_all_properties()
    
    async def get_property_by_id(self, property_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific property by ID"""
        try:
            result = await self.client._make_request("GET", f"properties?id=eq.{property_id}")
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting property {property_id}: {e}")
            return None
    
    async def get_properties_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get properties by status"""
        try:
            return await self.client._make_request("GET", f"properties?status=eq.{status}")
        except Exception as e:
            print(f"Error getting properties by status {status}: {e}")
            return []
    
    async def get_available_properties(self) -> List[Dict[str, Any]]:
        """Get all available properties"""
        return await self.get_properties_by_status(PropertyStatus.AVAILABLE)
    
    async def update_property_status(self, property_id: str, new_status: str) -> bool:
        """Update property status"""
        try:
            if not PropertyStatus.is_valid(new_status):
                raise ValueError(f"Invalid status: {new_status}")
            
            url = f"{self.client.supabase_url}/rest/v1/properties?id=eq.{property_id}"
            headers = self.client.headers.copy()
            headers["Prefer"] = "return=minimal"
            
            import httpx
            async with httpx.AsyncClient() as http_client:
                response = await http_client.patch(
                    url,
                    headers=headers,
                    json={
                        "status": new_status,
                        "updated_at": datetime.utcnow().isoformat()
                    }
                )
                
                if response.status_code >= 400:
                    raise Exception(f"Supabase API error: {response.status_code} - {response.text}")
            
            return True
        except Exception as e:
            print(f"Error updating property {property_id} status to {new_status}: {e}")
            return False
    
    async def update_property(self, property_id: str, updates: Dict[str, Any]) -> bool:
        """Update property with any fields"""
        try:
            # Add updated_at timestamp
            updates["updated_at"] = datetime.utcnow().isoformat()
            
            url = f"{self.client.supabase_url}/rest/v1/properties?id=eq.{property_id}"
            headers = self.client.headers.copy()
            headers["Prefer"] = "return=minimal"
            
            import httpx
            async with httpx.AsyncClient() as http_client:
                response = await http_client.patch(
                    url,
                    headers=headers,
                    json=updates
                )
                
                if response.status_code >= 400:
                    raise Exception(f"Supabase API error: {response.status_code} - {response.text}")
            
            return True
        except Exception as e:
            print(f"Error updating property {property_id}: {e}")
            return False
    
    async def create_property(self, property_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new property"""
        try:
            # Set default values
            property_data.setdefault("status", PropertyStatus.AVAILABLE)
            property_data.setdefault("country", "France")
            property_data.setdefault("rent_currency", "EUR")
            property_data.setdefault("bathroom_type", "shared")
            
            result = await self.client._make_request("POST", "properties", property_data)
            return result
        except Exception as e:
            print(f"Error creating property: {e}")
            return None
    
    async def delete_property(self, property_id: str) -> bool:
        """Delete a property"""
        try:
            await self.client._make_request("DELETE", f"properties?id=eq.{property_id}")
            return True
        except Exception as e:
            print(f"Error deleting property {property_id}: {e}")
            return False
    
    async def search_properties(self, search_term: str) -> List[Dict[str, Any]]:
        """Search properties by name or address"""
        return await self.client.search_properties(search_term)
    
    async def get_property_stats(self) -> Dict[str, int]:
        """Get property statistics by status"""
        try:
            all_properties = await self.get_all_properties()
            stats = {
                "total": len(all_properties),
                "available": 0,
                "not_available": 0,
                "rented": 0,
                "under_maintenance": 0,
                "reserved": 0
            }
            
            for prop in all_properties:
                status = prop.get("status", PropertyStatus.AVAILABLE)
                # Normalize status for comparison
                normalized_status = status.lower().replace(" ", "_")
                if normalized_status in stats:
                    stats[normalized_status] += 1
                else:
                    # If status doesn't match expected values, count as "not_available"
                    stats["not_available"] += 1
            
            return stats
        except Exception as e:
            print(f"Error getting property stats: {e}")
            return {}
    
    async def bulk_update_status(self, property_ids: List[str], new_status: str) -> Dict[str, Any]:
        """Bulk update property statuses"""
        if not PropertyStatus.is_valid(new_status):
            raise ValueError(f"Invalid status: {new_status}")
        
        results = {
            "total": len(property_ids),
            "successful": 0,
            "failed": 0,
            "failed_ids": []
        }
        
        for property_id in property_ids:
            success = await self.update_property_status(property_id, new_status)
            if success:
                results["successful"] += 1
            else:
                results["failed"] += 1
                results["failed_ids"].append(property_id)
        
        return results

# Global property manager instance
property_manager = None

def get_property_manager() -> PropertyManager:
    """Get or create property manager instance"""
    global property_manager
    if property_manager is None:
        property_manager = PropertyManager()
    return property_manager
