#!/usr/bin/env python3
"""
Debug script to check property data loading
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

load_dotenv()

def check_environment():
    """Check if required environment variables are set"""
    print("🔍 Checking Environment Variables")
    print("=" * 50)
    
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY", 
        "SUPABASE_SERVICE_KEY"
    ]
    
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: {'*' * 10}...{value[-4:] if len(value) > 4 else value}")
        else:
            print(f"❌ {var}: NOT SET")
    
    print()

def test_supabase_connection():
    """Test Supabase connection"""
    print("🔗 Testing Supabase Connection")
    print("=" * 50)
    
    try:
        from app.supabase_client import get_supabase_client
        client = get_supabase_client()
        print("✅ Supabase client created successfully")
        print(f"   URL: {client.supabase_url}")
        print(f"   Anon Key: {'*' * 10}...{client.supabase_key[-4:] if client.supabase_key else 'None'}")
        print(f"   Service Key: {'*' * 10}...{client.service_key[-4:] if client.service_key else 'None'}")
        return client
    except Exception as e:
        print(f"❌ Error creating Supabase client: {e}")
        return None

async def test_property_loading():
    """Test property data loading"""
    print("\n🏠 Testing Property Data Loading")
    print("=" * 50)
    
    try:
        from app.supabase_utils import get_all_property_info
        
        print("Loading properties...")
        properties = get_all_property_info()
        
        if properties:
            print(f"✅ Successfully loaded {len(properties)} properties")
            print("\n📋 Property Details:")
            for i, prop in enumerate(properties[:3], 1):  # Show first 3
                fields = prop.get('fields', {})
                print(f"   {i}. {fields.get('Name', 'Unknown')}")
                print(f"      Address: {fields.get('Address', 'Unknown')}")
                print(f"      Rent: {fields.get('Rent', 'Unknown')}")
                print(f"      Available: {fields.get('Available', 'Unknown')}")
                print()
        else:
            print("❌ No properties loaded")
            
    except Exception as e:
        print(f"❌ Error loading properties: {e}")
        import traceback
        traceback.print_exc()

async def test_direct_supabase_query():
    """Test direct Supabase query"""
    print("\n🔍 Testing Direct Supabase Query")
    print("=" * 50)
    
    try:
        from app.supabase_client import get_supabase_client
        client = get_supabase_client()
        
        print("Querying properties table directly...")
        properties = await client.get_all_properties()
        
        if properties:
            print(f"✅ Direct query returned {len(properties)} properties")
            print("\n📋 Raw Property Data:")
            for i, prop in enumerate(properties[:3], 1):  # Show first 3
                print(f"   {i}. ID: {prop.get('id', 'Unknown')}")
                print(f"      Name: {prop.get('name', 'Unknown')}")
                print(f"      Address: {prop.get('address_street', 'Unknown')}, {prop.get('city', 'Unknown')}")
                print(f"      Rent: {prop.get('rent_amount', 'Unknown')} {prop.get('rent_currency', 'EUR')}")
                print(f"      Status: {prop.get('status', 'Unknown')}")
                print()
        else:
            print("❌ Direct query returned no properties")
            
    except Exception as e:
        print(f"❌ Error in direct query: {e}")
        import traceback
        traceback.print_exc()

def test_property_endpoint():
    """Test the /properties endpoint"""
    print("\n🌐 Testing /properties Endpoint")
    print("=" * 50)
    
    try:
        import requests
        
        # Start the server if not running
        base_url = "http://localhost:8000"
        
        response = requests.get(f"{base_url}/properties")
        
        if response.status_code == 200:
            data = response.json()
            properties = data.get('properties', [])
            print(f"✅ Endpoint returned {len(properties)} properties")
            
            if properties:
                print("\n📋 Endpoint Property Data:")
                for i, prop in enumerate(properties[:3], 1):
                    fields = prop.get('fields', {})
                    print(f"   {i}. {fields.get('Name', 'Unknown')}")
                    print(f"      Address: {fields.get('Address', 'Unknown')}")
                    print(f"      Rent: {fields.get('Rent', 'Unknown')}")
                    print()
            else:
                print("❌ Endpoint returned no properties")
        else:
            print(f"❌ Endpoint error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")

async def main():
    """Main diagnostic function"""
    print("🔧 Property Data Diagnostic Tool")
    print("=" * 60)
    
    # Check environment
    check_environment()
    
    # Test Supabase connection
    client = test_supabase_connection()
    
    if client:
        # Test direct property loading
        await test_direct_supabase_query()
        
        # Test property loading through utils
        await test_property_loading()
    
    # Test endpoint
    test_property_endpoint()
    
    print("\n" + "=" * 60)
    print("🏁 Diagnostic Complete")

if __name__ == "__main__":
    asyncio.run(main())
