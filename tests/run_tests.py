#!/usr/bin/env python3
"""
Test runner for Rental Genie tests
"""

import sys
import os
import unittest
import argparse
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../app'))


def run_unit_tests():
    """Run all unit tests"""
    print("🧪 Running Unit Tests...")
    
    # Change to the project root directory
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(__file__))
    os.chdir(project_root)
    
    try:
        # Discover and run unit tests
        loader = unittest.TestLoader()
        start_dir = os.path.join('tests', 'unit')
        suite = loader.discover(start_dir, pattern='test_*.py')
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result.wasSuccessful()
    finally:
        # Restore original directory
        os.chdir(original_dir)


def run_integration_tests():
    """Run all integration tests"""
    print("🔗 Running Integration Tests...")
    
    # Change to the project root directory
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(__file__))
    os.chdir(project_root)
    
    try:
        # Discover and run integration tests
        loader = unittest.TestLoader()
        start_dir = os.path.join('tests', 'integration')
        suite = loader.discover(start_dir, pattern='test_*.py')
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result.wasSuccessful()
    finally:
        # Restore original directory
        os.chdir(original_dir)


def run_specific_test(test_path):
    """Run a specific test file"""
    print(f"🎯 Running Specific Test: {test_path}")
    
    # Run the specific test file
    loader = unittest.TestLoader()
    suite = loader.discover(os.path.dirname(test_path), pattern=os.path.basename(test_path))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_all_tests():
    """Run all tests (unit + integration)"""
    print("🚀 Running All Tests...")
    
    # Run unit tests first
    unit_success = run_unit_tests()
    print("\n" + "="*50 + "\n")
    
    # Run integration tests
    integration_success = run_integration_tests()
    
    return unit_success and integration_success


def list_tests():
    """List all available tests"""
    print("📋 Available Tests:\n")
    
    # List unit tests
    print("Unit Tests:")
    unit_dir = Path(__file__).parent / 'unit'
    if unit_dir.exists():
        for test_file in unit_dir.glob('test_*.py'):
            print(f"  - {test_file.name}")
    else:
        print("  No unit tests found")
    
    print("\nIntegration Tests:")
    integration_dir = Path(__file__).parent / 'integration'
    if integration_dir.exists():
        for test_file in integration_dir.glob('test_*.py'):
            print(f"  - {test_file.name}")
    else:
        print("  No integration tests found")


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description='Rental Genie Test Runner')
    parser.add_argument('--type', choices=['unit', 'integration', 'all'], 
                       default='all', help='Type of tests to run')
    parser.add_argument('--test', help='Specific test file to run')
    parser.add_argument('--list', action='store_true', help='List all available tests')
    
    args = parser.parse_args()
    
    if args.list:
        list_tests()
        return
    
    if args.test:
        success = run_specific_test(args.test)
    elif args.type == 'unit':
        success = run_unit_tests()
    elif args.type == 'integration':
        success = run_integration_tests()
    else:  # all
        success = run_all_tests()
    
    print("\n" + "="*50)
    if success:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()
