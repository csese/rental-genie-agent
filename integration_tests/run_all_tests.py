#!/usr/bin/env python3
"""
Run all tests from the tests directory
Organizes and executes different types of tests
"""

import os
import sys
import subprocess
from pathlib import Path

def run_test(test_file, description):
    """Run a single test file and return the result"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"📁 {test_file}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=False, 
                              text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {test_file}: {e}")
        return False

def main():
    """Run all tests in organized categories"""
    print("🧪 Rental Genie Test Suite")
    print("=" * 60)
    
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    tests_dir = Path(__file__).parent
    
    # Change to project root for proper imports
    os.chdir(project_root)
    
    # Test categories
    slack_tests = [
        ("integration_tests/test_slack_quick.py", "Quick Slack Integration Test"),
        ("integration_tests/test_slack_notifications.py", "Comprehensive Slack Notifications Test")
    ]
    
    unit_tests = [
        ("unit_tests/test_agent.py", "Agent Functionality Test"),
        ("unit_tests/test_conversation_memory.py", "Conversation Memory Test"),
        ("unit_tests/test_extraction.py", "Information Extraction Test"),
        ("unit_tests/test_interactive.py", "Interactive Chat Test"),
        ("unit_tests/test_prompts.py", "Prompt Management Test"),
        ("unit_tests/test_tenant_storage.py", "Tenant Storage Test"),
        ("unit_tests/test_airtable.py", "Airtable Integration Test")
    ]
    
    # Results tracking
    results = {}
    
    # Run Slack tests first (integration tests)
    print("\n🔗 INTEGRATION TESTS")
    print("=" * 60)
    for test_file, description in slack_tests:
        if os.path.exists(test_file):
            results[description] = run_test(test_file, description)
        else:
            print(f"⚠️ Test file not found: {test_file}")
            results[description] = False
    
    # Run unit tests
    print("\n⚙️ UNIT TESTS")
    print("=" * 60)
    for test_file, description in unit_tests:
        if os.path.exists(test_file):
            results[description] = run_test(test_file, description)
        else:
            print(f"⚠️ Test file not found: {test_file}")
            results[description] = False
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
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
        return True
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
