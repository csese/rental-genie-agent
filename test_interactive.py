#!/usr/bin/env python3
"""
Interactive test script for Rental Genie Agent
Supports session-based conversations with memory
"""

import requests
import json
import time
import uuid

def interactive_chat():
    """Interactive chat with the agent"""
    base_url = "http://localhost:8000"
    
    print("🏠 Rental Genie Agent - Interactive Chat")
    print("=" * 50)
    print("Type 'quit' to exit, 'help' for commands, 'memory' to see conversation state")
    print()
    
    # Generate a unique session ID
    session_id = f"interactive_{uuid.uuid4().hex[:8]}"
    print(f"Session ID: {session_id}")
    print()
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if user_input.lower() == 'quit':
                print("Goodbye! 👋")
                break
            elif user_input.lower() == 'help':
                print("\nAvailable commands:")
                print("- quit: Exit the chat")
                print("- help: Show this help")
                print("- memory: Show conversation memory")
                print("- clear: Clear conversation memory")
                print("- sessions: Show all active sessions")
                print("- switch v1: Switch to v1 prompt")
                print("- switch v2: Switch to v2 prompt")
                print()
                continue
            elif user_input.lower() == 'memory':
                show_conversation_memory(base_url, session_id)
                continue
            elif user_input.lower() == 'clear':
                clear_conversation_memory(base_url, session_id)
                continue
            elif user_input.lower() == 'sessions':
                show_all_sessions(base_url)
                continue
            elif user_input.startswith('switch '):
                version = user_input.split(' ')[1]
                switch_prompt_version(base_url, version)
                continue
            elif not user_input:
                continue
            
            # Send message to agent
            response = requests.post(
                f"{base_url}/chat",
                json={
                    "message": user_input,
                    "session_id": session_id,
                    "user_id": "interactive_user"
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n🤖 Agent: {data['response']}")
                
                # Show profile completion status
                if data.get('profile_complete') is not None:
                    status = "✅ Complete" if data['profile_complete'] else "⏳ Incomplete"
                    print(f"📊 Profile Status: {status}")
                
                print()
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                print()
                
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print()

def show_conversation_memory(base_url: str, session_id: str):
    """Show conversation memory for the current session"""
    try:
        response = requests.get(f"{base_url}/conversation/{session_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"\n📊 Conversation Memory for {session_id}")
            print("-" * 40)
            print(f"Profile Complete: {data.get('profile_complete', 'Unknown')}")
            print(f"Conversation Turns: {data.get('conversation_turns', 0)}")
            print(f"Last Updated: {data.get('last_updated', 'Unknown')}")
            
            missing_info = data.get('missing_info', [])
            if missing_info:
                print(f"Missing Information: {', '.join(missing_info)}")
            else:
                print("Missing Information: None (profile complete)")
            print()
        else:
            print(f"❌ Error getting conversation memory: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def clear_conversation_memory(base_url: str, session_id: str):
    """Clear conversation memory for the current session"""
    try:
        response = requests.delete(f"{base_url}/conversation/{session_id}")
        if response.status_code == 200:
            print(f"✅ Conversation memory cleared for session: {session_id}")
        else:
            print(f"❌ Error clearing conversation memory: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def show_all_sessions(base_url: str):
    """Show all active sessions"""
    try:
        response = requests.get(f"{base_url}/conversation")
        if response.status_code == 200:
            data = response.json()
            print(f"\n📋 All Active Sessions")
            print("-" * 30)
            print(f"Total Sessions: {data.get('active_sessions', 0)}")
            
            session_ids = data.get('session_ids', [])
            if session_ids:
                for session_id in session_ids:
                    print(f"- {session_id}")
            else:
                print("No active sessions")
            print()
        else:
            print(f"❌ Error getting sessions: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def switch_prompt_version(base_url: str, version: str):
    """Switch prompt version"""
    try:
        response = requests.post(
            f"{base_url}/prompts/switch",
            json={"version": version},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data.get('message', 'Prompt version switched')}")
        else:
            print(f"❌ Error switching prompt version: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_multi_turn_conversation():
    """Test a predefined multi-turn conversation"""
    base_url = "http://localhost:8000"
    session_id = f"test_multi_{int(time.time())}"
    
    print("🧪 Testing Multi-Turn Conversation")
    print("=" * 40)
    
    # Predefined conversation flow
    conversation = [
        "Hi, I'm interested in renting a property",
        "I am 28 years old and work as a data scientist",
        "I want to move in on April 15th",
        "I can stay for 18 months",
        "I am female",
        "I have a guarantor, my mother who is a teacher",
        "Yes, I would like to schedule a viewing. I'm available on weekends"
    ]
    
    for i, message in enumerate(conversation, 1):
        print(f"\n{i}. Sending: {message}")
        
        try:
            response = requests.post(
                f"{base_url}/chat",
                json={
                    "message": message,
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
    
    # Show final state
    print(f"\n📊 Final Conversation State")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/conversation/{session_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"Profile Complete: {data.get('profile_complete', False)}")
            print(f"Conversation Turns: {data.get('conversation_turns', 0)}")
            print(f"Missing Info: {data.get('missing_info', [])}")
    except Exception as e:
        print(f"❌ Error getting final state: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_multi_turn_conversation()
    else:
        interactive_chat()
