#!/usr/bin/env python3
"""
Test Facebook access token and permissions
"""

import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def test_facebook_token():
    """Test Facebook access token"""
    access_token = os.environ.get("FACEBOOK_ACCESS_TOKEN")
    
    if not access_token:
        print("❌ FACEBOOK_ACCESS_TOKEN not set")
        return
    
    print("🔍 Testing Facebook Access Token")
    print("=" * 50)
    
    # Test 1: Get page info
    print("1. Testing page info...")
    try:
        url = f"https://graph.facebook.com/v23.0/me?access_token={access_token}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Page info: {data}")
                print(f"   Page ID: {data.get('id')}")
                print(f"   Page Name: {data.get('name')}")
            else:
                print(f"❌ Failed to get page info: {response.status_code}")
                print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error getting page info: {e}")
    
    # Test 2: Get page permissions
    print("\n2. Testing page permissions...")
    try:
        url = f"https://graph.facebook.com/v23.0/me/permissions?access_token={access_token}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Page permissions: {data}")
                
                # Check for messaging permissions
                permissions = data.get('data', [])
                messaging_permissions = [p for p in permissions if 'messaging' in p.get('permission', '')]
                
                if messaging_permissions:
                    print("✅ Messaging permissions found:")
                    for perm in messaging_permissions:
                        print(f"   - {perm['permission']}: {perm['status']}")
                else:
                    print("❌ No messaging permissions found")
                    print("   Available permissions:")
                    for perm in permissions:
                        print(f"   - {perm['permission']}: {perm['status']}")
            else:
                print(f"❌ Failed to get permissions: {response.status_code}")
                print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error getting permissions: {e}")
    
    # Test 3: Test messaging endpoint
    print("\n3. Testing messaging endpoint...")
    try:
        url = f"https://graph.facebook.com/v23.0/me/messages?access_token={access_token}"
        payload = {
            "recipient": {"id": "test_user_id"},
            "message": {"text": "Test message"}
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                print("✅ Messaging endpoint works!")
            else:
                print(f"❌ Messaging endpoint failed: {response.status_code}")
                print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing messaging: {e}")
    
    print("\n" + "=" * 50)
    print("📝 Recommendations:")
    print("1. Make sure you're using a Page Access Token (not User Access Token)")
    print("2. Ensure the page has messaging permissions enabled")
    print("3. Check that the page is published and active")
    print("4. Verify the app has been approved for messaging")

if __name__ == "__main__":
    asyncio.run(test_facebook_token())
