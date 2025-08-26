#!/usr/bin/env python3
"""
Migration script to move data from Airtable to Supabase
"""

import os
import asyncio
from dotenv import load_dotenv
from pyairtable import Table
from supabase_client import get_supabase_client

load_dotenv()

async def migrate_airtable_to_supabase():
    """Migrate data from Airtable to Supabase"""
    print("🚀 Starting Airtable to Supabase Migration")
    print("=" * 60)
    
    # Initialize clients
    try:
        # Airtable client
        airtable_token = os.environ.get("AIRTABLE_PERSONAL_ACCESS_TOKEN")
        base_id = os.environ.get("BASE_ID")
        table_name = os.environ.get("TENANT_TABLE_NAME")
        
        if not all([airtable_token, base_id, table_name]):
            print("❌ Missing Airtable environment variables")
            return
        
        airtable_table = Table(airtable_token, base_id, table_name)
        
        # Supabase client
        supabase = get_supabase_client()
        
        print("✅ Clients initialized successfully")
        
    except Exception as e:
        print(f"❌ Error initializing clients: {e}")
        return
    
    # Migrate properties (if they exist in Airtable)
    print("\n📋 Migrating Properties...")
    try:
        # Check if properties table exists in Airtable
        properties_table_name = os.environ.get("PROPERTY_TABLE_NAME")
        if properties_table_name:
            properties_table = Table(airtable_token, base_id, properties_table_name)
            airtable_properties = properties_table.all()
            
            print(f"Found {len(airtable_properties)} properties in Airtable")
            
            for prop in airtable_properties:
                fields = prop.get('fields', {})
                
                # Map Airtable fields to Supabase structure
                supabase_property = {
                    "name": fields.get("Name", fields.get("name", "Unknown Property")),
                    "address_street": fields.get("Address", fields.get("address_street", "")),
                    "city": fields.get("City", fields.get("city", "")),
                    "zip_code": fields.get("Zip Code", fields.get("zip_code", "")),
                    "description": fields.get("Description", fields.get("description", "")),
                    "status": fields.get("Status", fields.get("status", "available")),
                    "rent_amount": fields.get("Rent", fields.get("rent_amount")),
                    "surface_area": fields.get("Surface Area", fields.get("surface_area")),
                    "room_count": fields.get("Rooms", fields.get("room_count")),
                    "availability_date": fields.get("Available", fields.get("availability_date"))
                }
                
                # Remove None values
                supabase_property = {k: v for k, v in supabase_property.items() if v is not None}
                
                try:
                    await supabase._make_request("POST", "properties", supabase_property)
                    print(f"✅ Migrated property: {supabase_property.get('name')}")
                except Exception as e:
                    print(f"❌ Failed to migrate property: {e}")
        
        else:
            print("No properties table found, skipping properties migration")
            
    except Exception as e:
        print(f"❌ Error migrating properties: {e}")
    
    # Migrate tenants
    print("\n👥 Migrating Tenants...")
    try:
        airtable_tenants = airtable_table.all()
        print(f"Found {len(airtable_tenants)} tenants in Airtable")
        
        migrated_count = 0
        skipped_count = 0
        
        for tenant in airtable_tenants:
            fields = tenant.get('fields', {})
            
            # Generate a session ID if none exists
            session_id = fields.get("Session ID") or f"migrated_{tenant.get('id')}"
            
            # Map Airtable fields to Supabase structure
            supabase_tenant = {
                "session_id": session_id,
                "status": "prospect",  # Default status for migrated tenants
                "age": fields.get("Age", fields.get("age")),
                "sex": fields.get("Sex", fields.get("Gender", fields.get("sex"))),
                "occupation": fields.get("Occupation", fields.get("occupation")),
                "move_in_date": fields.get("Move In Date", fields.get("move_in_date")),
                "rental_duration": fields.get("Rental Duration", fields.get("rental_duration")),
                "guarantor_status": fields.get("Guarantor Status", fields.get("guarantor_status")),
                "guarantor_details": fields.get("Guarantor Details", fields.get("guarantor_details")),
                "viewing_interest": fields.get("Viewing Interest", fields.get("viewing_interest", False)),
                "availability": fields.get("Availability", fields.get("availability")),
                "language_preference": fields.get("Language Preference", fields.get("language_preference")),
                "property_interest": fields.get("Property Interest", fields.get("property_interest")),
                "notes": fields.get("Notes", fields.get("notes")),
                "profile_data": {
                    # Store any additional fields in the flexible JSON structure
                    "first_name": fields.get("First name", fields.get("first_name")),
                    "email": fields.get("email"),
                    "phone": fields.get("Phone number", fields.get("phone")),
                    "address": fields.get("address"),
                    "postal_code": fields.get("Postal Code", fields.get("postal_code")),
                    "country": fields.get("Country", fields.get("country")),
                    "date_of_birth": fields.get("Date of Birth", fields.get("date_of_birth"))
                }
            }
            
            # Remove None values from main fields
            supabase_tenant = {k: v for k, v in supabase_tenant.items() if v is not None}
            
            # Clean up profile_data (remove None values)
            if supabase_tenant.get("profile_data"):
                supabase_tenant["profile_data"] = {
                    k: v for k, v in supabase_tenant["profile_data"].items() if v is not None
                }
            
            try:
                await supabase._make_request("POST", "tenants", supabase_tenant)
                migrated_count += 1
                print(f"✅ Migrated tenant: {session_id}")
            except Exception as e:
                print(f"❌ Failed to migrate tenant {session_id}: {e}")
                skipped_count += 1
        
        print(f"\n📊 Migration Summary:")
        print(f"   ✅ Successfully migrated: {migrated_count}")
        print(f"   ❌ Skipped: {skipped_count}")
        
    except Exception as e:
        print(f"❌ Error migrating tenants: {e}")
    
    print("\n🎉 Migration completed!")
    print("\n📝 Next steps:")
    print("1. Update your environment variables to use Supabase")
    print("2. Test the new Supabase integration")
    print("3. Update your code to use the new Supabase client")

