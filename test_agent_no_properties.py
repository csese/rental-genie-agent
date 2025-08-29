#!/usr/bin/env python3
"""
Test script to verify the agent handles no properties available scenario
"""

import asyncio
import os
from dotenv import load_dotenv
from app.agent import handle_message

load_dotenv()

def test_agent_no_properties():
    """Test the agent with no properties available"""
    
    print("=== Testing Agent with No Properties Available ===\n")
    
    # Test 1: Test with empty property data
    print("1. Testing with empty property data:")
    empty_property_data = "[]"
    
    test_messages = [
        "Bonjour, je cherche une chambre",
        "Hello, I'm looking for a room",
        "J'ai besoin d'une colocation",
        "I need accommodation"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n   Test {i}: '{message}'")
        try:
            response = handle_message(message, empty_property_data, session_id=f"test_session_{i}")
            print(f"   Response: {response[:200]}...")
            
            # Check if response indicates no properties available
            if any(keyword in response.lower() for keyword in ["no properties", "not available", "pas disponible", "aucune propriété"]):
                print("   ✓ Correctly indicates no properties available")
            else:
                print("   ⚠️  Response doesn't clearly indicate no properties available")
                
        except Exception as e:
            print(f"   ✗ Error: {e}")
    
    # Test 2: Test with actual property data (for comparison)
    print("\n2. Testing with actual property data (for comparison):")
    sample_property_data = '[{"name": "Test Property", "status": "available", "rent_amount": 1000}]'
    
    try:
        response = handle_message("Bonjour, je cherche une chambre", sample_property_data, session_id="test_session_compare")
        print(f"   Response with properties: {response[:200]}...")
        
        if any(keyword in response.lower() for keyword in ["test property", "1000", "available"]):
            print("   ✓ Correctly mentions available properties")
        else:
            print("   ⚠️  Response doesn't mention available properties")
            
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n=== Test completed! ===")

if __name__ == "__main__":
    test_agent_no_properties()
