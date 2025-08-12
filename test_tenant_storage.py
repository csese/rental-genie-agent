#!/usr/bin/env python3
"""
Test script for tenant storage functionality
Tests both in-memory and persistent storage capabilities with status management
"""

import sys
import os
import time
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from conversation_memory import ConversationMemory, TenantProfile, extract_tenant_info, TenantStatus
from utils import store_tenant_profile, get_tenant_profile, get_all_tenant_profiles, delete_tenant_profile, update_tenant_status, get_tenants_by_status, get_tenant_status_info

def test_tenant_status_enum():
    """Test the TenantStatus enum functionality"""
    print("=== Testing TenantStatus Enum ===")
    
    # Test enum values
    print(f"All status values: {TenantStatus.get_all_values()}")
    print(f"Total statuses: {len(TenantStatus)}")
    
    # Test validation
    print(f"Is 'prospect' valid? {TenantStatus.is_valid('prospect')}")
    print(f"Is 'invalid_status' valid? {TenantStatus.is_valid('invalid_status')}")
    
    # Test display names
    for status in TenantStatus:
        display_name = TenantStatus.get_display_name(status.value)
        description = TenantStatus.get_description(status.value)
        print(f"{status.value} -> {display_name}: {description}")
    
    # Test enum access
    print(f"PROSPECT enum: {TenantStatus.PROSPECT}")
    print(f"PROSPECT value: {TenantStatus.PROSPECT.value}")
    print(f"QUALIFIED enum: {TenantStatus.QUALIFIED}")
    print(f"ACTIVE_TENANT enum: {TenantStatus.ACTIVE_TENANT}")