async def test_supabase_connection():
    """Test Supabase connection and basic operations"""
    print("🔍 Testing Supabase Connection")
    print("=" * 40)
    
    try:
        supabase = get_supabase_client()
        
        # Test basic operations
        print("Testing property retrieval...")
        properties = await supabase.get_all_properties()
        print(f"✅ Found {len(properties)} properties")
        
        print("Testing tenant retrieval...")
        tenants = await supabase.get_all_tenants()
        print(f"✅ Found {len(tenants)} tenants")
        
        print("✅ Supabase connection test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection test failed: {e}")
        return False

async def create_sample_data():
    """Create sample data in Supabase for testing"""
    print("📝 Creating Sample Data in Supabase")
    print("=" * 40)
    
    try:
        supabase = get_supabase_client()
        
        # Create sample tenant
        sample_tenant = {
            "session_id": "test_session_123",
            "status": "prospect",
            "age": 28,
            "sex": "Female",
            "occupation": "Software Engineer",
            "move_in_date": "2024-03-15",
            "rental_duration": "12 months",
            "guarantor_status": "Yes",
            "guarantor_details": "Father - Accountant",
            "viewing_interest": True,
            "availability": "Weekends",
            "language_preference": "English",
            "property_interest": "2-bedroom apartment",
            "notes": "Sample tenant for testing"
        }
        
        await supabase._make_request("POST", "tenants", sample_tenant)
        print("✅ Created sample tenant")
        
        # Create sample chat session
        sample_session = {
            "session_id": "test_session_123",
            "platform": "facebook",
            "user_id": "test_user_456",
            "status": "active"
        }
        
        await supabase._make_request("POST", "chat_sessions", sample_session)
        print("✅ Created sample chat session")
        
        # Create sample messages
        sample_messages = [
            {
                "session_id": "test_session_123",
                "message_type": "user",
                "content": "Hi, I'm interested in renting a property",
                "extracted_info": {"intent": "property_inquiry"}
            },
            {
                "session_id": "test_session_123",
                "message_type": "agent",
                "content": "Hello! I'd be happy to help you find a property. What are you looking for?",
                "extracted_info": {"response_type": "greeting"}
            }
        ]
        
        for message in sample_messages:
            await supabase._make_request("POST", "conversation_messages", message)
        
        print("✅ Created sample messages")
        print("✅ Sample data creation completed!")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")

if __name__ == "__main__":
    print("🚀 Supabase Migration Tool")
    print("=" * 60)
    
    # Check environment variables
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY", 
        "SUPABASE_SERVICE_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing Supabase environment variables: {missing_vars}")
        print("\nPlease set these variables:")
        for var in missing_vars:
            print(f"   {var}")
        exit(1)
    
    # Run tests and migration
    async def main():
        # Test connection first
        if await test_supabase_connection():
            # Create sample data
            await create_sample_data()
            
            # Ask if user wants to migrate
            print("\n" + "=" * 60)
            response = input("Do you want to migrate data from Airtable? (y/n): ")
            
            if response.lower() == 'y':
                await migrate_airtable_to_supabase()
            else:
                print("Skipping migration. You can run it later with: python migrate_to_supabase.py")
        else:
            print("❌ Cannot proceed without working Supabase connection")
    
    asyncio.run(main())
