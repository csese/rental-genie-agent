#!/usr/bin/env python3
"""
Debug script to check Airtable configuration and field names
"""

import os
from dotenv import load_dotenv
from pyairtable import Api, Table

load_dotenv()

def check_airtable_config():
    """Check Airtable configuration and field names"""
    print("🔍 Checking Airtable Configuration")
    print("=" * 50)
    
    # Check environment variables
    required_vars = [
        "AIRTABLE_PERSONAL_ACCESS_TOKEN",
        "BASE_ID", 
        "TENANT_TABLE_NAME"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.environ.get(var)
        if not value:
            missing_vars.append(var)
        else:
            print(f"✅ {var}: {'*' * (len(value) - 4) + value[-4:] if len(value) > 4 else '***'}")
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False
    
    try:
        # Get table
        token = os.environ.get("AIRTABLE_PERSONAL_ACCESS_TOKEN")
        base_id = os.environ.get("BASE_ID")
        table_name = os.environ.get("TENANT_TABLE_NAME")
        
        table = Table(token, base_id, table_name)
        
        # Get all records to see field names
        records = table.all()
        
        if not records:
            print("⚠️  No records found in table")
            return True
        
        # Get field names from first record
        first_record = records[0]
        fields = first_record.get('fields', {})
        
        print(f"\n📋 Table: {table_name}")
        print(f"📊 Total records: {len(records)}")
        print(f"🏷️  Available field names:")
        
        for field_name in fields.keys():
            print(f"   - {field_name}")
        
        # Check for session ID field
        session_id_fields = [name for name in fields.keys() if 'session' in name.lower() or 'id' in name.lower()]
        if session_id_fields:
            print(f"\n🎯 Potential Session ID fields: {session_id_fields}")
        else:
            print(f"\n⚠️  No obvious Session ID field found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error accessing Airtable: {e}")
        return False

def check_facebook_config():
    """Check Facebook configuration"""
    print("\n🔍 Checking Facebook Configuration")
    print("=" * 50)
    
    facebook_vars = [
        "FACEBOOK_ACCESS_TOKEN",
        "FACEBOOK_APP_SECRET", 
        "FACEBOOK_VERIFY_TOKEN"
    ]
    
    for var in facebook_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: {'*' * (len(value) - 4) + value[-4:] if len(value) > 4 else '***'}")
        else:
            print(f"❌ {var}: Not set")
    
    # Test Facebook access token if available
    access_token = os.environ.get("FACEBOOK_ACCESS_TOKEN")
    if access_token:
        print(f"\n🔗 Testing Facebook access token...")
        try:
            import httpx
            import asyncio
            
            async def test_token():
                url = f"https://graph.facebook.com/v23.0/me?access_token={access_token}"
                async with httpx.AsyncClient() as client:
                    response = await client.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        print(f"✅ Token valid - Page: {data.get('name', 'Unknown')} (ID: {data.get('id', 'Unknown')})")
                        return True
                    else:
                        print(f"❌ Token invalid: {response.text}")
                        return False
            
            asyncio.run(test_token())
        except Exception as e:
            print(f"❌ Error testing token: {e}")

if __name__ == "__main__":
    print("🚀 Rental Genie Debug Tool")
    print("=" * 50)
    
    # Check Airtable
    airtable_ok = check_airtable_config()
    
    # Check Facebook
    check_facebook_config()
    
    print("\n" + "=" * 50)
    if airtable_ok:
        print("✅ Airtable configuration looks good!")
    else:
        print("❌ Airtable configuration needs attention")
    
    print("\n📝 Next steps:")
    print("1. If Airtable field names don't match, update your Airtable table")
    print("2. Set Facebook environment variables in Heroku")
    print("3. Make sure your Facebook app has Messenger permissions")
    print("4. Use a Page Access Token, not a User Access Token")
