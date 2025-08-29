#!/usr/bin/env python3
"""
Test fixtures and sample data for Rental Genie tests
"""

# Sample property data for testing
SAMPLE_PROPERTY_DATA = [
    {
        "fields": {
            "Name": "Sample Property",
            "Address": "123 Main St",
            "Rent": "$1500/month",
            "Available": "January 2024"
        }
    },
    {
        "fields": {
            "Name": "Test Apartment",
            "Address": "456 Oak Ave",
            "Rent": "$2000/month",
            "Available": "February 2024"
        }
    }
]

# Sample user messages for testing
SAMPLE_USER_MESSAGES = {
    "basic_info": "Hello, I'm interested in renting an apartment. I'm 25 years old and work as a software engineer.",
    "french_complete": "Bonjour, je suis une femme de 28 ans, médecin, et je cherche un appartement pour 6 mois à partir de janvier.",
    "age_correction": "I'm 25 now.",
    "sex_correction": "No, I meant female.",
    "french_age_correction": "J'ai 24 ans maintenant.",
    "french_sex_correction": "Non, je voulais dire homme.",
    "multiple_fields": "I need a guarantor and can move in next month for 12 months.",
    "simple_greeting": "Hello.",
    "french_student": "Salut ! J'ai 19 ans, je suis étudiant en informatique. J'ai besoin d'un garant et je peux emménager en février pour 8 mois.",
    "french_architect": "Je suis un homme de 35 ans, architecte. Je veux louer pour 24 mois à partir de mars prochain."
}

# Expected extraction results for testing
EXPECTED_EXTRACTIONS = {
    "basic_info": {
        "expected_fields": ["age", "occupation"],
        "expected_values": {"age": 25, "occupation": "software engineer"},
        "expected_language": "English"
    },
    "french_complete": {
        "expected_fields": ["age", "sex", "occupation", "rental_duration", "move_in_date"],
        "expected_values": {"age": 28, "sex": "female", "occupation": "médecin", "rental_duration": "6 mois", "move_in_date": "janvier"},
        "expected_language": "French"
    },
    "age_correction": {
        "expected_fields": ["age"],
        "expected_values": {"age": 25},
        "expected_language": "English"
    },
    "sex_correction": {
        "expected_fields": ["sex"],
        "expected_values": {"sex": "female"},
        "expected_language": "English"
    },
    "french_age_correction": {
        "expected_fields": ["age"],
        "expected_values": {"age": 24},
        "expected_language": "French"
    },
    "french_sex_correction": {
        "expected_fields": ["sex"],
        "expected_values": {"sex": "male"},
        "expected_language": "French"
    },
    "multiple_fields": {
        "expected_fields": ["guarantor_status", "move_in_date", "rental_duration"],
        "expected_values": {"guarantor_status": "yes", "move_in_date": "next month", "rental_duration": "12 months"},
        "expected_language": "English"
    },
    "simple_greeting": {
        "expected_fields": ["language_preference"],
        "expected_values": {},
        "expected_language": "English"
    },
    "french_student": {
        "expected_fields": ["age", "occupation", "guarantor_status", "move_in_date", "rental_duration"],
        "expected_values": {"age": 19, "occupation": "étudiant en informatique", "guarantor_status": "yes", "move_in_date": "février", "rental_duration": "8 mois"},
        "expected_language": "French"
    },
    "french_architect": {
        "expected_fields": ["age", "sex", "occupation", "rental_duration", "move_in_date"],
        "expected_values": {"age": 35, "sex": "male", "occupation": "architecte", "rental_duration": "24 mois", "move_in_date": "mars prochain"},
        "expected_language": "French"
    }
}

# Sample tenant profiles for testing
SAMPLE_TENANT_PROFILES = {
    "empty_profile": {
        "age": None,
        "sex": None,
        "occupation": None,
        "move_in_date": None,
        "rental_duration": None,
        "guarantor_status": None,
        "language_preference": None
    },
    "partial_profile": {
        "age": 24,
        "sex": "male",
        "occupation": "developer",
        "move_in_date": "January 2024",
        "rental_duration": "12 months",
        "guarantor_status": "yes",
        "language_preference": "English"
    },
    "complete_profile": {
        "age": 28,
        "sex": "female",
        "occupation": "engineer",
        "move_in_date": "March 2024",
        "rental_duration": "18 months",
        "guarantor_status": "no",
        "language_preference": "English"
    },
    "french_profile": {
        "age": 25,
        "sex": "male",
        "occupation": "étudiant",
        "move_in_date": "septembre",
        "rental_duration": "9 mois",
        "guarantor_status": "yes",
        "language_preference": "French"
    }
}

# Sample conversation history for testing
SAMPLE_CONVERSATION_HISTORY = [
    {
        "timestamp": "2024-01-15T10:00:00",
        "user_message": "Hello, I'm interested in renting an apartment.",
        "agent_response": "Great! I'd be happy to help you find a rental. Can you tell me your age and occupation?",
        "extracted_info": {}
    },
    {
        "timestamp": "2024-01-15T10:01:00",
        "user_message": "I'm 25 years old and work as a software engineer.",
        "agent_response": "Thank you! What's your preferred move-in date and how long do you plan to rent?",
        "extracted_info": {"age": 25, "occupation": "software engineer"}
    },
    {
        "timestamp": "2024-01-15T10:02:00",
        "user_message": "I can move in next month for 12 months.",
        "agent_response": "Perfect! Do you have a guarantor?",
        "extracted_info": {"move_in_date": "next month", "rental_duration": "12 months"}
    }
]

# Sample session data for testing
SAMPLE_SESSIONS = {
    "new_session": {
        "session_id": "test_session_new",
        "tenant_profile": SAMPLE_TENANT_PROFILES["empty_profile"],
        "conversation_history": [],
        "session_created": "2024-01-15T10:00:00"
    },
    "active_session": {
        "session_id": "test_session_active",
        "tenant_profile": SAMPLE_TENANT_PROFILES["partial_profile"],
        "conversation_history": SAMPLE_CONVERSATION_HISTORY,
        "session_created": "2024-01-15T09:00:00"
    },
    "complete_session": {
        "session_id": "test_session_complete",
        "tenant_profile": SAMPLE_TENANT_PROFILES["complete_profile"],
        "conversation_history": SAMPLE_CONVERSATION_HISTORY,
        "session_created": "2024-01-15T08:00:00"
    }
}

# Test configuration
TEST_CONFIG = {
    "min_confidence_threshold": 0.7,
    "max_confidence_threshold": 1.0,
    "test_session_prefix": "test_session_",
    "mock_api_key": "test_openai_api_key_12345",
    "timeout_seconds": 30
}
