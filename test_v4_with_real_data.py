#!/usr/bin/env python3
"""
Test script to verify V4 prompt with real property data
"""

import requests
import json
import time

def test_v4_with_real_properties():
    """Test the v4 prompt with real property data from database"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing V4 Prompt with Real Property Data")
    print("=" * 60)
    
    # Test 1: Check if properties are loaded from database
    print("\n1. 🏠 Checking real property data...")
    try:
        response = requests.get(f"{base_url}/properties")
        if response.status_code == 200:
            data = response.json()
            properties = data.get('properties', [])
            print(f"✅ Found {len(properties)} properties in database")
            
            # Check for Annemasse properties (what the user was asking for)
            annemasse_properties = [p for p in properties if 'Annemasse' in p.get('fields', {}).get('Address', '')]
            print(f"✅ Found {len(annemasse_properties)} properties in Annemasse")
            
            if annemasse_properties:
                print("\n📋 Annemasse Properties:")
                for i, prop in enumerate(annemasse_properties[:3], 1):
                    fields = prop.get('fields', {})
                    print(f"   {i}. {fields.get('Name', 'Unknown')}")
                    print(f"      Address: {fields.get('Address', 'Unknown')}")
                    print(f"      Rent: {fields.get('Rent', 'Unknown')}")
                    print(f"      Status: {fields.get('Status', 'Unknown')}")
                    print()
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Test V4 prompt with property interest
    print("\n2. 💬 Testing V4 prompt with property interest...")
    session_id = f"test_v4_real_{int(time.time())}"
    
    try:
        response = requests.post(
            f"{base_url}/chat",
            json={
                "message": "Je suis intéressé par une chambre à Annemasse en colocation",
                "session_id": session_id,
                "prompt_version": "v4"
            },
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response: {data['response'][:300]}...")
            
            # Check if response mentions real properties
            if "Annemasse" in data['response']:
                print("✅ Response mentions Annemasse properties")
            if "660" in data['response'] or "675" in data['response'] or "690" in data['response']:
                print("✅ Response includes real rent prices from database")
            if "Rue des Amoureux" in data['response'] or "Rue du Saget" in data['response']:
                print("✅ Response includes real addresses from database")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Test progressive information gathering
    print("\n3. 📝 Testing progressive information gathering...")
    try:
        response = requests.post(
            f"{base_url}/chat",
            json={
                "message": "J'ai 28 ans et je veux une chambre à partir du 1er septembre",
                "session_id": session_id,
                "prompt_version": "v4"
            },
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response: {data['response'][:300]}...")
            
            # Check if it asks for only 1-2 more details instead of all
            if "occupation" in data['response'].lower() or "profession" in data['response'].lower():
                print("✅ Asks for occupation (progressive gathering)")
            if "garant" in data['response'].lower() or "visale" in data['response'].lower():
                print("✅ Asks for guarantor info (progressive gathering)")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Compare with V3 behavior
    print("\n4. 🔍 Comparing V3 vs V4 behavior...")
    session_id_v3 = f"test_v3_{int(time.time())}"
    
    try:
        response = requests.post(
            f"{base_url}/chat",
            json={
                "message": "Je suis intéressé par une chambre à Annemasse en colocation",
                "session_id": session_id_v3,
                "prompt_version": "v3"
            },
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ V3 Response: {data['response'][:200]}...")
            print("✅ V3 should ask for all missing info upfront")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Test Complete")

if __name__ == "__main__":
    test_v4_with_real_properties()
