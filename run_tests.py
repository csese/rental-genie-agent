#!/usr/bin/env python3
"""
Simple test runner for Rental Genie Agent
Runs all tests from the root directory
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Run all tests using the integration test runner"""
    print("🧪 Running Rental Genie Test Suite")
    print("=" * 50)
    
    # Run the comprehensive test suite
    test_runner = Path("integration_tests/run_all_tests.py")
    
    if not test_runner.exists():
        print("❌ Test runner not found!")
        print("💡 Make sure you're in the project root directory")
        return False
    
    try:
        result = subprocess.run([sys.executable, str(test_runner)], 
                              capture_output=False, 
                              text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
