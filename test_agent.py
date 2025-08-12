#!/usr/bin/env python3
"""
Test suite for Rental Genie Agent
Includes unit tests, integration tests, and manual testing utilities
"""

import unittest
import json
import requests
import os
from unittest.mock import Mock, patch, MagicMock
import sys
import time

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from agent import handle_message, get_system_prompt
from utils import get_all_property_info

class TestRentalAgent(unittest.TestCase):
    """Unit tests for the rental agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_property_data = """
        Property: 123 Main St, 2BR/1BA, $1500/month
        Available: January 2024
        Requirements: Credit check, income 3x rent, security deposit
        """
        
        self.test_messages = [
            "Hi, I'm interested in renting a property",
            "What's the move-in date?",
            "I'm 25 years old and work as a software engineer",
            "Do you need a guarantor?",
            "How long is the lease term?"
        ]
    
    def test_system_prompt_generation(self):
        """Test that system prompt is generated correctly"""
        prompt = get_system_prompt(self.sample_property_data)
        self.assertIn("rental genie", prompt.lower())
        self.assertIn("property data", prompt.lower())
        self.assertIn("move-in date", prompt.lower())
        self.assertIn("duration", prompt.lower())
        self.assertIn("age", prompt.lower())
        self.assertIn("sex", prompt.lower())
        self.assertIn("occupation", prompt.lower())
        self.assertIn("guarantor", prompt.lower())
    
    @patch('agent.chain.predict')
    def test_handle_message_basic(self, mock_predict):
        """Test basic message handling"""
        mock_predict.return_value = "Thank you for your interest! I'll need some information from you."
        
        response = handle_message("Hello", self.sample_property_data)
        
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
        mock_predict.assert_called_once()
    
    @patch('agent.chain.predict')
    def test_handle_message_with_tenant_info(self, mock_predict):
        """Test message handling with tenant information"""
        mock_predict.return_value = "Great! I have your information: Age 25, Software Engineer. What's your move-in date?"
        
        response = handle_message("I'm 25 and work as a software engineer", self.sample_property_data)
        
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
        mock_predict.assert_called_once()

class TestAPIIntegration(unittest.TestCase):
    """Integration tests for the API endpoints"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.base_url = "http://localhost:8000"
        self.test_message = {
            "message": "Hi, I'm interested in renting a property",
            "user_id": "test_user_123",
            "session_id": "test_session_456"
        }
    
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("status", data)
            self.assertIn("message", data)
        except requests.exceptions.ConnectionError:
            self.skipTest("Server not running")
    
    def test_chat_endpoint(self):
        """Test the main chat endpoint"""
        try:
            response = requests.post(
                f"{self.base_url}/chat",
                json=self.test_message,
                headers={"Content-Type": "application/json"}
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("response", data)
            self.assertIn("status", data)
            self.assertEqual(data["status"], "success")
        except requests.exceptions.ConnectionError:
            self.skipTest("Server not running")
    
    def test_properties_endpoint(self):
        """Test the properties endpoint"""
        try:
            response = requests.get(f"{self.base_url}/properties")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("properties", data)
            self.assertIn("count", data)
        except requests.exceptions.ConnectionError:
            self.skipTest("Server not running")

class ManualTestSuite:
    """Manual testing utilities for interactive testing"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session_id = f"manual_test_{int(time.time())}"
    
    def test_conversation_flow(self):
        """Test a complete conversation flow"""
        print("=== Manual Conversation Flow Test ===")
        
        conversation = [
            "Hi, I'm looking for a rental property",
            "I'm 28 years old",
            "I work as a data analyst",
            "I want to move in on March 1st",
            "I can stay for 12 months",
            "I have a guarantor",
            "My guarantor is my father who works as an accountant"
        ]
        
        for i, message in enumerate(conversation, 1):
            print(f"\n--- Message {i}: {message} ---")
            
            try:
                response = requests.post(
                    f"{self.base_url}/chat",
                    json={
                        "message": message,
                        "user_id": "manual_test_user",
                        "session_id": self.session_id
                    },
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"Agent Response: {data['response']}")
                else:
                    print(f"Error: {response.status_code} - {response.text}")
                    
            except requests.exceptions.ConnectionError:
                print("Error: Cannot connect to server. Make sure it's running on localhost:8000")
                return
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("\n=== Edge Cases Test ===")
        
        edge_cases = [
            "",  # Empty message
            "   ",  # Whitespace only
            "A" * 1000,  # Very long message
            "Hello! 😊",  # Message with emoji
            "I'm interested in the property at 123 Main St",  # Specific property reference
        ]
        
        for i, message in enumerate(edge_cases, 1):
            print(f"\n--- Edge Case {i}: {repr(message)} ---")
            
            try:
                response = requests.post(
                    f"{self.base_url}/chat",
                    json={
                        "message": message,
                        "user_id": "edge_test_user",
                        "session_id": self.session_id
                    },
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"Response: {data['response'][:100]}...")
                else:
                    print(f"Error: {response.status_code} - {response.text}")
                    
            except requests.exceptions.ConnectionError:
                print("Error: Cannot connect to server")
                return

def run_unit_tests():
    """Run all unit tests"""
    print("Running unit tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)

def run_integration_tests():
    """Run integration tests"""
    print("Running integration tests...")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAPIIntegration)
    unittest.TextTestRunner(verbosity=2).run(suite)

def run_manual_tests():
    """Run manual tests"""
    print("Starting manual tests...")
    tester = ManualTestSuite()
    tester.test_conversation_flow()
    tester.test_edge_cases()

def check_server_status():
    """Check if the server is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and healthy")
            return True
        else:
            print(f"⚠️  Server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Start it with: python -m app.main")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

if __name__ == "__main__":
    print("=== Rental Genie Agent Test Suite ===\n")
    
    # Check server status first
    server_running = check_server_status()
    
    # Run unit tests (don't require server)
    print("\n" + "="*50)
    run_unit_tests()
    
    # Run integration tests (require server)
    if server_running:
        print("\n" + "="*50)
        run_integration_tests()
        
        # Run manual tests
        print("\n" + "="*50)
        run_manual_tests()
    else:
        print("\n" + "="*50)
        print("Skipping integration and manual tests - server not running")
        print("To start the server, run: python -m app.main")
