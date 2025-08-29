#!/usr/bin/env python3
"""
Unit tests for LLM extraction logic functions
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../app'))

import unittest
from unittest.mock import Mock, patch, MagicMock

# Mock the conversation_memory module to avoid import issues
class MockConversationMemory:
    def get_tenant_profile(self, session_id):
        return None
    
    def get_missing_information(self, session_id):
        return []
    
    def get_or_create_session(self, session_id):
        return {"conversation_history": []}

# Mock the extract_tenant_info function
def mock_extract_tenant_info(message):
    return {}

# Import with mocked dependencies
import agent
agent.conversation_memory = MockConversationMemory()
agent.extract_tenant_info = mock_extract_tenant_info

from agent import extract_tenant_info_llm, get_extraction_chain


class TestExtractionLogic(unittest.TestCase):
    """Test the extraction logic functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_session_id = "test_session_123"
        self.sample_user_input = "I'm 25 years old and work as a software engineer"
    
    @patch('agent.get_extraction_chain')
    @patch('agent.conversation_memory')
    def test_extraction_chain_unavailable_fallback(self, mock_conversation_memory, mock_get_chain):
        """Test fallback to rule-based extraction when chain is unavailable"""
        # Mock chain as unavailable
        mock_get_chain.return_value = None
        
        # Mock rule-based extraction
        mock_conversation_memory.extract_tenant_info.return_value = {"age": 25, "occupation": "engineer"}
        
        # Test the function
        result = extract_tenant_info_llm(self.sample_user_input, self.mock_session_id)
        
        # Verify fallback was used
        mock_conversation_memory.extract_tenant_info.assert_called_once_with(self.sample_user_input)
        self.assertEqual(result, {"age": 25, "occupation": "engineer"})
    
    @patch('agent.get_extraction_chain')
    @patch('agent.conversation_memory')
    def test_extraction_with_no_session_id(self, mock_conversation_memory, mock_get_chain):
        """Test extraction when no session_id is provided"""
        # Mock chain as available
        mock_chain = Mock()
        mock_get_chain.return_value = mock_chain
        
        # Mock LLM response
        mock_result = Mock()
        mock_result.fields = {
            "age": Mock(value="25", confidence=0.9),
            "occupation": Mock(value="engineer", confidence=0.8)
        }
        mock_result.language_preference = "English"
        mock_result.overall_confidence = 0.85
        mock_result.updated_fields = ["age", "occupation"]
        
        mock_chain.invoke.return_value = mock_result
        
        # Test the function
        result = extract_tenant_info_llm(self.sample_user_input, None)
        
        # Verify chain was called with empty context
        mock_chain.invoke.assert_called_once()
        call_args = mock_chain.invoke.call_args[0][0]
        self.assertEqual(call_args["known_info"], "{}")
        self.assertEqual(call_args["missing_fields"], "[]")
        self.assertEqual(call_args["focus_fields"], "['age', 'sex', 'occupation', 'move_in_date', 'rental_duration', 'guarantor_status', 'language_preference']")
    
    @patch('agent.get_extraction_chain')
    @patch('agent.conversation_memory')
    def test_extraction_with_existing_profile(self, mock_conversation_memory, mock_get_chain):
        """Test extraction with existing tenant profile"""
        # Mock existing profile
        mock_profile = Mock()
        mock_profile.age = 24
        mock_profile.sex = "male"
        mock_profile.occupation = "developer"
        mock_profile.move_in_date = "January 2024"
        mock_profile.rental_duration = "12 months"
        mock_profile.guarantor_status = "yes"
        mock_profile.language_preference = "English"
        
        mock_conversation_memory.get_tenant_profile.return_value = mock_profile
        mock_conversation_memory.get_missing_information.return_value = ["age"]  # Only age is missing
        
        # Mock session
        mock_session = {"conversation_history": []}
        mock_conversation_memory.get_or_create_session.return_value = mock_session
        
        # Mock chain
        mock_chain = Mock()
        mock_get_chain.return_value = mock_chain
        
        # Mock LLM response
        mock_result = Mock()
        mock_result.fields = {
            "age": Mock(value="25", confidence=0.9)
        }
        mock_result.language_preference = "English"
        mock_result.overall_confidence = 0.9
        mock_result.updated_fields = ["age"]
        
        mock_chain.invoke.return_value = mock_result
        
        # Test the function
        result = extract_tenant_info_llm("I'm 25 now", self.mock_session_id)
        
        # Verify context was built correctly
        mock_chain.invoke.assert_called_once()
        call_args = mock_chain.invoke.call_args[0][0]
        self.assertIn("age=24", call_args["known_info"])
        self.assertIn("sex=male", call_args["known_info"])
        self.assertEqual(call_args["missing_fields"], "['age']")
        self.assertEqual(call_args["focus_fields"], "['age']")
        
        # Verify result
        self.assertEqual(result, {"age": 25})
    
    @patch('agent.get_extraction_chain')
    @patch('agent.conversation_memory')
    def test_extraction_confidence_filtering(self, mock_conversation_memory, mock_get_chain):
        """Test that low-confidence extractions are filtered out"""
        # Mock chain
        mock_chain = Mock()
        mock_get_chain.return_value = mock_chain
        
        # Mock LLM response with mixed confidence scores
        mock_result = Mock()
        mock_result.fields = {
            "age": Mock(value="25", confidence=0.9),  # High confidence
            "occupation": Mock(value="engineer", confidence=0.6),  # Low confidence
            "sex": Mock(value="male", confidence=0.8)  # Medium confidence
        }
        mock_result.language_preference = "English"
        mock_result.overall_confidence = 0.77
        mock_result.updated_fields = ["age", "occupation", "sex"]
        
        mock_chain.invoke.return_value = mock_result
        
        # Test the function
        result = extract_tenant_info_llm(self.sample_user_input, self.mock_session_id)
        
        # Verify only high-confidence fields were included
        self.assertIn("age", result)
        self.assertNotIn("occupation", result)  # Should be filtered out
        self.assertIn("sex", result)
        self.assertEqual(result["age"], 25)  # Should be converted to int
        self.assertEqual(result["sex"], "male")
    
    @patch('agent.get_extraction_chain')
    @patch('agent.conversation_memory')
    def test_extraction_error_handling(self, mock_conversation_memory, mock_get_chain):
        """Test error handling in extraction"""
        # Mock chain to raise an exception
        mock_chain = Mock()
        mock_chain.invoke.side_effect = Exception("LLM API error")
        mock_get_chain.return_value = mock_chain
        
        # Mock rule-based extraction as fallback
        mock_conversation_memory.extract_tenant_info.return_value = {"age": 25}
        
        # Test the function
        result = extract_tenant_info_llm(self.sample_user_input, self.mock_session_id)
        
        # Verify fallback was used
        mock_conversation_memory.extract_tenant_info.assert_called_once_with(self.sample_user_input)
        self.assertEqual(result, {"age": 25})
    
    @patch('agent.get_extraction_chain')
    @patch('agent.conversation_memory')
    def test_extraction_with_recent_context(self, mock_conversation_memory, mock_get_chain):
        """Test extraction with recent conversation context"""
        # Mock existing profile
        mock_profile = Mock()
        mock_profile.age = 24
        mock_profile.sex = None
        mock_profile.occupation = None
        mock_profile.move_in_date = None
        mock_profile.rental_duration = None
        mock_profile.guarantor_status = None
        mock_profile.language_preference = None
        
        mock_conversation_memory.get_tenant_profile.return_value = mock_profile
        mock_conversation_memory.get_missing_information.return_value = ["sex", "occupation", "move_in_date", "rental_duration", "guarantor_status"]
        
        # Mock session with conversation history
        mock_session = {
            "conversation_history": [
                {
                    "user_message": "Hello, I'm interested in renting",
                    "agent_response": "Great! Can you tell me your age and occupation?"
                },
                {
                    "user_message": "I'm 25 years old",
                    "agent_response": "Thank you. What's your occupation?"
                }
            ]
        }
        mock_conversation_memory.get_or_create_session.return_value = mock_session
        
        # Mock chain
        mock_chain = Mock()
        mock_get_chain.return_value = mock_chain
        
        # Mock LLM response
        mock_result = Mock()
        mock_result.fields = {
            "occupation": Mock(value="engineer", confidence=0.9)
        }
        mock_result.language_preference = "English"
        mock_result.overall_confidence = 0.9
        mock_result.updated_fields = ["occupation"]
        
        mock_chain.invoke.return_value = mock_result
        
        # Test the function
        result = extract_tenant_info_llm("I work as a software engineer", self.mock_session_id)
        
        # Verify context was included
        mock_chain.invoke.assert_called_once()
        call_args = mock_chain.invoke.call_args[0][0]
        self.assertIn("User: I'm 25 years old", call_args["recent_context"])
        self.assertIn("Agent: Thank you. What's your occupation?", call_args["recent_context"])
        
        # Verify result
        self.assertEqual(result, {"occupation": "engineer"})


class TestExtractionChain(unittest.TestCase):
    """Test the extraction chain creation"""
    
    @patch('agent.get_llm')
    @patch('agent.ChatPromptTemplate')
    @patch('agent.PydanticOutputParser')
    def test_get_extraction_chain_success(self, mock_parser, mock_prompt, mock_get_llm):
        """Test successful extraction chain creation"""
        # Mock LLM availability
        mock_get_llm.return_value = (True, Mock())
        
        # Mock prompt and parser
        mock_prompt.from_messages.return_value = Mock()
        mock_parser.return_value = Mock()
        
        # Test chain creation
        chain = get_extraction_chain()
        
        # Verify chain was created
        self.assertIsNotNone(chain)
        mock_prompt.from_messages.assert_called_once()
        mock_parser.assert_called_once()
    
    @patch('agent.get_llm')
    def test_get_extraction_chain_llm_unavailable(self, mock_get_llm):
        """Test extraction chain creation when LLM is unavailable"""
        # Mock LLM as unavailable
        mock_get_llm.return_value = (False, None)
        
        # Test chain creation
        chain = get_extraction_chain()
        
        # Verify no chain was created
        self.assertIsNone(chain)


if __name__ == '__main__':
    unittest.main()
