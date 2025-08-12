#!/usr/bin/env python3
"""
Quick test script for Slack notifications
Simple and fast way to test if Slack integration is working
"""

import os
import sys
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from notifications import test_slack_integration, send_handoff_notification, send_session_notification

def quick_test():
    """Run a quick test of Slack notifications"""
    print("🧪 Quick Slack Notification Test")
    print("=" * 40)
    
    # Check configuration
    webhook_url = os.environ.get("SLACK_WEBHOOK_RENTAL_GENIE_URL")
    if not webhook_url:
        print("❌ SLACK_WEBHOOK_RENTAL_GENIE_URL not found!")
        print("💡 Set the environment variable to enable Slack notifications")
        return False
    
    print(f"✅ Webhook URL found: {webhook_url[:30]}...")
    
    # Test 1: Basic integration test
    print("\n1️⃣ Testing basic integration...")
    success1 = test_slack_integration()
    print(f"   {'✅ Passed' if success1 else '❌ Failed'}")
    
    # Test 2: Handoff notification
    print("\n2️⃣ Testing handoff notification...")
    success2 = send_handoff_notification(
        session_id="quick_test_001",
        handoff_reason="Quick test - tenant needs assistance",
        confidence_level="medium",
        escalation_priority="low",
        conversation_summary="This is a quick test of the handoff notification system.",
        tenant_name="Test User",
        tenant_age=30
    )
    print(f"   {'✅ Passed' if success2 else '❌ Failed'}")
    
    # Test 3: Session notification
    print("\n3️⃣ Testing session notification...")
    success3 = send_session_notification(
        session_id="quick_test_002",
        tenant_message="Hi, I'm looking for an apartment. This is a test message.",
        tenant_age=25,
        extracted_info={"budget": "$2000", "location": "downtown"}
    )
    print(f"   {'✅ Passed' if success3 else '❌ Failed'}")
    
    # Summary
    print("\n" + "=" * 40)
    passed = sum([success1, success2, success3])
    print(f"📊 Results: {passed}/3 tests passed")
    
    if passed == 3:
        print("🎉 All tests passed! Slack integration is working correctly.")
    else:
        print("⚠️ Some tests failed. Check your webhook URL and network connection.")
    
    return passed == 3

if __name__ == "__main__":
    success = quick_test()
    sys.exit(0 if success else 1)
