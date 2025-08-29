from langchain_core.prompts import ChatPromptTemplate
from langchain_core.memory import BaseMemory
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
import os
import json
import re
from dotenv import load_dotenv
from .prompts import get_system_prompt, prompt_manager
from .conversation_memory import conversation_memory, extract_tenant_info
from .notifications import send_handoff_notification, send_session_notification

# Load environment variables
load_dotenv()

# Global variables for caching
llm = None
chain = None
llm_available = None
extraction_chain = None

# Pydantic models for LLM extraction
class ExtractedField(BaseModel):
    """Individual extracted field with confidence score"""
    value: Optional[str] = Field(None, description="The extracted value")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")

class TenantInfo(BaseModel):
    """Complete tenant information extraction result"""
    fields: Dict[str, ExtractedField] = Field(default_factory=dict, description="Extracted fields with confidence scores")
    language_preference: Optional[str] = Field(None, description="Detected language preference: French, English, or Other")
    overall_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall confidence score")
    updated_fields: List[str] = Field(default_factory=list, description="List of field names that were updated")
    
    class Config:
        extra = "allow"  # Allow extra fields to prevent parsing errors

def get_llm():
    """Get or create the LLM instance"""
    global llm, chain, llm_available
    
    if llm_available is None:
        try:
            llm = ChatOpenAI(model="gpt-4o")
            prompt = ChatPromptTemplate.from_messages([("system", "{system}"), ("human", "{input}")])
            chain = LLMChain(llm=llm, prompt=prompt)
            llm_available = True
            print("OpenAI API configured successfully")
        except Exception as e:
            print(f"Warning: OpenAI API not configured: {e}")
            llm_available = False
            llm = None
            chain = None
    
    return llm_available, chain

def get_extraction_chain():
    """Get or create the extraction chain"""
    global extraction_chain, llm
    
    if extraction_chain is None:
        try:
            # Get LLM instance
            llm_available, _ = get_llm()
            if not llm_available:
                return None
            
            # Create extraction prompt
            extraction_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert information extraction system for rental property inquiries. Your task is to extract specific tenant information from user messages.

FIELD DEFINITIONS:
- move_in_date: When the tenant wants to move in (e.g., "January 2024", "next month", "asap")
- rental_duration: How long they want to rent (e.g., "12 months", "6 months", "long term")
- age: Tenant's age as an integer
- sex: "male" or "female"
- occupation: Their job or profession
- guarantor_status: "yes", "no", "visale", or "unknown"
- language_preference: "French", "English", or "Other"

CONSTRAINTS:
1. Extract ONLY from the current message - no inferences or external knowledge
2. Only extract fields that are explicitly mentioned or corrected
3. Do not override known information unless user provides new/conflicting info
4. Focus on missing fields and fields implied by recent context
5. Provide confidence scores (0.0-1.0) for each field
6. Only return fields with confidence >= 0.7
7. If no relevant information is found, return empty fields with low confidence

FEW-SHOT EXAMPLES:
1. Message: "I'm 25 now." | Known: age=24 | Missing: sex | Focus: age → Update age to 25
2. Message: "No, I meant female." | Known: sex=male | Missing: occupation | Focus: sex → Update sex to female  
3. Message: "Hello." | Known: all | Missing: none | Focus: none → Empty fields, detect language
4. Message: "Je suis étudiant, 22 ans, pour 9 mois à partir d'octobre." | Known: none | Missing: all | Focus: all → Extract age=22, occupation="étudiant", etc., language="French"
5. Message: "Bonjour, je suis une femme de 28 ans, médecin." | Known: none | Missing: all | Focus: all → Extract sex="female", age=28, occupation="médecin", language="French"
6. Message: "J'ai 24 ans maintenant." | Known: age=23 | Missing: occupation | Focus: age → Update age to 24, language="French"
7. Message: "Non, je voulais dire homme." | Known: sex=female | Missing: guarantor_status | Focus: sex → Update sex to "male", language="French"
8. Message: "Je travaille comme ingénieur et j'ai 31 ans." | Known: none | Missing: all | Focus: all → Extract occupation="ingénieur", age=31, language="French"

KNOWN INFORMATION: {known_info}
MISSING FIELDS: {missing_fields}
FOCUS FIELDS: {focus_fields}
RECENT CONTEXT: {recent_context}

Extract information from this message: {user_input}

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
            
            print("Extraction chain created successfully")
            
        except Exception as e:
            print(f"Warning: Extraction chain not configured: {e}")
            extraction_chain = None
    
    return extraction_chain

