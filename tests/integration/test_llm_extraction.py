#!/usr/bin/env python3
"""
Test script for LLM-based tenant information extraction
"""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Load environment variables
load_dotenv()

def test_llm_extraction():
    """Test the LLM-based extraction system"""
    
    # Import the extraction function
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))
    
    # Mock the conversation_memory module for testing
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
    
    extract_tenant_info_llm = agent.extract_tenant_info_llm
    
    # Test cases
    test_cases = [
        {
            "message": "Hello, I'm interested in renting an apartment. I'm 25 years old and work as a software engineer.",
            "expected_fields": ["age", "occupation"],
            "description": "Basic information extraction"
        },
        {
            "message": "Je suis étudiant, 22 ans, pour 9 mois à partir d'octobre.",
            "expected_fields": ["age", "occupation", "rental_duration", "move_in_date", "language_preference"],
            "description": "French message with multiple fields"
        },
        {
            "message": "I'm 25 now.",
            "expected_fields": ["age"],
            "description": "Age correction"
        },
        {
            "message": "No, I meant female.",
            "expected_fields": ["sex"],
            "description": "Sex correction"
        },
        {
            "message": "Hello.",
            "expected_fields": ["language_preference"],
            "description": "Simple greeting with language detection"
        },
        {
            "message": "I need a guarantor and can move in next month for 12 months.",
            "expected_fields": ["guarantor_status", "move_in_date", "rental_duration"],
            "description": "Multiple fields in one message"
        },
        # Additional French test cases
        {
            "message": "Bonjour, je suis une femme de 28 ans, médecin, et je cherche un appartement pour 6 mois à partir de janvier.",
            "expected_fields": ["age", "sex", "occupation", "rental_duration", "move_in_date", "language_preference"],
            "description": "French professional woman with complete information"
        },
        {
            "message": "Salut ! J'ai 19 ans, je suis étudiant en informatique. J'ai besoin d'un garant et je peux emménager en février pour 8 mois.",
            "expected_fields": ["age", "occupation", "guarantor_status", "move_in_date", "rental_duration", "language_preference"],
            "description": "French student with guarantor need"
        },
        {
            "message": "Je suis un homme de 35 ans, architecte. Je veux louer pour 24 mois à partir de mars prochain.",
            "expected_fields": ["age", "sex", "occupation", "rental_duration", "move_in_date", "language_preference"],
            "description": "French architect with long-term rental"
        },
        {
            "message": "J'ai 24 ans maintenant.",
            "expected_fields": ["age", "language_preference"],
            "description": "French age correction"
        },
        {
            "message": "Non, je voulais dire homme.",
            "expected_fields": ["sex", "language_preference"],
            "description": "French sex correction"
        },
        {
            "message": "Je travaille comme ingénieur et j'ai 31 ans. Je peux emménager dès que possible pour 12 mois.",
            "expected_fields": ["occupation", "age", "move_in_date", "rental_duration", "language_preference"],
            "description": "French engineer with ASAP move-in"
        },
        {
            "message": "Je suis une étudiante de 20 ans. J'ai un garant (mon père) et je veux louer pour 9 mois à partir de septembre.",
            "expected_fields": ["age", "sex", "occupation", "guarantor_status", "guarantor_details", "rental_duration", "move_in_date", "language_preference"],
            "description": "French student with guarantor details"
        },
        {
            "message": "Bonjour, je suis un homme de 42 ans, professeur. Je cherche un logement pour 18 mois à partir d'avril.",
            "expected_fields": ["age", "sex", "occupation", "rental_duration", "move_in_date", "language_preference"],
            "description": "French teacher with medium-term rental"
        },
        {
            "message": "J'ai besoin d'un appartement pour 3 mois seulement, à partir de juin. Je suis une femme de 26 ans, avocate.",
            "expected_fields": ["rental_duration", "move_in_date", "sex", "age", "occupation", "language_preference"],
            "description": "French lawyer with short-term rental"
        },
        {
            "message": "Je suis étudiant en médecine, 23 ans, homme. Je peux emménager en juillet pour 10 mois. J'ai un garant.",
            "expected_fields": ["occupation", "age", "sex", "move_in_date", "rental_duration", "guarantor_status", "language_preference"],
            "description": "French medical student with guarantor"
        },
        {
            "message": "Salut ! Je suis une femme de 29 ans, designer. Je veux louer pour 15 mois à partir d'août. Pas de garant.",
            "expected_fields": ["sex", "age", "occupation", "rental_duration", "move_in_date", "guarantor_status", "language_preference"],
            "description": "French designer without guarantor"
        },
        {
            "message": "Je suis un homme de 38 ans, consultant. J'ai besoin d'un logement pour 6 mois à partir de mai. J'ai un garant visale.",
            "expected_fields": ["age", "sex", "occupation", "rental_duration", "move_in_date", "guarantor_status", "language_preference"],
            "description": "French consultant with visale guarantor"
        },
        {
            "message": "Bonjour, je suis une femme de 25 ans, infirmière. Je peux emménager en décembre pour 12 mois. J'ai un garant.",
            "expected_fields": ["sex", "age", "occupation", "move_in_date", "rental_duration", "guarantor_status", "language_preference"],
            "description": "French nurse with standard rental period"
        }
    ]
    
    print("=== LLM Extraction Test Suite ===")
    print(f"OpenAI API Key available: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")
    print()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['description']}")
        print(f"Message: '{test_case['message']}'")
        print(f"Expected fields: {test_case['expected_fields']}")
        
        try:
            # Test extraction
            result = extract_tenant_info_llm(test_case['message'])
            
            print(f"Extracted fields: {list(result.keys())}")
            print(f"Extracted values: {result}")
            
            # Check if expected fields were extracted
            extracted_fields = list(result.keys())
            missing_fields = [field for field in test_case['expected_fields'] if field not in extracted_fields]
            
            if missing_fields:
                print(f"❌ Missing expected fields: {missing_fields}")
            else:
                print("✅ All expected fields extracted")
            
            print("-" * 50)
            
        except Exception as e:
            print(f"❌ Error in test {i}: {e}")
            print("-" * 50)
    
    print("=== Test Suite Complete ===")

if __name__ == "__main__":
    test_llm_extraction()
