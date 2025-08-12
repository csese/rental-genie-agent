#!/usr/bin/env python3
"""
Comprehensive tests for conversation memory system
Tests multi-turn conversations and information gathering
"""

import requests
import json
import time

def test_conversation_memory():
    """Test the conversation memory system with multi-turn conversations"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Conversation Memory System")
    print("=" * 60)
    
    # Test 1: Start a new conversation
    print("\n1. 🆕 Starting new conversation...")
    session_id = f"test_session_{int(time.time())}"
    
    try:
        response = requests.post(
            f"{base_url}/chat",
            json={
                "message": "Hi, I'm interested in renting a property",
                "session_id": session_id,
                "user_id": "test_user_123"
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response: {data['response'][:100]}...")
            print(f"✅ Session ID: {data['session_id']}")
            print(f"✅ Profile Complete: {data['profile_complete']}")
        else:
            print(f"❌ Error: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Test 2: Provide age and occupation
    print("\n2. 👤 Providing age and occupation...")
    try:
        response = requests.post(
            f"{base_url}/chat",
            json={
                "message": "I am 25 years old and work as a software engineer",
                "session_id": session_id
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response: {data['response'][:100]}...")
            print(f"✅ Profile Complete: {data['profile_complete']}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Provide move-in date
    print("\n3. 📅 Providing move-in date...")
    try:
        response = requests.post(
            f"{base_url}/chat",
            json={
                "message": "I want to move in on March 1st",
                "session_id": session_id
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response: {data['response'][:100]}...")
            print(f"✅ Profile Complete: {data['profile_complete']}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Provide rental duration
    print("\n4. ⏰ Providing rental duration...")
    try:
        response = requests.post(
            f"{base_url}/chat",
            json={
                "message": "I can stay for 12 months",
                "session_id": session_id
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response: {data['response'][:100]}...")
            print(f"✅ Profile Complete: {data['profile_complete']}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Provide sex/gender
    print("\n5. 👥 Providing sex/gender...")
    try:
        response = requests.post(
            f"{base_url}/chat",
            json={
                "message": "I am male",
                "session_id": session_id
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response: {data['response'][:100]}...")
            print(f"✅ Profile Complete: {data['profile_complete']}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 6: Provide guarantor information
    print("\n6. 🏦 Providing guarantor information...")
    try:
        response = requests.post(
            f"{base_url}/chat",
            json={
                "message": "I have a guarantor, my father who works as an accountant",
                "session_id": session_id
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response: {data['response'][:100]}...")
            print(f"✅ Profile Complete: {data['profile_complete']}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 7: Check conversation memory
    print("\n7. 📊 Checking conversation memory...")
    try:
        response = requests.get(f"{base_url}/conversation/{session_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Session ID: {data['session_id']}")
            print(f"✅ Profile Complete: {data['profile_complete']}")
            print(f"✅ Missing Info: {data['missing_info']}")
            print(f"✅ Conversation Turns: {data['conversation_turns']}")
            print(f"✅ Last Updated: {data['last_updated']}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 8: Test that agent remembers previous information
    print("\n8. 🧠 Testing agent memory (should not ask for age again)...")
    try:
        response = requests.post(
            f"{base_url}/chat",
            json={
                "message": "What information do you have about me?",
                "session_id": session_id
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response: {data['response'][:150]}...")
            # Check if the response mentions the age we provided
            if "25" in data['response']:
                print("✅ Agent remembered the age!")
            else:
                print("⚠️  Agent may not have referenced the stored age")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 9: Test viewing interest
    print("\n9. 👀 Testing viewing interest...")
    try:
        response = requests.post(
            f"{base_url}/chat",
            json={
                "message": "Yes, I would like to schedule a viewing. I'm available next week",
                "session_id": session_id
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response: {data['response'][:150]}...")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 10: Check final conversation state
    print("\n10. 📋 Final conversation state...")
    try:
        response = requests.get(f"{base_url}/conversation/{session_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Final Profile Complete: {data['profile_complete']}")
            print(f"✅ Final Missing Info: {data['missing_info']}")
            print(f"✅ Total Conversation Turns: {data['conversation_turns']}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_multiple_sessions():
    """Test multiple concurrent sessions"""
    base_url = "http://localhost:8000"
    
    print("\n🧪 Testing Multiple Sessions")
    print("=" * 40)
    
    session1 = f"multi_session_1_{int(time.time())}"
    session2 = f"multi_session_2_{int(time.time())}"
    
    # Session 1: Provide age
    print("\n📝 Session 1 - Providing age...")
    try:
        response = requests.post(
            f"{base_url}/chat",
            json={
                "message": "I am 30 years old",
                "session_id": session1
            },
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            print("✅ Session 1: Age provided")
    except Exception as e:
        print(f"❌ Session 1 Error: {e}")
    
    # Session 2: Provide different age
    print("\n📝 Session 2 - Providing different age...")
    try:
        response = requests.post(
            f"{base_url}/chat",
            json={
                "message": "I am 25 years old",
                "session_id": session2
            },
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            print("✅ Session 2: Age provided")
    except Exception as e:
        print(f"❌ Session 2 Error: {e}")
    
    # Check both sessions
    print("\n📊 Checking both sessions...")
    for session_id in [session1, session2]:
        try:
            response = requests.get(f"{base_url}/conversation/{session_id}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {session_id}: Turns={data['conversation_turns']}, Complete={data['profile_complete']}")
        except Exception as e:
            print(f"❌ Error checking {session_id}: {e}")

def test_conversation_cleanup():
    """Test conversation cleanup"""
    base_url = "http://localhost:8000"
    
    print("\n🧪 Testing Conversation Cleanup")
    print("=" * 40)
    
    session_id = f"cleanup_test_{int(time.time())}"
    
    # Create a conversation
    try:
        response = requests.post(
            f"{base_url}/chat",
            json={
                "message": "Hi, I'm testing cleanup",
                "session_id": session_id
            },
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            print("✅ Conversation created")
    except Exception as e:
        print(f"❌ Error creating conversation: {e}")
        return
    
    # Check it exists
    try:
        response = requests.get(f"{base_url}/conversation/{session_id}")
        if response.status_code == 200:
            print("✅ Conversation exists")
    except Exception as e:
        print(f"❌ Error checking conversation: {e}")
        return
    
    # Clear it
    try:
        response = requests.delete(f"{base_url}/conversation/{session_id}")
        if response.status_code == 200:
            print("✅ Conversation cleared")
    except Exception as e:
        print(f"❌ Error clearing conversation: {e}")
        return
    
    # Check it's gone
    try:
        response = requests.get(f"{base_url}/conversation/{session_id}")
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "not_found":
                print("✅ Conversation successfully removed")
            else:
                print("⚠️  Conversation still exists")
        else:
            print("✅ Conversation not found (as expected)")
    except Exception as e:
        print(f"❌ Error checking cleared conversation: {e}")

def test_comprehensive_first_message():
    """Test conversation with a comprehensive first message"""
    base_url = "http://localhost:8000"
    
    print("\n🧪 Testing Comprehensive First Message")
    print("=" * 50)
    
    session_id = f"comprehensive_{int(time.time())}"
    
    # Send a comprehensive first message with all information
    comprehensive_message = """Hi, I'm a 28-year-old female software engineer looking to rent a property. 
    I want to move in on March 15th and can stay for 12 months. 
    I have a guarantor (my father who is an accountant). 
    I'm available for viewings on weekends."""
    
    print(f"📝 Sending comprehensive first message...")
    print(f"Message: {comprehensive_message}")
    
    try:
        response = requests.post(
            f"{base_url}/chat",
            json={
                "message": comprehensive_message,
                "session_id": session_id
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response: {data['response'][:150]}...")
            print(f"✅ Profile Complete: {data['profile_complete']}")
        else:
            print(f"❌ Error: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Check conversation memory immediately
    print(f"\n📊 Checking conversation memory after first message...")
    try:
        response = requests.get(f"{base_url}/conversation/{session_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Session ID: {data['session_id']}")
            print(f"✅ Profile Complete: {data['profile_complete']}")
            print(f"✅ Missing Info: {data['missing_info']}")
            print(f"✅ Conversation Turns: {data['conversation_turns']}")
            
            if data['profile_complete']:
                print("🎉 Profile completed in just one message!")
            else:
                print(f"⚠️  Still missing: {data['missing_info']}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test follow-up question to see if agent remembers
    print(f"\n🧠 Testing agent memory with follow-up question...")
    try:
        response = requests.post(
            f"{base_url}/chat",
            json={
                "message": "What information do you have about me so far?",
                "session_id": session_id
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response: {data['response'][:200]}...")
            
            # Check if response mentions the extracted information
            response_lower = data['response'].lower()
            checks = [
                ("28", "age"),
                ("female", "sex"),
                ("software engineer", "occupation"),
                ("march 15th", "move-in date"),
                ("12 months", "duration"),
                ("guarantor", "guarantor status")
            ]
            
            for text, field in checks:
                if text in response_lower:
                    print(f"✅ Agent remembered: {field}")
                else:
                    print(f"⚠️  Agent may not have mentioned: {field}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_conversation_memory()
    test_multiple_sessions()
    test_conversation_cleanup()
    test_comprehensive_first_message()