def test_tenant_extraction():
    """Test tenant information extraction from messages"""
    print("\n=== Testing Tenant Information Extraction ===")
    
    test_messages = [
        "Hi, I'm a 25-year-old software engineer looking for a 2-bedroom apartment. I want to move in on January 15th for 12 months. I have a guarantor.",
        "Bonjour, je suis une femme de 30 ans, comptable. Je veux déménager le 1er mars pour 6 mois. J'ai besoin d'un garant.",
        "I'm interested in viewing the property. I'm available on weekends. I'm 28 years old and work as a teacher.",
        "J'ai 35 ans, je suis médecin. Je peux commencer le bail en février pour 24 mois. J'ai un garant (mon père)."
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\nTest {i}: {message[:50]}...")
        extracted = extract_tenant_info(message)
        print(f"Extracted: {extracted}")

def test_in_memory_storage():
    """Test in-memory tenant storage"""
    print("\n=== Testing In-Memory Storage ===")
    
    # Create memory instance without persistent storage
    memory = ConversationMemory(use_persistent_storage=False)
    
    # Test session creation
    session_id = f"test_session_{int(time.time())}"
    session = memory.get_or_create_session(session_id)
    print(f"Created session: {session_id}")
    
    # Test profile update
    updates = {
        "age": 25,
        "sex": "male",
        "occupation": "software engineer",
        "move_in_date": "January 15th",
        "rental_duration": "12 months",
        "guarantor_status": "yes"
    }
    
    memory.update_tenant_profile(session_id, updates)
    print(f"Updated profile with: {updates}")
    
    # Test profile retrieval
    profile = memory.get_tenant_profile(session_id)
    print(f"Retrieved profile: Age={profile.age}, Occupation={profile.occupation}, Status={profile.status}")
    
    # Test conversation turn
    memory.add_conversation_turn(
        session_id, 
        "I need a 2-bedroom apartment", 
        "I have several 2-bedroom options available.", 
        {"property_type": "2-bedroom"}
    )
    print("Added conversation turn")
    
    # Test missing information
    missing = memory.get_missing_information(session_id)
    print(f"Missing information: {missing}")
    
    # Test profile completion
    is_complete = memory.is_profile_complete(session_id)
    print(f"Profile complete: {is_complete}")
    
    return session_id

def test_status_management():
    """Test tenant status management"""
    print("\n=== Testing Status Management ===")
    
    # Create memory instance
    memory = ConversationMemory(use_persistent_storage=False)
    
    session_id = f"status_test_{int(time.time())}"
    
    # Create initial profile
    updates = {
        "age": 30,
        "sex": "female",
        "occupation": "accountant",
        "move_in_date": "March 1st",
        "rental_duration": "6 months",
        "guarantor_status": "need"
    }
    
    memory.update_tenant_profile(session_id, updates)
    print(f"Created profile with status: {memory.get_tenant_profile(session_id).status}")
    
    # Test status updates using enum values
    status_transitions = [
        (TenantStatus.QUALIFIED.value, {"property_interest": "2-bedroom apartment"}),
        (TenantStatus.VIEWING_SCHEDULED.value, {"availability": "weekends"}),
        (TenantStatus.APPLICATION_SUBMITTED.value, {"application_date": datetime.now().isoformat()}),
        (TenantStatus.APPROVED.value, {"notes": "Application approved by owner"}),
        (TenantStatus.ACTIVE_TENANT.value, {"lease_start_date": "2024-03-01", "lease_end_date": "2024-09-01"})
    ]
    
    for new_status, additional_data in status_transitions:
        memory.update_tenant_status(session_id, new_status, additional_data)
        profile = memory.get_tenant_profile(session_id)
        display_name = TenantStatus.get_display_name(profile.status)
        print(f"Status updated to: {profile.status} ({display_name})")
        if additional_data:
            print(f"Additional data: {additional_data}")
    
    return session_id

def test_persistent_storage():
    """Test persistent storage functionality"""
    print("\n=== Testing Persistent Storage ===")
    
    session_id = f"persistent_test_{int(time.time())}"
    
    # Test storing tenant profile
    tenant_data = {
        "status": TenantStatus.PROSPECT.value,  # Use enum value
        "age": 30,
        "sex": "female",
        "occupation": "accountant",
        "move_in_date": "March 1st",
        "rental_duration": "6 months",
        "guarantor_status": "need",
        "viewing_interest": True,
        "availability": "weekends",
        "language_preference": "french",
        "created_at": datetime.now().isoformat(),
        "conversation_turns": 3
    }
    
    success = store_tenant_profile(session_id, tenant_data)
    print(f"Stored tenant profile: {success}")
    
    # Test retrieving tenant profile
    retrieved_data = get_tenant_profile(session_id)
    if retrieved_data:
        print(f"Retrieved profile: Age={retrieved_data.get('age')}, Status={retrieved_data.get('status')}")
    else:
        print("Failed to retrieve profile")
    
    # Test status update using enum
    update_success = update_tenant_status(session_id, TenantStatus.QUALIFIED.value, {"property_interest": "Studio apartment"})
    print(f"Updated status to qualified: {update_success}")
    
    # Test getting all profiles
    all_profiles = get_all_tenant_profiles()
    print(f"Total profiles in storage: {len(all_profiles)}")
    
    # Test filtering by status using enum values
    prospects = get_tenants_by_status(TenantStatus.PROSPECT.value)
    qualified = get_tenants_by_status(TenantStatus.QUALIFIED.value)
    print(f"Prospects: {len(prospects)}, Qualified: {len(qualified)}")
    
    # Test status info
    status_info = get_tenant_status_info()
    print(f"Status info: {len(status_info['statuses'])} statuses available")
    
    # Test deleting profile
    delete_success = delete_tenant_profile(session_id)
    print(f"Deleted profile: {delete_success}")
    
    return session_id

def test_integrated_storage():
    """Test integrated storage with both memory and persistence"""
    print("\n=== Testing Integrated Storage ===")
    
    # Create memory instance with persistent storage
    memory = ConversationMemory(use_persistent_storage=True)
    
    session_id = f"integrated_test_{int(time.time())}"
    
    # Create session and update profile
    session = memory.get_or_create_session(session_id)
    updates = {
        "age": 28,
        "sex": "male",
        "occupation": "teacher",
        "move_in_date": "February 1st",
        "rental_duration": "18 months",
        "guarantor_status": "yes",
        "guarantor_details": "father"
    }
    
    memory.update_tenant_profile(session_id, updates)
    print(f"Updated profile in integrated storage")
    
    # Test conversation turn
    memory.add_conversation_turn(
        session_id,
        "I'm interested in viewing the property",
        "I can schedule a viewing for you.",
        {"viewing_interest": True}
    )
    print("Added conversation turn to integrated storage")
    
    # Test status management using enum
    memory.update_tenant_status(session_id, TenantStatus.QUALIFIED.value, {"property_interest": "3-bedroom house"})
    print("Updated status to qualified")
    
    # Test loading from persistent storage
    print("Testing load from persistent storage...")
    memory2 = ConversationMemory(use_persistent_storage=True)
    profile = memory2.get_tenant_profile(session_id)
    
    if profile:
        display_name = TenantStatus.get_display_name(profile.status)
        print(f"Successfully loaded profile: Age={profile.age}, Status={profile.status} ({display_name})")
        print(f"Property interest: {profile.property_interest}")
        print(f"Conversation turns: {profile.conversation_turns}")
    else:
        print("Failed to load profile from persistent storage")
    
    return session_id

def test_status_filtering():
    """Test filtering tenants by status"""
    print("\n=== Testing Status Filtering ===")
    
    memory = ConversationMemory(use_persistent_storage=True)
    
    # Create multiple test profiles with different statuses using enum values
    test_profiles = [
        ("prospect_1", TenantStatus.PROSPECT.value, {"age": 25, "sex": "male", "occupation": "student"}),
        ("prospect_2", TenantStatus.PROSPECT.value, {"age": 30, "sex": "female", "occupation": "engineer"}),
        ("qualified_1", TenantStatus.QUALIFIED.value, {"age": 28, "sex": "male", "occupation": "teacher"}),
        ("active_1", TenantStatus.ACTIVE_TENANT.value, {"age": 35, "sex": "female", "occupation": "doctor"})
    ]
    
    for session_id, status, data in test_profiles:
        memory.update_tenant_status(session_id, status, data)
        display_name = TenantStatus.get_display_name(status)
        print(f"Created {display_name} profile: {session_id}")
    
    # Test filtering
    prospects = memory.get_prospects()
    qualified = memory.get_qualified_prospects()
    active = memory.get_active_tenants()
    
    print(f"Prospects: {len(prospects)}")
    print(f"Qualified: {len(qualified)}")
    print(f"Active tenants: {len(active)}")
    
    # Clean up test data
    for session_id, _, _ in test_profiles:
        memory.clear_session(session_id)
    
    return [session_id for session_id, _, _ in test_profiles]

def main():
    """Run all tests"""
    print("Starting Tenant Storage Tests")
    print("=" * 50)
    
    try:
        # Test enum functionality
        test_tenant_status_enum()
        
        # Test extraction
        test_tenant_extraction()
        
        # Test in-memory storage
        in_memory_session = test_in_memory_storage()
        
        # Test status management
        status_session = test_status_management()
        
        # Test persistent storage
        persistent_session = test_persistent_storage()
        
        # Test integrated storage
        integrated_session = test_integrated_storage()
        
        # Test status filtering
        filtered_sessions = test_status_filtering()
        
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        print(f"Test sessions created: {in_memory_session}, {status_session}, {persistent_session}, {integrated_session}")
        print(f"Filtered sessions: {filtered_sessions}")
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