def extract_tenant_info_llm(user_input: str, session_id: str = None) -> Dict[str, Any]:
    """
    Extract tenant information using LLM-based extraction
    """
    try:
        print(f"=== LLM EXTRACTION START ===")
        print(f"User input: '{user_input}'")
        print(f"Session ID: {session_id}")
        
        # Get extraction chain
        chain = get_extraction_chain()
        if not chain:
            print("Extraction chain not available, falling back to rule-based extraction")
            return extract_tenant_info(user_input)
        
        # Get current tenant profile
        known_info = {}
        missing_fields = []
        focus_fields = []
        recent_context = ""
        
        if session_id:
            profile = conversation_memory.get_tenant_profile(session_id)
            if profile:
                # Build known info summary
                known_info = {
                    "age": profile.age,
                    "sex": profile.sex,
                    "occupation": profile.occupation,
                    "move_in_date": profile.move_in_date,
                    "rental_duration": profile.rental_duration,
                    "guarantor_status": profile.guarantor_status,
                    "language_preference": profile.language_preference
                }
                
                # Get missing fields
                missing_fields = conversation_memory.get_missing_information(session_id)
                
                # Focus fields = missing fields + fields implied by recent context
                focus_fields = missing_fields.copy()
                
                # Get recent conversation context (last 2 turns)
                session = conversation_memory.get_or_create_session(session_id)
                history = session.get("conversation_history", [])
                if history:
                    recent_turns = history[-2:]  # Last 2 turns
                    recent_context = "\n".join([
                        f"User: {turn['user_message']}\nAgent: {turn['agent_response']}"
                        for turn in recent_turns
                    ])
        
        # If no session or new session, focus on all fields
        if not session_id or not known_info:
            focus_fields = ["age", "sex", "occupation", "move_in_date", "rental_duration", "guarantor_status", "language_preference"]
        
        print(f"Known info: {known_info}")
        print(f"Missing fields: {missing_fields}")
        print(f"Focus fields: {focus_fields}")
        print(f"Recent context: {recent_context[:100]}...")
        
        # Run extraction
        result = chain.invoke({
            "known_info": str(known_info),
            "missing_fields": str(missing_fields),
            "focus_fields": str(focus_fields),
            "recent_context": recent_context,
            "user_input": user_input
        })
        
        print(f"Raw LLM result: {result}")
        
        # Process results
        extracted = {}
        updated_fields = []
        
        for field_name, field_data in result.fields.items():
            if field_data.confidence >= 0.7:  # Only use high-confidence extractions
                value = field_data.value
                if value and value.strip():
                    # Type conversion for specific fields
                    if field_name == "age" and value.isdigit():
                        extracted[field_name] = int(value)
                    else:
                        extracted[field_name] = value
                    updated_fields.append(field_name)
                    print(f"Extracted {field_name}: {value} (confidence: {field_data.confidence})")
                else:
                    print(f"Skipped {field_name}: empty value")
            else:
                print(f"Skipped {field_name}: low confidence ({field_data.confidence})")
        
        # Add language preference if detected
        if result.language_preference:
            extracted["language_preference"] = result.language_preference
            print(f"Detected language: {result.language_preference}")
        
        print(f"Final extracted info: {extracted}")
        print(f"Updated fields: {updated_fields}")
        print(f"Overall confidence: {result.overall_confidence}")
        print(f"=== LLM EXTRACTION END ===")
        
        return extracted
        
    except Exception as e:
        print(f"Error in LLM extraction: {e}")
        import traceback
        traceback.print_exc()
        print("Falling back to rule-based extraction")
        return extract_tenant_info(user_input)

def extract_json_from_response(response: str) -> dict:
    """Extract JSON data from the agent response"""
    try:
        # Look for JSON in the response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            return json.loads(json_str)
        return {}
    except Exception as e:
        print(f"Error extracting JSON from response: {e}")
        return {}

