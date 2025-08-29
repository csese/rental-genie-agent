#!/usr/bin/env python3
"""
Script to update property statuses in Supabase
Changes all properties with status "Available" to "available"
"""

import asyncio
import os
import httpx
from dotenv import load_dotenv
from app.supabase_client import get_supabase_client

load_dotenv()

async def update_property_statuses():
    """Update all property statuses from 'Available' to 'available'"""
    try:
        client = get_supabase_client()
        
        # Get all properties
        print("Fetching all properties...")
        properties = await client.get_all_properties()
        
        if not properties:
            print("No properties found in the database.")
            return
        
        print(f"Found {len(properties)} properties")
        
        
        
        # Update each property
        updated_count = 0
        for prop in properties:
            try:
                property_id = prop.get('id')
                print(f"Updating property {property_id} ({prop.get('name', 'Unknown')}) from 'Available' to 'available'")
                
                # Update the property status using PATCH method
                url = f"{client.supabase_url}/rest/v1/properties?id=eq.{property_id}"
                headers = client.headers
                headers["Prefer"] = "return=minimal"
                
                async with httpx.AsyncClient() as http_client:
                    response = await http_client.patch(
                        url, 
                        headers=headers,
                        json={"status": "not_available"}
                    )
                    
                    if response.status_code >= 400:
                        raise Exception(f"Supabase API error: {response.status_code} - {response.text}")
                
                updated_count += 1
                print(f"✓ Successfully updated property {property_id}")
                
            except Exception as e:
                print(f"✗ Error updating property {property_id}: {e}")
        
        print(f"\nUpdate complete! Successfully updated {updated_count} out of {len(properties)} properties.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(update_property_statuses())
