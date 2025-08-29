#!/usr/bin/env python3
"""
Integration test for LLM-based extraction within the full message handling pipeline
"""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Load environment variables
load_dotenv()

def test_integration():
    """Test the full message handling pipeline with LLM extraction"""
    
    # Import the message handling function
    from agent import handle_message
    
    # Sample property data
    property_data = """[
        {
            "fields": {
                "Name": "Sample Property",
                "Address": "123 Main St",
                "Rent": "$1500/month",
                "Available": "January 2024"
            }
        }
    ]"""
    
    # Test cases with session tracking
    test_cases = [
        {
            "message": "Hello, I'm interested in renting an apartment. I'm 25 years old and work as a software engineer.",
            "session_id": "test_session_1",
            "description": "Initial contact with basic information"
        },
        {
            "message": "I can move in next month and need a 12-month lease.",
            "session_id": "test_session_1",
            "description": "Follow-up with rental details"
        },
        {
            "message": "Je suis étudiant, 22 ans, pour 9 mois à partir d'octobre.",
            "session_id": "test_session_2",
            "description": "French message with comprehensive information"
        },
        {
            "message": "I'm 25 now.",
            "session_id": "test_session_1",
            "description": "Age correction in existing session"
        }
    ]
    
    print("=== Integration Test Suite ===")
    print(f"OpenAI API Key available: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")
    print()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['description']}")
        print(f"Session ID: {test_case['session_id']}")
        print(f"Message: '{test_case['message']}'")
        
        try:
            # Test message handling
            response = handle_message(
                user_input=test_case['message'],
                property_data=property_data,
                session_id=test_case['session_id'],
                prompt_version="current"
            )
            
            print(f"Agent Response: '{response[:200]}...'")
            
            # Get conversation memory info
            from agent import get_conversation_memory_info
            memory_info = get_conversation_memory_info(test_case['session_id'])
            
            print(f"Profile Complete: {memory_info.get('profile_complete', False)}")
            print(f"Missing Info: {memory_info.get('missing_info', [])}")
            print(f"Conversation Turns: {memory_info.get('conversation_turns', 0)}")
            
            print("-" * 50)
            
        except Exception as e:
            print(f"❌ Error in test {i}: {e}")
            import traceback
            traceback.print_exc()
            print("-" * 50)
    
    print("=== Integration Test Complete ===")

if __name__ == "__main__":
    test_integration()