def detect_handoff_triggers(user_input: str, session_id: str = None) -> dict:
    """Detect handoff triggers in user input"""
    triggers = {
        "handoff_triggered": False,
        "handoff_reason": "",
        "confidence_level": "high",
        "escalation_priority": "low"
    }
    
    user_input_lower = user_input.lower()
    
    # Manual triggers - explicit requests for human
    manual_trigger_keywords = [
        "speak to someone", "human agent", "real person", "talk to owner", 
        "speak to landlord", "talk to human", "speak to manager", "contact owner",
        "speak to property owner", "talk to someone real", "human help",
        "speak with owner", "contact landlord", "speak to manager"
    ]
    
    for keyword in manual_trigger_keywords:
        if keyword in user_input_lower:
            triggers["handoff_triggered"] = True
            triggers["handoff_reason"] = f"Explicit request for human: '{keyword}'"
            triggers["escalation_priority"] = "medium"
            break
    
    # Emotional triggers
    emotional_keywords = [
        "frustrated", "angry", "upset", "disappointed", "not happy", "unhappy",
        "urgent", "emergency", "asap", "immediately", "right now", "today",
        "complicated", "complex", "difficult", "problem", "issue", "trouble"
    ]
    
    emotional_count = sum(1 for keyword in emotional_keywords if keyword in user_input_lower)
    if emotional_count >= 2:
        triggers["handoff_triggered"] = True
        triggers["handoff_reason"] = "Emotional situation detected"
        triggers["escalation_priority"] = "high"
    
    # Language barrier detection - only trigger for actual communication difficulties
    if session_id:
        profile = conversation_memory.get_tenant_profile(session_id)
        if profile and profile.language_preference:
            # Only trigger for actual communication difficulties, not simple greetings
            communication_difficulty_keywords = ["sorry", "not understand", "confused", "help", "don't understand", "can't understand"]
            if any(word in user_input_lower for word in communication_difficulty_keywords):
                triggers["handoff_triggered"] = True
                triggers["handoff_reason"] = "Potential language barrier"
                triggers["escalation_priority"] = "medium"
    
    return triggers

def handle_handoff_notification(session_id: str, handoff_data: dict, conversation_summary: str):
    """Handle handoff notification to Slack"""
    try:
        # Get tenant profile and conversation history
        tenant_profile = None
        conversation_history = None
        
        if session_id:
            profile = conversation_memory.get_tenant_profile(session_id)
            if profile:
                tenant_profile = {
                    "age": profile.age,
                    "sex": profile.sex,
                    "occupation": profile.occupation,
                    "language_preference": profile.language_preference,
                    "move_in_date": profile.move_in_date,
                    "rental_duration": profile.rental_duration,
                    "guarantor_status": profile.guarantor_status,
                    "viewing_interest": profile.viewing_interest,
                    "availability": profile.availability,
                    "property_interest": profile.property_interest
                }
            
            # Get conversation history
            session = conversation_memory.get_or_create_session(session_id)
            conversation_history = session.get("conversation_history", [])
        
        # Send notification
        success = send_handoff_notification(
            session_id=session_id,
            handoff_reason=handoff_data.get("handoff_reason", "Unknown reason"),
            confidence_level=handoff_data.get("confidence_level", "medium"),
            escalation_priority=handoff_data.get("escalation_priority", "medium"),
            conversation_summary=conversation_summary,
            tenant_profile=tenant_profile,
            conversation_history=conversation_history,
            tenant_age=tenant_profile.get("age") if tenant_profile else None,
            tenant_occupation=tenant_profile.get("occupation") if tenant_profile else None,
            tenant_language=tenant_profile.get("language_preference") if tenant_profile else None,
            property_interest=tenant_profile.get("property_interest") if tenant_profile else None,
            move_in_date=tenant_profile.get("move_in_date") if tenant_profile else None,
            rental_duration=tenant_profile.get("rental_duration") if tenant_profile else None,
            guarantor_status=tenant_profile.get("guarantor_status") if tenant_profile else None,
            viewing_interest=tenant_profile.get("viewing_interest") if tenant_profile else None,
            availability=tenant_profile.get("availability") if tenant_profile else None
        )
        
        if success:
            print(f"Handoff notification sent successfully for session {session_id}")
        else:
            print(f"Failed to send handoff notification for session {session_id}")
            
    except Exception as e:
        print(f"Error handling handoff notification: {e}")

def handle_session_notification(session_id: str, user_input: str, extracted_info: dict):
    """Handle new session notification to Slack"""
    try:
        # Get tenant profile if available
        tenant_profile = None
        if session_id:
            profile = conversation_memory.get_tenant_profile(session_id)
            if profile:
                tenant_profile = {
                    "age": profile.age,
                    "sex": profile.sex,
                    "occupation": profile.occupation,
                    "language_preference": profile.language_preference
                }
        
        # Send notification
        success = send_session_notification(
            session_id=session_id,
            tenant_message=user_input,
            extracted_info=extracted_info,
            tenant_age=tenant_profile.get("age") if tenant_profile else None,
            tenant_occupation=tenant_profile.get("occupation") if tenant_profile else None,
            tenant_language=tenant_profile.get("language_preference") if tenant_profile else None
        )
        
        if success:
            print(f"Session notification sent successfully for session {session_id}")
        else:
            print(f"Failed to send session notification for session {session_id}")
            
    except Exception as e:
        print(f"Error handling session notification: {e}")

