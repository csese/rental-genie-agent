#!/usr/bin/env python3
"""
Simple test for LLM-based extraction without full app dependencies
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_simple_extraction():
    """Test the LLM extraction logic directly"""
    
    # Check if OpenAI API key is available
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key to test the LLM extraction")
        return
    
    try:
        # Import required libraries
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_openai import ChatOpenAI
        from langchain_core.output_parsers import PydanticOutputParser
        from pydantic import BaseModel, Field
        from typing import Optional, Dict, List
        
        # Define Pydantic models
        class ExtractedField(BaseModel):
            value: Optional[str] = Field(None, description="The extracted value")
            confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence score")
        
        class TenantInfo(BaseModel):
            fields: Dict[str, ExtractedField] = Field(default_factory=dict, description="Extracted fields")
            language_preference: Optional[str] = Field(None, description="Language preference")
            overall_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall confidence")
            updated_fields: List[str] = Field(default_factory=list, description="Updated fields")
        
        # Create LLM
        llm = ChatOpenAI(model="gpt-4o", temperature=0.0)
        
        # Create extraction prompt
        extraction_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert information extraction system for rental property inquiries.

FIELD DEFINITIONS:
- move_in_date: When the tenant wants to move in (e.g., "January 2024", "next month", "asap")
- rental_duration: How long they want to rent (e.g., "12 months", "6 months", "long term")
- age: Tenant's age as an integer
- sex: "male" or "female"
- occupation: Their job or profession
- guarantor_status: "yes", "no", "visale", or "unknown"
- language_preference: "French", "English", or "Other"

CONSTRAINTS:
1. Extract ONLY from the current message - no inferences
2. Provide confidence scores (0.0-1.0) for each field
3. Only return fields with confidence >= 0.7

Extract information from this message: {user_input}

FEW-SHOT EXAMPLES:
1. "I'm 25 years old" → age=25, language="English"
2. "Je suis étudiant, 22 ans" → age=22, occupation="étudiant", language="French"
3. "Bonjour, je suis une femme de 28 ans" → sex="female", age=28, language="French"
4. "Je travaille comme ingénieur" → occupation="ingénieur", language="French"

IMPORTANT: You must return a valid JSON object with exactly this structure:
{{
  "fields": {{
    "age": {{"value": "25", "confidence": 0.9}},
    "occupation": {{"value": "software engineer", "confidence": 0.8}}
  }},
  "language_preference": "English",
  "overall_confidence": 0.85,
  "updated_fields": ["age", "occupation"]
}}

Do not include any text before or after the JSON object."""),
            ("human", "{user_input}")
        ])
        
        # Create output parser
        parser = PydanticOutputParser(pydantic_object=TenantInfo)
        
        # Create extraction chain
        extraction_chain = extraction_prompt | llm | parser
        
        # Test cases
        test_cases = [
            "Hello, I'm interested in renting an apartment. I'm 25 years old and work as a software engineer.",
            "Je suis étudiant, 22 ans, pour 9 mois à partir d'octobre.",
            "I need a guarantor and can move in next month for 12 months.",
            "I'm 25 now.",
            "No, I meant female.",
            # Additional French test cases
            "Bonjour, je suis une femme de 28 ans, médecin, et je cherche un appartement pour 6 mois à partir de janvier.",
            "Salut ! J'ai 19 ans, je suis étudiant en informatique. J'ai besoin d'un garant et je peux emménager en février pour 8 mois.",
            "Je suis un homme de 35 ans, architecte. Je veux louer pour 24 mois à partir de mars prochain.",
            "J'ai 24 ans maintenant.",
            "Non, je voulais dire homme.",
            "Je travaille comme ingénieur et j'ai 31 ans. Je peux emménager dès que possible pour 12 mois.",
            "Je suis une étudiante de 20 ans. J'ai un garant (mon père) et je veux louer pour 9 mois à partir de septembre.",
            "Bonjour, je suis un homme de 42 ans, professeur. Je cherche un logement pour 18 mois à partir d'avril.",
            "J'ai besoin d'un appartement pour 3 mois seulement, à partir de juin. Je suis une femme de 26 ans, avocate.",
            "Je suis étudiant en médecine, 23 ans, homme. Je peux emménager en juillet pour 10 mois. J'ai un garant.",
            "Salut ! Je suis une femme de 29 ans, designer. Je veux louer pour 15 mois à partir d'août. Pas de garant.",
            "Je suis un homme de 38 ans, consultant. J'ai besoin d'un logement pour 6 mois à partir de mai. J'ai un garant visale.",
            "Bonjour, je suis une femme de 25 ans, infirmière. Je peux emménager en décembre pour 12 mois. J'ai un garant."
        ]
        
        print("=== Simple LLM Extraction Test ===")
        print(f"OpenAI API Key: {'✅ Available' if os.getenv('OPENAI_API_KEY') else '❌ Missing'}")
        print()
        
        for i, message in enumerate(test_cases, 1):
            print(f"Test {i}: '{message}'")
            
            try:
                # Run extraction
                result = extraction_chain.invoke({"user_input": message})
                
                print(f"Result: {result}")
                print(f"Extracted fields: {list(result.fields.keys())}")
                print(f"Language: {result.language_preference}")
                print(f"Overall confidence: {result.overall_confidence}")
                print("-" * 50)
                
            except Exception as e:
                print(f"❌ Error: {e}")
                print("-" * 50)
        
        print("=== Test Complete ===")
        
    except ImportError as e:
        print(f"❌ Missing required library: {e}")
        print("Please install required packages: pip install langchain-openai langchain-core pydantic python-dotenv")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_simple_extraction()
