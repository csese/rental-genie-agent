#!/usr/bin/env python3
"""
Test script for property management functionality
"""

import asyncio
import os
from dotenv import load_dotenv
from app.property_management import get_property_manager, PropertyStatus

load_dotenv()

async def test_property_management():
    """Test property management functionality"""
    try:
        property_manager = get_property_manager()
        
        print("=== Property Management Test ===\n")
        
        # Test 1: Get all properties
        print("1. Getting all properties...")
        properties = await property_manager.get_all_properties()
        print(f"   Found {len(properties)} properties")
        
        if properties:
            # Show first property details
            first_prop = properties[0]
            print(f"   First property: {first_prop.get('name', 'Unknown')} - Status: {first_prop.get('status', 'Unknown')}")
        
        # Test 2: Get available properties
        print("\n2. Getting available properties...")
        available_properties = await property_manager.get_available_properties()
        print(f"   Found {len(available_properties)} available properties")
        
        # Test 3: Get property statistics
        print("\n3. Getting property statistics...")
        stats = await property_manager.get_property_stats()
        print(f"   Property stats: {stats}")
        
        # Test 4: Get property status info
        print("\n4. Available property statuses:")
        statuses = PropertyStatus.get_all_statuses()
        for status in statuses:
            print(f"   - {status}")
        
        # Test 5: Test status validation
        print("\n5. Testing status validation...")
        valid_status = PropertyStatus.is_valid("available")
        invalid_status = PropertyStatus.is_valid("invalid_status")
        print(f"   'available' is valid: {valid_status}")
        print(f"   'invalid_status' is valid: {invalid_status}")
        
        print("\n=== Test completed successfully! ===")
        
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    asyncio.run(test_property_management())
