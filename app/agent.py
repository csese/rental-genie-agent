from langchain_core.prompts import ChatPromptTemplate
from langchain_core.memory import BaseMemory
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
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
    
    # Language barrier detection
    if session_id:
        profile = conversation_memory.get_tenant_profile(session_id)
        if profile and profile.language_preference:
            # If language preference is set but communication seems difficult
            if len(user_input.split()) < 3 or any(word in user_input_lower for word in ["sorry", "not understand", "confused", "help"]):
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
        
        # Extract information from the user's message
        extracted_info = extract_tenant_info(user_input)
        
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
            
            # Get missing information to guide the agent
            missing_info = conversation_memory.get_missing_information(session_id)
            if missing_info:
                conversation_context += f"\n\nMissing required information: {', '.join(missing_info)}"
        
        # Create enhanced system prompt with conversation context
        base_prompt = get_system_prompt(property_data, prompt_version)
        
        if conversation_context:
            enhanced_prompt = f"{base_prompt}\n\nCONVERSATION CONTEXT:\n{conversation_context}\n\nUse this context to provide personalized responses and avoid asking for information already provided."
        else:
            enhanced_prompt = base_prompt
        
        # Get agent response
        response = chain.predict(system=enhanced_prompt, input=user_input)
        
        # Extract JSON data from response
        json_data = extract_json_from_response(response)
        
        # Detect handoff triggers
        handoff_triggers = detect_handoff_triggers(user_input, session_id)
        
        # Check if handoff is triggered (either by detection or agent response)
        handoff_triggered = (
            handoff_triggers["handoff_triggered"] or 
            json_data.get("handoff_triggered", "false").lower() == "true"
        )
        
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
            # Mark session as handed off
            session = conversation_memory.get_or_create_session(session_id)
            session["handoff_completed"] = True
            
            # Send notification
            conversation_summary = json_data.get("summary", "Handoff triggered")
            handle_handoff_notification(session_id, final_handoff_data, conversation_summary)
            
            # Return final response to tenant (don't mention handoff)
            if json_data.get("summary"):
                return f"Thank you for your inquiry. {json_data['summary']} The property owner will be in touch with you shortly to assist with your specific needs."
            else:
                return "Thank you for your inquiry. The property owner will be in touch with you shortly to assist with your specific needs."
        
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
        
        return clean_response
        
    except Exception as e:
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