def handle_message(user_input: str, property_data: str, session_id: str = None, prompt_version: str = "current") -> str:
    """
    Handle a user message with conversation memory and the specified prompt version
    
    Args:
        user_input: The user's message
        property_data: Property data to include in the prompt
        session_id: Session ID for conversation memory (optional)
        prompt_version: Which prompt version to use (default: "current")
    
    Returns:
        The agent's response
    """
    llm_available, chain = get_llm()
    
    if not llm_available:
        return "Hello! I'm the Rental Genie. I'm currently in test mode. In a real setup, I would help you with rental inquiries. Please set up your OPENAI_API_KEY environment variable to enable full functionality."
    
    try:
        # Check if session is already handed off
        if session_id:
            session = conversation_memory.get_or_create_session(session_id)
            if session.get("handoff_completed", False):
                return "I've connected you with the property owner. They will be in touch with you shortly to assist with your inquiry."
        
        # Extract information from the user's message using LLM-based extraction
        extracted_info = extract_tenant_info_llm(user_input, session_id)
        
        # Check if this is a new session (first message)
        is_new_session = False
        if session_id:
            session = conversation_memory.get_or_create_session(session_id)
            is_new_session = len(session.get("conversation_history", [])) == 0
            
            # Send session notification for new conversations
            if is_new_session:
                handle_session_notification(session_id, user_input, extracted_info)
        
        # Update conversation memory if session_id is provided
        conversation_context = ""
        if session_id:
            # Update tenant profile with extracted information
            if extracted_info:
                conversation_memory.update_tenant_profile(session_id, extracted_info)
            
            # Get conversation summary for context
            conversation_context = conversation_memory.get_conversation_summary(session_id)
            
            # Get missing information to guide the agent (only if more than 2 fields missing)
            missing_info = conversation_memory.get_missing_information(session_id, min_threshold=3)
            if missing_info:
                conversation_context += f"\n\nMissing required information: {', '.join(missing_info)}"
        
        # Detect if user expresses property interest
        interest_keywords = ["intéressé", "interested", "chambre", "room", "colocation", "available", "disponible", "louer", "rent", "location"]
        shows_interest = any(keyword in user_input.lower() for keyword in interest_keywords)
        
        if shows_interest and conversation_context:
            # Check if property_data is empty or contains no real data
            if not property_data or property_data.strip() == "[]" or "Sample Property" in property_data:
                conversation_context += f"\n\n⚠️  IMPORTANT: No real property data available in database. Inform user that property information is currently unavailable and suggest they contact the property owner directly."
            else:
                # If partial info available, attempt to filter properties
                try:
                    import json
                    property_dict = json.loads(property_data)  # Or parse as needed
                    filtered_properties = []  # Simple filter example
                    profile = conversation_memory.get_tenant_profile(session_id)
                    if profile and profile.move_in_date:
                        for prop in property_dict.get("properties", []):
                            if prop.get("availability_start") <= profile.move_in_date:
                                filtered_properties.append(prop)
                    if filtered_properties:
                        conversation_context += f"\n\nAvailable properties matching partial info: {json.dumps(filtered_properties, ensure_ascii=False)}"
                    else:
                        conversation_context += f"\n\nUser shows interest in properties—prioritize sharing details from property_data."
                except:
                    conversation_context += f"\n\nUser shows interest in properties—prioritize sharing details from property_data."
        
        # Create enhanced system prompt with conversation context
        base_prompt = get_system_prompt(property_data, prompt_version)
        
        if conversation_context:
            enhanced_prompt = f"{base_prompt}\n\nCONVERSATION CONTEXT:\n{conversation_context}\n\nUse this context to provide personalized responses and avoid asking for information already provided."
        else:
            enhanced_prompt = base_prompt
        
        # Get agent response
        print(f"=== AGENT DECISION PROCESS ===")
        print(f"User input: '{user_input}'")
        print(f"Language detection: User said '{user_input}' - should respond in {'French' if any(word in user_input.lower() for word in ['bonjour', 'salut', 'merci', 'oui', 'non', 'je', 'tu', 'vous']) else 'English'}")
        print(f"Enhanced prompt length: {len(enhanced_prompt)} characters")
        
        response = chain.predict(system=enhanced_prompt, input=user_input)
        print(f"Raw AI response: '{response[:200]}...'")
        
        # Extract JSON data from response
        json_data = extract_json_from_response(response)
        print(f"Extracted JSON data: {json_data}")
        
        # Detect handoff triggers
        handoff_triggers = detect_handoff_triggers(user_input, session_id)
        print(f"Handoff triggers detected: {handoff_triggers}")
        
        # Check if handoff is triggered (either by detection or agent response)
        handoff_triggered = (
            handoff_triggers["handoff_triggered"] or 
            json_data.get("handoff_triggered", "false").lower() == "true"
        )
        print(f"Final handoff decision: {handoff_triggered}")
        print(f"Handoff reason: {json_data.get('handoff_reason', 'None')}")
        print(f"Confidence level: {json_data.get('confidence_level', 'None')}")
        print(f"=== END AGENT DECISION PROCESS ===")
        
        # Combine handoff data
        final_handoff_data = {
            "handoff_triggered": handoff_triggered,
            "handoff_reason": (
                json_data.get("handoff_reason") or 
                handoff_triggers["handoff_reason"] or 
                "Agent determined handoff needed"
            ),
            "confidence_level": json_data.get("confidence_level", handoff_triggers["confidence_level"]),
            "escalation_priority": json_data.get("escalation_priority", handoff_triggers["escalation_priority"])
        }
        
        # Handle handoff if triggered
        if handoff_triggered and session_id:
            print(f"=== HANDOFF EXECUTION ===")
            print(f"Handoff triggered: {handoff_triggered}")
            print(f"Handoff reason: {final_handoff_data['handoff_reason']}")
            print(f"Confidence level: {final_handoff_data['confidence_level']}")
            print(f"Escalation priority: {final_handoff_data['escalation_priority']}")
            
            # Mark session as handed off
            session = conversation_memory.get_or_create_session(session_id)
            session["handoff_completed"] = True
            
            # Send notification
            conversation_summary = json_data.get("summary", "Handoff triggered")
            handle_handoff_notification(session_id, final_handoff_data, conversation_summary)
            
            # Return final response to tenant (don't mention handoff)
            if json_data.get("summary"):
                final_response = f"Thank you for your inquiry. {json_data['summary']} The property owner will be in touch with you shortly to assist with your specific needs."
            else:
                final_response = "Thank you for your inquiry. The property owner will be in touch with you shortly to assist with your specific needs."
            
            print(f"Final handoff response: '{final_response}'")
            print(f"=== END HANDOFF EXECUTION ===")
            return final_response
        
        # Store conversation turn if session_id is provided
        if session_id:
            conversation_memory.add_conversation_turn(
                session_id, 
                user_input, 
                response, 
                extracted_info
            )
        
        # Return clean response (remove JSON if present)
        clean_response = response
        if json_data:
            # Remove JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                clean_response = response.replace(json_match.group(0), "").strip()
        
        print(f"=== NORMAL RESPONSE PATH ===")
        print(f"Clean response: '{clean_response}'")
        print(f"Response length: {len(clean_response)} characters")
        print(f"=== END NORMAL RESPONSE PATH ===")
        
        return clean_response
        
    except Exception as e:
        import traceback
        print(f"=== ERROR IN handle_message ===")
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e)}")
        print(f"Full traceback:")
        traceback.print_exc()
        print(f"=== END ERROR ===")
        return f"I'm having trouble processing your request right now. Error: {str(e)}"

