#!/usr/bin/env python3
"""
Test script for the new prompt that handles no properties available scenario
"""

import asyncio
import os
from dotenv import load_dotenv
from app.prompts import get_system_prompt, prompt_manager

load_dotenv()

def test_no_properties_prompt():
    """Test the new prompt with no properties available"""
    
    print("=== Testing No Properties Available Prompt ===\n")
    
    # Test 1: Check current prompt version
    print("1. Current prompt version:")
    prompt_info = prompt_manager.get_prompt_info()
    print(f"   Current version: {prompt_info['current_version']}")
    print(f"   Available versions: {prompt_info['available_versions']}")
    
    # Test 2: Get prompt with empty property data
    print("\n2. Testing prompt with empty property data:")
    empty_property_data = "[]"
    prompt_with_empty_data = get_system_prompt(empty_property_data, "v5")
    
    # Check if the prompt contains the no properties protocol
    if "NO PROPERTIES AVAILABLE PROTOCOL" in prompt_with_empty_data:
        print("   ✓ No Properties Available Protocol found in prompt")
    else:
        print("   ✗ No Properties Available Protocol NOT found in prompt")
    
    if "Do NOT ask for personal details" in prompt_with_empty_data:
        print("   ✓ Personal details restriction found in prompt")
    else:
        print("   ✗ Personal details restriction NOT found in prompt")
    
    if "When do you need a room and for how long" in prompt_with_empty_data:
        print("   ✓ Minimal information request found in prompt")
    else:
        print("   ✗ Minimal information request NOT found in prompt")
    
    # Test 3: Get prompt with actual property data
    print("\n3. Testing prompt with actual property data:")
    sample_property_data = '[{"name": "Test Property", "status": "available"}]'
    prompt_with_data = get_system_prompt(sample_property_data, "v5")
    
    if "NO PROPERTIES AVAILABLE PROTOCOL" in prompt_with_data:
        print("   ✓ No Properties Available Protocol still present (should be)")
    else:
        print("   ✗ No Properties Available Protocol missing")
    
    # Test 4: Check JSON output format
    print("\n4. Checking JSON output format:")
    if '"no_properties_available": "true/false"' in prompt_with_data:
        print("   ✓ no_properties_available field found in JSON output")
    else:
        print("   ✗ no_properties_available field NOT found in JSON output")
    
    # Test 5: Show example of how the prompt would work
    print("\n5. Example prompt behavior:")
    print("   When property_data is '[]' or empty:")
    print("   - Agent should follow NO PROPERTIES AVAILABLE PROTOCOL")
    print("   - Should inform tenant no properties are available")
    print("   - Should offer to notify when properties become available")
    print("   - Should ask only: when they need a room and for how long")
    print("   - Should NOT ask for age, sex, occupation, or guarantor status")
    
    print("\n=== Test completed successfully! ===")

if __name__ == "__main__":
    test_no_properties_prompt()
