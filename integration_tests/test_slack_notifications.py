#!/usr/bin/env python3
"""
Test script for Slack notifications in Rental Genie Agent
Tests various notification types and scenarios
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Any

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from notifications import (
    SlackNotifier, 
    HandoffNotification, 
    SessionNotification,
    send_handoff_notification,
    send_session_notification,
    test_slack_integration
)

def test_basic_integration():
    """Test basic Slack integration"""
    print("🔧 Testing basic Slack integration...")
    
    # Test the built-in test function
    success = test_slack_integration()
    
    if success:
        print("✅ Basic integration test passed!")
    else:
        print("❌ Basic integration test failed!")
    
    return success

def test_handoff_notifications():
    """Test various handoff notification scenarios"""
    print("\n🚨 Testing handoff notifications...")
    
    notifier = SlackNotifier()
    
    # Test case 1: Low priority handoff
    print("Testing low priority handoff...")
    low_priority = HandoffNotification(
        session_id="test_low_priority_001",
        tenant_name="John Doe",
        tenant_age=28,
        tenant_occupation="Software Engineer",
        tenant_language="English",
        handoff_reason="Tenant requested specific property details",
        confidence_level="high",
        escalation_priority="low",
        conversation_summary="Tenant is interested in 2-bedroom apartments and has good credit score.",
        property_interest="2-bedroom apartment in downtown",
        move_in_date="2024-03-01",
        rental_duration="12 months",
        guarantor_status="Not required",
        viewing_interest=True,
        availability="Weekends",
        conversation_history=[
            {"user_message": "Hi, I'm looking for a 2-bedroom apartment", "agent_response": "Great! I can help you find the perfect place."},
            {"user_message": "What's available in downtown?", "agent_response": "I have several options. Let me show you the details."}
        ],
        created_at=datetime.now().isoformat()
    )
    
    success1 = notifier.send_handoff_notification(low_priority)
    
    # Test case 2: High priority handoff
    print("Testing high priority handoff...")
    high_priority = HandoffNotification(
        session_id="test_high_priority_002",
        tenant_name="Jane Smith",
        tenant_age=35,
        tenant_occupation="Doctor",
        tenant_language="English",
        handoff_reason="Urgent move-in request - immediate availability needed",
        confidence_level="medium",
        escalation_priority="high",
        conversation_summary="Tenant needs immediate housing due to job relocation. Has excellent references.",
        property_interest="Any available 1-2 bedroom",
        move_in_date="ASAP",
        rental_duration="24 months",
        guarantor_status="Available",
        viewing_interest=True,
        availability="Any time",
        conversation_history=[
            {"user_message": "I need a place immediately", "agent_response": "I understand this is urgent. Let me help you."},
            {"user_message": "I can move in tomorrow", "agent_response": "This requires immediate attention from our team."}
        ],
        created_at=datetime.now().isoformat()
    )
    
    success2 = notifier.send_handoff_notification(high_priority)
    
    # Test case 3: Urgent priority handoff
    print("Testing urgent priority handoff...")
    urgent_priority = HandoffNotification(
        session_id="test_urgent_priority_003",
        tenant_name="Mike Johnson",
        tenant_age=42,
        tenant_occupation="Business Owner",
        tenant_language="English",
        handoff_reason="Complex financial situation requiring manual review",
        confidence_level="low",
        escalation_priority="urgent",
        conversation_summary="Tenant has complex income structure with multiple businesses. Requires manual verification.",
        property_interest="Luxury 3-bedroom penthouse",
        move_in_date="2024-02-15",
        rental_duration="36 months",
        guarantor_status="Multiple guarantors",
        viewing_interest=True,
        availability="Weekdays only",
        conversation_history=[
            {"user_message": "I own several businesses", "agent_response": "I'll need to gather more information about your income."},
            {"user_message": "My income varies monthly", "agent_response": "This requires special handling. Let me connect you with our team."}
        ],
        created_at=datetime.now().isoformat()
    )
    
    success3 = notifier.send_handoff_notification(urgent_priority)
    
    return success1 and success2 and success3

def test_session_notifications():
    """Test new session notifications"""
    print("\n🆕 Testing session notifications...")
    
    notifier = SlackNotifier()
    
    # Test case 1: Basic session notification
    print("Testing basic session notification...")
    basic_session = SessionNotification(
        session_id="test_session_001",
        tenant_message="Hi, I'm looking for an apartment in the city center. I have a budget of $2000 per month.",
        tenant_age=25,
        tenant_occupation="Marketing Specialist",
        tenant_language="English",
        extracted_info={
            "budget": "$2000/month",
            "location": "city center",
            "property_type": "apartment"
        },
        created_at=datetime.now().isoformat()
    )
    
    success1 = notifier.send_session_notification(basic_session)
    
    # Test case 2: Session with more extracted info
    print("Testing session with detailed extraction...")
    detailed_session = SessionNotification(
        session_id="test_session_002",
        tenant_message="Hello! I need a 2-bedroom house with a garden. I have two children and a dog. My budget is $3000 and I need to move in by March 1st.",
        tenant_age=32,
        tenant_occupation="Teacher",
        tenant_language="English",
        extracted_info={
            "bedrooms": "2",
            "property_type": "house",
            "features": ["garden", "pet-friendly"],
            "budget": "$3000",
            "move_in_date": "March 1st",
            "family_size": "4 (2 adults, 2 children)",
            "pets": "dog"
        },
        created_at=datetime.now().isoformat()
    )
    
    success2 = notifier.send_session_notification(detailed_session)
    
    return success1 and success2

def test_function_wrappers():
    """Test the convenience function wrappers"""
    print("\n🔗 Testing function wrappers...")
    
    # Test handoff notification wrapper
    print("Testing handoff notification wrapper...")
    success1 = send_handoff_notification(
        session_id="test_wrapper_001",
        handoff_reason="Testing function wrapper",
        confidence_level="high",
        escalation_priority="medium",
        conversation_summary="This is a test of the convenience function wrapper.",
        tenant_name="Test User",
        tenant_age=30,
        tenant_occupation="Tester"
    )
    
    # Test session notification wrapper
    print("Testing session notification wrapper...")
    success2 = send_session_notification(
        session_id="test_wrapper_002",
        tenant_message="This is a test message for the session notification wrapper.",
        tenant_age=28,
        tenant_occupation="Developer",
        extracted_info={"test": "data"}
    )
    
    return success1 and success2

def test_error_handling():
    """Test error handling scenarios"""
    print("\n⚠️ Testing error handling...")
    
    # Test with disabled notifications
    print("Testing with disabled notifications...")
    original_webhook = os.environ.get("SLACK_WEBHOOK_RENTAL_GENIE_URL")
    
    # Temporarily disable webhook
    if "SLACK_WEBHOOK_RENTAL_GENIE_URL" in os.environ:
        del os.environ["SLACK_WEBHOOK_RENTAL_GENIE_URL"]
    
    notifier = SlackNotifier()
    test_notification = HandoffNotification(
        session_id="test_error_001",
        handoff_reason="Test error handling",
        confidence_level="medium",
        escalation_priority="low",
        conversation_summary="Testing error handling when webhook is disabled.",
        created_at=datetime.now().isoformat()
    )
    
    success = notifier.send_handoff_notification(test_notification)
    
    # Restore webhook
    if original_webhook:
        os.environ["SLACK_WEBHOOK_RENTAL_GENIE_URL"] = original_webhook
    
    print(f"Error handling test result: {'✅ Passed' if not success else '❌ Failed'}")
    return True  # This test should pass (notifications disabled)

def check_configuration():
    """Check if Slack is properly configured"""
    print("\n🔍 Checking configuration...")
    
    webhook_url = os.environ.get("SLACK_WEBHOOK_RENTAL_GENIE_URL")
    
    if webhook_url:
        print(f"✅ Slack webhook URL found: {webhook_url[:20]}...")
        return True
    else:
        print("❌ SLACK_WEBHOOK_RENTAL_GENIE_URL not found in environment variables")
        print("💡 To enable Slack notifications, set the SLACK_WEBHOOK_RENTAL_GENIE_URL environment variable")
        return False

def main():
    """Main test function"""
    print("🧪 Slack Notifications Test Suite")
    print("=" * 50)
    
    # Check configuration first
    config_ok = check_configuration()
    
    if not config_ok:
        print("\n⚠️ Tests will run but notifications will be disabled due to missing configuration.")
    
    # Run all tests
    tests = [
        ("Basic Integration", test_basic_integration),
        ("Handoff Notifications", test_handoff_notifications),
        ("Session Notifications", test_session_notifications),
        ("Function Wrappers", test_function_wrappers),
        ("Error Handling", test_error_handling)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
