#!/usr/bin/env python3
"""
Test script for enhanced information extraction
Demonstrates how the system can extract multiple pieces of information from comprehensive first messages
"""

from app.conversation_memory import extract_tenant_info

def test_comprehensive_messages():
    """Test extraction from comprehensive first messages"""
    
    print("🧪 Testing Enhanced Information Extraction")
    print("=" * 60)
    
    # Test cases with comprehensive first messages
    test_messages = [
        {
            "message": "Hi, I'm a 28-year-old female software engineer looking to rent a property. I want to move in on March 15th and can stay for 12 months. I have a guarantor (my father who is an accountant). I'm available for viewings on weekends.",
            "description": "Complete profile in one message"
        },
        {
            "message": "Bonjour, je suis un homme de 32 ans, je travaille comme architecte. Je veux déménager le 1er avril et rester 18 mois. J'ai un garant (ma mère qui est enseignante). Je suis disponible en semaine pour les visites.",
            "description": "Complete French profile in one message"
        },
        {
            "message": "Hello! I'm 25, male, work as a data scientist. Looking to move in April 1st for 6 months minimum. No guarantor but I can provide Garantie Visale. Available evenings and weekends.",
            "description": "Profile with Visale guarantee"
        },
        {
            "message": "Hi there! I'm a 30-year-old female marketing manager. I need to move in ASAP, preferably by next week. I can commit to 24 months. I have a guarantor (my employer). I'm very interested in scheduling a viewing - I'm free most afternoons.",
            "description": "Urgent move-in with employer guarantor"
        },
        {
            "message": "Salut! Je suis étudiante de 22 ans, je cherche un logement pour septembre. Je peux rester 12 mois. J'ai besoin d'un garant car je n'ai pas de revenus stables. Je préfère les visites en fin d'après-midi.",
            "description": "Student with guarantor need"
        },
        {
            "message": "Hello, I'm a 35-year-old male consultant. I want to move in on May 1st and stay for 36 months. I have a guarantor (my friend who is a lawyer). I'm available for viewings on weekdays after 6 PM.",
            "description": "Long-term rental with friend guarantor"
        }
    ]
    
    for i, test_case in enumerate(test_messages, 1):
        print(f"\n{i}. 📝 {test_case['description']}")
        print("-" * 50)
        print(f"Message: {test_case['message']}")
        
        # Extract information
        extracted = extract_tenant_info(test_case['message'])
        
        print(f"\n✅ Extracted Information:")
        for key, value in extracted.items():
            print(f"  {key}: {value}")
        
        # Calculate completeness
        required_fields = ['age', 'sex', 'occupation', 'move_in_date', 'rental_duration', 'guarantor_status']
        extracted_fields = [field for field in required_fields if field in extracted]
        completeness = len(extracted_fields) / len(required_fields) * 100
        
        print(f"\n📊 Completeness: {completeness:.1f}% ({len(extracted_fields)}/{len(required_fields)} fields)")
        
        if completeness >= 80:
            print("🎉 Excellent extraction!")
        elif completeness >= 60:
            print("👍 Good extraction")
        elif completeness >= 40:
            print("⚠️  Partial extraction")
        else:
            print("❌ Poor extraction")

def test_edge_cases():
    """Test edge cases and variations"""
    
    print("\n\n🧪 Testing Edge Cases")
    print("=" * 40)
    
    edge_cases = [
        {
            "message": "I'm 25",
            "description": "Minimal age only"
        },
        {
            "message": "Age: 30, Male, Software Engineer",
            "description": "Formal format"
        },
        {
            "message": "Je suis une femme de 28 ans, architecte",
            "description": "French minimal"
        },
        {
            "message": "Hi! I work as a teacher and I'm 35 years old. I want to move in on January 15th, 2024 and stay for 12 months. I'm female and I have a guarantor (my sister). I'm available on weekends for viewings.",
            "description": "Mixed format with specific date"
        },
        {
            "message": "Hello, I'm a 27-year-old male. I work as a graphic designer. I want to move in ASAP and can stay for 6-12 months. I don't have a guarantor but I can provide Garantie Visale. I'm available evenings and weekends for viewings.",
            "description": "ASAP move-in with Visale"
        }
    ]
    
    for i, test_case in enumerate(edge_cases, 1):
        print(f"\n{i}. 🔍 {test_case['description']}")
        print(f"Message: {test_case['message']}")
        
        extracted = extract_tenant_info(test_case['message'])
        
        print(f"Extracted: {extracted}")
        
        # Check for specific patterns
        if 'age' in extracted:
            print(f"✅ Age detected: {extracted['age']}")
        if 'sex' in extracted:
            print(f"✅ Sex detected: {extracted['sex']}")
        if 'occupation' in extracted:
            print(f"✅ Occupation detected: {extracted['occupation']}")
        if 'move_in_date' in extracted:
            print(f"✅ Move-in date detected: {extracted['move_in_date']}")
        if 'rental_duration' in extracted:
            print(f"✅ Duration detected: {extracted['rental_duration']}")
        if 'guarantor_status' in extracted:
            print(f"✅ Guarantor status detected: {extracted['guarantor_status']}")

def test_language_detection():
    """Test language preference detection"""
    
    print("\n\n🧪 Testing Language Detection")
    print("=" * 40)
    
    language_tests = [
        {
            "message": "Bonjour! Je suis intéressé par votre propriété. Je suis un homme de 30 ans.",
            "expected": "french"
        },
        {
            "message": "Hello! I'm interested in your property. I'm a 30-year-old man.",
            "expected": "english"
        },
        {
            "message": "Hi there, je veux louer un appartement. I'm 25 years old.",
            "expected": "english"  # More English words
        },
        {
            "message": "Salut, I want to rent an apartment. Je suis 25 ans.",
            "expected": "french"  # More French words
        }
    ]
    
    for i, test_case in enumerate(language_tests, 1):
        print(f"\n{i}. 🌍 Language Test")
        print(f"Message: {test_case['message']}")
        
        extracted = extract_tenant_info(test_case['message'])
        detected_language = extracted.get('language_preference', 'unknown')
        
        print(f"Expected: {test_case['expected']}")
        print(f"Detected: {detected_language}")
        
        if detected_language == test_case['expected']:
            print("✅ Correct language detection!")
        else:
            print("❌ Incorrect language detection")

if __name__ == "__main__":
    test_comprehensive_messages()
    test_edge_cases()
    test_language_detection()



