#!/usr/bin/env python3
"""
Script to help set up the correct Airtable table structure for Rental Genie
"""

import os
from dotenv import load_dotenv
from pyairtable import Api, Table

load_dotenv()

def check_current_table():
    """Check the current table structure"""
    print("🔍 Checking Current Airtable Table Structure")
    print("=" * 60)
    
    token = os.environ.get("AIRTABLE_PERSONAL_ACCESS_TOKEN")
    base_id = os.environ.get("BASE_ID")
    table_name = os.environ.get("TENANT_TABLE_NAME")
    
    if not all([token, base_id, table_name]):
        print("❌ Missing environment variables")
        return
    
    try:
        table = Table(token, base_id, table_name)
        records = table.all()
        
        if not records:
            print("⚠️  No records found in table")
            return
        
        first_record = records[0]
        fields = first_record.get('fields', {})
        
        print(f"📋 Current Table: {table_name}")
        print(f"📊 Total records: {len(records)}")
        print(f"🏷️  Current field names:")
        
        for field_name in fields.keys():
            print(f"   - {field_name}")
        
        # Check what's missing
        required_fields = [
            "Session ID", "Status", "Age", "Sex", "Occupation", 
            "Move In Date", "Rental Duration", "Guarantor Status",
            "Guarantor Details", "Viewing Interest", "Availability",
            "Language Preference", "Property Interest", "Application Date",
            "Lease Start Date", "Lease End Date", "Notes", "Created At",
            "Last Updated", "Conversation Turns"
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in fields:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"\n❌ Missing required fields:")
            for field in missing_fields:
                print(f"   - {field}")
        else:
            print(f"\n✅ All required fields are present!")
        
        return fields
        
    except Exception as e:
        print(f"❌ Error accessing table: {e}")
        return None

def suggest_migration():
    """Suggest how to migrate the current data"""
    print("\n🔄 Migration Suggestions")
    print("=" * 60)
    
    print("Based on your current table structure, here are your options:")
    print()
    print("Option 1: Add Session ID to Current Table")
    print("- Add a 'Session ID' field to your existing table")
    print("- This will allow the system to track conversations")
    print("- Existing records won't have session IDs until they interact")
    print()
    print("Option 2: Create New Tenants Table")
    print("- Create a new table called 'Tenants' with the proper structure")
    print("- This gives you a clean slate with the correct fields")
    print("- You can migrate existing data if needed")
    print()
    print("Option 3: Rename Current Table")
    print("- Rename your current table to 'Tenants'")
    print("- Add the missing fields to match the required structure")
    print()
    print("Recommended: Option 1 (Add Session ID field)")
    print("This is the quickest fix and preserves your existing data.")

def create_sample_tenant_record():
    """Create a sample tenant record structure"""
    print("\n📝 Sample Tenant Record Structure")
    print("=" * 60)
    
    sample_record = {
        "Session ID": "fb_5906947856087567_1756232941",
        "Status": "prospect",
        "Age": 28,
        "Sex": "Female",
        "Occupation": "Software Engineer",
        "Move In Date": "2024-03-15",
        "Rental Duration": "12 months",
        "Guarantor Status": "Yes",
        "Guarantor Details": "Father - Accountant",
        "Viewing Interest": True,
        "Availability": "Weekends",
        "Language Preference": "English",
        "Property Interest": "2-bedroom apartment",
        "Application Date": None,
        "Lease Start Date": None,
        "Lease End Date": None,
        "Notes": "Initial inquiry via Facebook Messenger",
        "Created At": "2024-01-15T10:30:00Z",
        "Last Updated": "2024-01-15T10:30:00Z",
        "Conversation Turns": 1
    }
    
    print("Here's what a complete tenant record should look like:")
    for field, value in sample_record.items():
        print(f"   {field}: {value}")
    
    return sample_record

def quick_fix_instructions():
    """Provide quick fix instructions"""
    print("\n🚀 Quick Fix Instructions")
    print("=" * 60)
    
    print("To fix the 'Unknown field names: session id' error:")
    print()
    print("1. Go to your Airtable base")
    print("2. Find your table (currently: tblO8k3E5rTXl4IAv)")
    print("3. Add a new field:")
    print("   - Name: 'Session ID' (exactly like this)")
    print("   - Type: 'Single line text'")
    print("   - Description: 'Unique session identifier'")
    print()
    print("4. Save the table")
    print("5. Test the Facebook integration again")
    print()
    print("That's it! The system will now be able to store session IDs.")
    print("Existing records will get session IDs when users interact with them.")

if __name__ == "__main__":
    print("🚀 Airtable Setup Helper")
    print("=" * 60)
    
    # Check current structure
    current_fields = check_current_table()
    
    # Provide suggestions
    suggest_migration()
    
    # Show sample structure
    create_sample_tenant_record()
    
    # Quick fix
    quick_fix_instructions()
    
    print("\n" + "=" * 60)
    print("✅ After making these changes, your Facebook integration should work!")
    print("📞 Test by sending a message to your Facebook page")