def get_prompt_info():
    """Get information about available prompts"""
    return prompt_manager.get_prompt_info()

def switch_prompt_version(version: str):
    """Switch to a different prompt version"""
    try:
        prompt_manager.set_current_version(version)
        return f"Successfully switched to prompt version: {version}"
    except ValueError as e:
        return f"Error: {str(e)}"

def get_conversation_memory_info(session_id: str = None):
    """Get information about conversation memory"""
    if session_id:
        profile = conversation_memory.get_tenant_profile(session_id)
        session = conversation_memory.get_or_create_session(session_id)
        if profile:
            return {
                "session_id": session_id,
                "profile_complete": conversation_memory.is_profile_complete(session_id),
                "missing_info": conversation_memory.get_missing_information(session_id),
                "conversation_turns": profile.conversation_turns,
                "last_updated": profile.last_updated,
                "handoff_completed": session.get("handoff_completed", False)
            }
        else:
            return {"session_id": session_id, "status": "not_found"}
    else:
        sessions = conversation_memory.get_all_sessions()
        return {
            "active_sessions": len(sessions),
            "session_ids": list(sessions.keys())
        }

def clear_conversation_memory(session_id: str):
    """Clear conversation memory for a session"""
    conversation_memory.clear_session(session_id)
    return f"Cleared conversation memory for session: {session_id}"

def test_slack_notification():
    """Test Slack notification functionality"""
    try:
        from .notifications import test_slack_integration
        return test_slack_integration()
    except Exception as e:
        return f"Error testing Slack notification: {e}"