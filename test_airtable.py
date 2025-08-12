#!/usr/bin/env python3
"""
Test script for Airtable integration
"""

import os
from dotenv import load_dotenv
from app.utils import get_all_property_info, get_property_by_id, search_properties

def test_airtable_connection():
    """Test the Airtable connection and data retrieval"""
    print("🧪 Testing Airtable Integration")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check environment variables
    print("📋 Environment Variables:")
    print(f"  AIRTABLE_PERSONAL_ACCESS_TOKEN: {'SET' if os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN') else 'NOT SET'}")
    print(f"  BASE_ID: {'SET' if os.getenv('BASE_ID') else 'NOT SET'}")
    print(f"  PROPERTY_TABLE_NAME: {'SET' if os.getenv('PROPERTY_TABLE_NAME') else 'NOT SET'}")
    print()
    
    # Test getting all properties
    print("🏠 Testing get_all_property_info()...")
    try:
        properties = get_all_property_info()
        print(f"✅ Successfully retrieved {len(properties)} properties")
        
        if properties:
            print("\n📋 Sample Property Data:")
            for i, prop in enumerate(properties[:3]):  # Show first 3 properties
                print(f"  Property {i+1}:")
                if 'fields' in prop:
                    for key, value in prop['fields'].items():
                        print(f"    {key}: {value}")
                else:
                    print(f"    Raw data: {prop}")
                print()
        
    except Exception as e:
        print(f"❌ Error getting properties: {e}")
    
    # Test search functionality
    print("🔍 Testing search_properties()...")
    try:
        search_results = search_properties("Main")
        print(f"✅ Search for 'Main' returned {len(search_results)} results")
    except Exception as e:
        print(f"❌ Error searching properties: {e}")

if __name__ == "__main__":
    test_airtable_connection()
