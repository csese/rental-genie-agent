#!/usr/bin/env python3
"""
Test script for the new prompt management system
"""

import requests
import json

def test_prompt_management():
    """Test the prompt management functionality"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Prompt Management System")
    print("=" * 50)
    
    # Test 1: Get available prompts
    print("\n1. 📋 Getting available prompt versions...")
    try:
        response = requests.get(f"{base_url}/prompts")
        if response.status_code == 200:
            prompt_info = response.json()
            print(f"✅ Current version: {prompt_info['current_version']}")
            print(f"✅ Available versions: {prompt_info['available_versions']}")
            print(f"✅ Total versions: {prompt_info['total_versions']}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Test chat with v1 prompt
    print("\n2. 💬 Testing chat with v1 prompt...")
    try:
        response = requests.post(
            f"{base_url}/chat",
            json={
                "message": "Hi, I'm interested in renting a property",
                "prompt_version": "v1"
            },
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response: {data['response'][:100]}...")
            print(f"✅ Prompt version used: {data['prompt_version']}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Test chat with v2 prompt (current)
    print("\n3. 💬 Testing chat with v2 prompt...")
    try:
        response = requests.post(
            f"{base_url}/chat",
            json={
                "message": "Hi, I'm interested in renting a property",
                "prompt_version": "v2"
            },
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response: {data['response'][:100]}...")
            print(f"✅ Prompt version used: {data['prompt_version']}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Switch prompt version
    print("\n4. 🔄 Switching to v1 prompt...")
    try:
        response = requests.post(
            f"{base_url}/prompts/switch",
            json={"version": "v1"},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data['message']}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Test chat with switched prompt
    print("\n5. 💬 Testing chat with switched prompt...")
    try:
        response = requests.post(
            f"{base_url}/chat",
            json={
                "message": "Hi, I'm interested in renting a property"
            },
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response: {data['response'][:100]}...")
            print(f"✅ Prompt version used: {data['prompt_version']}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 6: Switch back to v2
    print("\n6. 🔄 Switching back to v2 prompt...")
    try:
        response = requests.post(
            f"{base_url}/prompts/switch",
            json={"version": "v2"},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data['message']}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def compare_prompts():
    """Compare the different prompt versions"""
    print("\n📊 Prompt Comparison")
    print("=" * 50)
    
    from app.prompts import prompt_manager
    
    print("\n🔍 V1 Prompt (Simple):")
    print("-" * 30)
    print(prompt_manager.get_prompt("v1"))
    
    print("\n🔍 V2 Prompt (Enhanced):")
    print("-" * 30)
    print(prompt_manager.get_prompt("v2"))

if __name__ == "__main__":
    test_prompt_management()
    compare_prompts()
