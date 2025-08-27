"""
Conversation memory system for Rental Genie Agent
Stores tenant information and conversation context across multiple turns
"""

import json
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
from .enums import TenantStatus
from .supabase_utils import store_tenant_profile, get_tenant_profile, delete_tenant_profile

@dataclass
class TenantProfile:
    """Structured tenant profile data"""
    # Basic information
    age: Optional[int] = None
    sex: Optional[str] = None
    occupation: Optional[str] = None
    
    # Rental preferences
    move_in_date: Optional[str] = None
    rental_duration: Optional[str] = None
    
    # Financial/legal
    guarantor_status: Optional[str] = None
    guarantor_details: Optional[str] = None
    
    # Additional context
    viewing_interest: Optional[bool] = None
    availability: Optional[str] = None
    language_preference: Optional[str] = None
    
    # Status and workflow
    status: str = TenantStatus.PROSPECT.value  # Use enum default value
    property_interest: Optional[str] = None
    application_date: Optional[str] = None
    lease_start_date: Optional[str] = None
    lease_end_date: Optional[str] = None
    notes: Optional[str] = None
    
    # Metadata
    created_at: Optional[str] = None
    last_updated: Optional[str] = None
    conversation_turns: int = 0

@dataclass
class ConversationTurn:
    """Individual conversation turn"""
    timestamp: str
    user_message: str
    agent_response: str
    extracted_info: Dict[str, Any]

class ConversationMemory:
    """Manages conversation memory and tenant profiles"""
    
    def __init__(self, use_persistent_storage: bool = True):
        self.conversations: Dict[str, Dict[str, Any]] = {}
        self.use_persistent_storage = use_persistent_storage
    
    def get_or_create_session(self, session_id: str) -> Dict[str, Any]:
        """Get existing session or create new one"""
        if session_id not in self.conversations:
            # Try to load from persistent storage first
            if self.use_persistent_storage:
                persistent_profile = get_tenant_profile(session_id)
                if persistent_profile:
                    # Reconstruct TenantProfile from persistent data
                    tenant_profile = TenantProfile(
                        age=persistent_profile.get("age"),
                        sex=persistent_profile.get("sex"),
                        occupation=persistent_profile.get("occupation"),
                        move_in_date=persistent_profile.get("move_in_date"),
                        rental_duration=persistent_profile.get("rental_duration"),
                        guarantor_status=persistent_profile.get("guarantor_status"),
                        guarantor_details=persistent_profile.get("guarantor_details"),
                        viewing_interest=persistent_profile.get("viewing_interest"),
                        availability=persistent_profile.get("availability"),
                        language_preference=persistent_profile.get("language_preference"),
                        created_at=persistent_profile.get("created_at"),
                        last_updated=persistent_profile.get("last_updated"),
                        conversation_turns=persistent_profile.get("conversation_turns", 0)
                    )
                    
                    self.conversations[session_id] = {
                        "tenant_profile": tenant_profile,
                        "conversation_history": [],  # Note: conversation history is not persisted
                        "session_created": persistent_profile.get("created_at", datetime.now().isoformat())
                    }
                    print(f"Loaded tenant profile from persistent storage for session {session_id}")
                    return self.conversations[session_id]
            
            # Create new session if not found in persistent storage
            self.conversations[session_id] = {
                "tenant_profile": TenantProfile(
                    created_at=datetime.now().isoformat(),
                    last_updated=datetime.now().isoformat()
                ),
                "conversation_history": [],
                "session_created": datetime.now().isoformat()
            }
        return self.conversations[session_id]
    
    def update_tenant_profile(self, session_id: str, updates: Dict[str, Any]):
        """Update tenant profile with new information"""
        session = self.get_or_create_session(session_id)
        profile = session["tenant_profile"]
        
        # Update fields
        for key, value in updates.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        # Update metadata
        profile.last_updated = datetime.now().isoformat()
        profile.conversation_turns += 1
        
        # Auto-update status based on profile completion
        if self._should_auto_qualify(profile):
            profile.status = TenantStatus.QUALIFIED.value
        
        # Sync to persistent storage
        if self.use_persistent_storage:
            self._sync_to_persistent_storage(session_id, profile)
    
    def _should_auto_qualify(self, profile: TenantProfile) -> bool:
        """Check if profile should be automatically qualified"""
        required_fields = ["age", "sex", "occupation", "move_in_date", "rental_duration", "guarantor_status"]
        return all(getattr(profile, field) for field in required_fields) and profile.status == TenantStatus.PROSPECT.value
    
    def update_tenant_status(self, session_id: str, new_status: str, additional_data: Optional[Dict[str, Any]] = None):
        """Update tenant status and optionally add additional data"""
        session = self.get_or_create_session(session_id)
        profile = session["tenant_profile"]
        
        # Update status
        profile.status = new_status
        profile.last_updated = datetime.now().isoformat()
        
        # Add additional data if provided
        if additional_data:
            for key, value in additional_data.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
        
        # Sync to persistent storage
        if self.use_persistent_storage:
            from .supabase_utils import update_tenant_status
            update_tenant_status(session_id, new_status, additional_data)
            self._sync_to_persistent_storage(session_id, profile)
    
    def get_tenants_by_status(self, status: str) -> List[TenantProfile]:
        """Get all tenants with a specific status"""
        if not self.use_persistent_storage:
            # Return from memory only
            return [
                session["tenant_profile"] 
                for session in self.conversations.values() 
                if session["tenant_profile"].status == status
            ]
        
        # Get from persistent storage
        from .supabase_utils import get_tenants_by_status
        tenant_data_list = get_tenants_by_status(status)
        
        tenants = []
        for tenant_data in tenant_data_list:
            tenant = TenantProfile(
                age=tenant_data.get("age"),
                sex=tenant_data.get("sex"),
                occupation=tenant_data.get("occupation"),
                move_in_date=tenant_data.get("move_in_date"),
                rental_duration=tenant_data.get("rental_duration"),
                guarantor_status=tenant_data.get("guarantor_status"),
                guarantor_details=tenant_data.get("guarantor_details"),
                viewing_interest=tenant_data.get("viewing_interest"),
                availability=tenant_data.get("availability"),
                language_preference=tenant_data.get("language_preference"),
                status=tenant_data.get("status", TenantStatus.PROSPECT.value),
                property_interest=tenant_data.get("property_interest"),
                application_date=tenant_data.get("application_date"),
                lease_start_date=tenant_data.get("lease_start_date"),
                lease_end_date=tenant_data.get("lease_end_date"),
                notes=tenant_data.get("notes"),
                created_at=tenant_data.get("created_at"),
                last_updated=tenant_data.get("last_updated"),
                conversation_turns=tenant_data.get("conversation_turns", 0)
            )
            tenants.append(tenant)
        
        return tenants
    
    def get_prospects(self) -> List[TenantProfile]:
        """Get all prospect tenants"""
        return self.get_tenants_by_status(TenantStatus.PROSPECT.value)
    
    def get_qualified_prospects(self) -> List[TenantProfile]:
        """Get all qualified prospects"""
        return self.get_tenants_by_status(TenantStatus.QUALIFIED.value)
    
    def get_active_tenants(self) -> List[TenantProfile]:
        """Get all active tenants"""
        return self.get_tenants_by_status(TenantStatus.ACTIVE_TENANT.value)
    
    def _sync_to_persistent_storage(self, session_id: str, profile: TenantProfile):
        """Sync tenant profile to persistent storage"""
        try:
            profile_dict = asdict(profile)
            success = store_tenant_profile(session_id, profile_dict)
            if success:
                print(f"Synced tenant profile to persistent storage for session {session_id}")
            else:
                print(f"Failed to sync tenant profile for session {session_id}")
        except Exception as e:
            print(f"Error syncing to persistent storage: {e}")
    
    def add_conversation_turn(self, session_id: str, user_message: str, agent_response: str, extracted_info: Dict[str, Any]):
        """Add a conversation turn to the history"""
        session = self.get_or_create_session(session_id)
        
        turn = ConversationTurn(
            timestamp=datetime.now().isoformat(),
            user_message=user_message,
            agent_response=agent_response,
            extracted_info=extracted_info
        )
        
        session["conversation_history"].append(asdict(turn))
        
        # Update conversation turns count
        session["tenant_profile"].conversation_turns = len(session["conversation_history"])
        
        # Sync to persistent storage
        if self.use_persistent_storage:
            self._sync_to_persistent_storage(session_id, session["tenant_profile"])
    
    def get_tenant_profile(self, session_id: str) -> Optional[TenantProfile]:
        """Get tenant profile for a session"""
        if session_id in self.conversations:
            return self.conversations[session_id]["tenant_profile"]
        
        # Try to load from persistent storage if not in memory
        if self.use_persistent_storage:
            persistent_profile = get_tenant_profile(session_id)
            if persistent_profile:
                return TenantProfile(
                    age=persistent_profile.get("age"),
                    sex=persistent_profile.get("sex"),
                    occupation=persistent_profile.get("occupation"),
                    move_in_date=persistent_profile.get("move_in_date"),
                    rental_duration=persistent_profile.get("rental_duration"),
                    guarantor_status=persistent_profile.get("guarantor_status"),
                    guarantor_details=persistent_profile.get("guarantor_details"),
                    viewing_interest=persistent_profile.get("viewing_interest"),
                    availability=persistent_profile.get("availability"),
                    language_preference=persistent_profile.get("language_preference"),
                    created_at=persistent_profile.get("created_at"),
                    last_updated=persistent_profile.get("last_updated"),
                    conversation_turns=persistent_profile.get("conversation_turns", 0)
                )
        
        return None
    
    def get_conversation_summary(self, session_id: str) -> str:
        """Get a summary of the conversation for the agent"""
        if session_id not in self.conversations:
            return "No previous conversation found."
        
        session = self.conversations[session_id]
        profile = session["tenant_profile"]
        history = session["conversation_history"]
        
        summary = f"Conversation Summary (Session: {session_id}):\n"
        summary += f"- Total turns: {len(history)}\n"
        summary += f"- Last updated: {profile.last_updated}\n\n"
        
        summary += "Collected Information:\n"
        if profile.age:
            summary += f"- Age: {profile.age}\n"
        if profile.sex:
            summary += f"- Sex: {profile.sex}\n"
        if profile.occupation:
            summary += f"- Occupation: {profile.occupation}\n"
        if profile.move_in_date:
            summary += f"- Move-in date: {profile.move_in_date}\n"
        if profile.rental_duration:
            summary += f"- Rental duration: {profile.rental_duration}\n"
        if profile.guarantor_status:
            summary += f"- Guarantor status: {profile.guarantor_status}\n"
        if profile.guarantor_details:
            summary += f"- Guarantor details: {profile.guarantor_details}\n"
        if profile.viewing_interest:
            summary += f"- Viewing interest: {profile.viewing_interest}\n"
        if profile.availability:
            summary += f"- Availability: {profile.availability}\n"
        
        # Add recent conversation context
        if history:
            summary += "\nRecent conversation context:\n"
            for turn in history[-3:]:  # Last 3 turns
                summary += f"- User: {turn['user_message'][:100]}...\n"
                summary += f"- Agent: {turn['agent_response'][:100]}...\n"
        
        return summary
    
    def get_missing_information(self, session_id: str) -> List[str]:
        """Get list of missing required information"""
        if session_id not in self.conversations:
            return ["age", "sex", "occupation", "move_in_date", "rental_duration", "guarantor_status"]
        
        profile = self.conversations[session_id]["tenant_profile"]
        missing = []
        
        if not profile.age:
            missing.append("age")
        if not profile.sex:
            missing.append("sex")
        if not profile.occupation:
            missing.append("occupation")
        if not profile.move_in_date:
            missing.append("move_in_date")
        if not profile.rental_duration:
            missing.append("rental_duration")
        if not profile.guarantor_status:
            missing.append("guarantor_status")
        
        return missing
    
    def is_profile_complete(self, session_id: str) -> bool:
        """Check if tenant profile is complete"""
        return len(self.get_missing_information(session_id)) == 0
    
    def clear_session(self, session_id: str):
        """Clear a session (for testing or privacy)"""
        if session_id in self.conversations:
            del self.conversations[session_id]
        
        # Also delete from persistent storage
        if self.use_persistent_storage:
            delete_tenant_profile(session_id)
    
    def get_all_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Get all active sessions (for debugging)"""
        return self.conversations.copy()
    
    def load_all_from_persistent_storage(self):
        """Load all tenant profiles from persistent storage into memory"""
        if not self.use_persistent_storage:
            return
        
        try:
            from .supabase_utils import get_all_tenant_profiles
            all_profiles = get_all_tenant_profiles()
            
            for profile_data in all_profiles:
                session_id = profile_data.get("session_id")
                if session_id and session_id not in self.conversations:
                    tenant_profile = TenantProfile(
                        age=profile_data.get("age"),
                        sex=profile_data.get("sex"),
                        occupation=profile_data.get("occupation"),
                        move_in_date=profile_data.get("move_in_date"),
                        rental_duration=profile_data.get("rental_duration"),
                        guarantor_status=profile_data.get("guarantor_status"),
                        viewing_interest=profile_data.get("viewing_interest"),
                        created_at=profile_data.get("created_at"),
                        last_updated=profile_data.get("last_updated")
                    )
                    
                    self.conversations[session_id] = {
                        "tenant_profile": tenant_profile,
                        "conversation_history": [],
                        "session_created": profile_data.get("created_at", datetime.now().isoformat())
                    }
            
            print(f"Loaded {len(all_profiles)} tenant profiles from persistent storage")
            
        except Exception as e:
            print(f"Error loading from persistent storage: {e}")

# Global conversation memory instance with persistent storage enabled
conversation_memory = ConversationMemory(use_persistent_storage=True)

def extract_tenant_info(message: str) -> Dict[str, Any]:
    """
    Extract tenant information from a message
    Enhanced to extract multiple pieces of information from comprehensive messages
    """
    extracted = {}
    message_lower = message.lower()
    
    # Age extraction - multiple patterns
    import re
    age_patterns = [
        r'(\d+)\s*(?:years?\s*old|ans?)',
        r'age[:\s]*(\d+)',
        r'i\s*am\s*(\d+)\s*(?:years?|ans?)',
        r'(\d+)\s*(?:years?|ans?)\s*old'
    ]
    for pattern in age_patterns:
        age_match = re.search(pattern, message_lower)
        if age_match:
            extracted['age'] = int(age_match.group(1))
            break
    
    # Sex/gender extraction - multiple patterns
    sex_patterns = [
        (r'\b(male|homme|man|masculin)\b', 'male'),
        (r'\b(female|femme|woman|feminin)\b', 'female'),
        (r'i\s*am\s*(male|homme|man)', 'male'),
        (r'i\s*am\s*(female|femme|woman)', 'female'),
        (r'sex[:\s]*(male|homme|man)', 'male'),
        (r'sex[:\s]*(female|femme|woman)', 'female')
    ]
    for pattern, sex in sex_patterns:
        if re.search(pattern, message_lower):
            extracted['sex'] = sex
            break
    
    # Occupation extraction - enhanced patterns
    occupation_keywords = [
        'work as', 'job', 'profession', 'travaille comme', 'métier', 'occupation',
        'i am a', 'je suis', 'i work', 'je travaille', 'employed as', 'employed at'
    ]
    
    for keyword in occupation_keywords:
        if keyword in message_lower:
            # Extract occupation after the keyword
            start_idx = message_lower.find(keyword) + len(keyword)
            # Look for end of sentence or common separators
            end_patterns = [r'\.', r',', r'\sand\s', r'\sbut\s', r'\salso\s', r'\splus\s']
            end_idx = len(message)
            for pattern in end_patterns:
                match = re.search(pattern, message[start_idx:])
                if match:
                    potential_end = start_idx + match.start()
                    if potential_end < end_idx:
                        end_idx = potential_end
            
            occupation = message[start_idx:end_idx].strip()
            if occupation and len(occupation) > 2:  # Avoid very short extractions
                extracted['occupation'] = occupation
                break
    
    # Move-in date extraction - enhanced patterns
    date_patterns = [
        r'(?:move in|move-in|déménager|emménager|arrival|arrivée)\s+(?:on\s+)?([^,\.]+)',
        r'(?:want to move|veux déménager|souhaite déménager)\s+(?:on\s+)?([^,\.]+)',
        r'(\d{1,2}(?:st|nd|rd|th)?\s+(?:january|february|march|april|may|june|july|august|september|october|november|december))',
        r'(\d{1,2}/\d{1,2}/\d{4})',
        r'(\d{1,2}-\d{1,2}-\d{4})',
        r'(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec))',
        r'(?:start|begin|commencer)\s+(?:on\s+)?([^,\.]+)',
        r'(?:available|disponible)\s+(?:from\s+)?([^,\.]+)'
    ]
    for pattern in date_patterns:
        match = re.search(pattern, message_lower)
        if match:
            extracted['move_in_date'] = match.group(1).strip()
            break
    
    # Rental duration extraction - enhanced patterns
    duration_patterns = [
        r'(\d+)\s*(?:months?|mois)',
        r'(?:stay|rester|remain|rester)\s+(?:for\s+)?(\d+)\s*(?:months?|mois)',
        r'(\d+)\s*(?:month|mois)\s*(?:lease|bail)',
        r'(?:duration|durée)\s*(?:of\s+)?(\d+)\s*(?:months?|mois)',
        r'(?:can stay|peux rester|peut rester)\s+(?:for\s+)?(\d+)\s*(?:months?|mois)',
        r'(?:minimum|minimum)\s+(\d+)\s*(?:months?|mois)',
        r'(?:long term|long terme)\s+(?:of\s+)?(\d+)\s*(?:months?|mois)'
    ]
    for pattern in duration_patterns:
        match = re.search(pattern, message_lower)
        if match:
            extracted['rental_duration'] = f"{match.group(1)} months"
            break
    
    # Guarantor extraction - enhanced patterns
    guarantor_patterns = [
        (r'\b(guarantor|garant)\b', 'yes'),
        (r'have\s+a\s+guarantor', 'yes'),
        (r'ai\s+un\s+garant', 'yes'),
        (r'no\s+guarantor', 'no'),
        (r'pas\s+de\s+garant', 'no'),
        (r'need\s+guarantor', 'need'),
        (r'besoin\s+d\'un\s+garant', 'need'),
        (r'garantie\s+visale', 'visale'),
        (r'visale\s+guarantee', 'visale')
    ]
    
    for pattern, status in guarantor_patterns:
        if re.search(pattern, message_lower):
            extracted['guarantor_status'] = status
            break
    
    # Extract guarantor details if mentioned
    if extracted.get('guarantor_status') == 'yes':
        guarantor_details_patterns = [
            (r'(father|père|dad|papa)', 'father'),
            (r'(mother|mère|mom|maman)', 'mother'),
            (r'(parent|parents)', 'parent'),
            (r'(accountant|comptable)', 'accountant'),
            (r'(employer|employeur)', 'employer'),
            (r'(friend|ami)', 'friend'),
            (r'(sibling|frère|sœur)', 'sibling')
        ]
        
        for pattern, detail in guarantor_details_patterns:
            if re.search(pattern, message_lower):
                extracted['guarantor_details'] = detail
                break
    
    # Viewing interest extraction
    viewing_patterns = [
        (r'(?:would like|souhaite|veux)\s+(?:to\s+)?(?:schedule|organiser)\s+(?:a\s+)?(?:viewing|visite)', True),
        (r'(?:interested in|intéressé par)\s+(?:a\s+)?(?:viewing|visite)', True),
        (r'(?:can|peux|peut)\s+(?:we\s+)?(?:schedule|organiser)\s+(?:a\s+)?(?:viewing|visite)', True),
        (r'(?:not interested|pas intéressé)', False),
        (r'(?:no viewing|pas de visite)', False)
    ]
    
    for pattern, interest in viewing_patterns:
        if re.search(pattern, message_lower):
            extracted['viewing_interest'] = interest
            break
    
    # Availability extraction
    availability_patterns = [
        r'(?:available|disponible)\s+(?:on\s+)?([^,\.]+)',
        r'(?:free|libre)\s+(?:on\s+)?([^,\.]+)',
        r'(?:can meet|peux rencontrer)\s+(?:on\s+)?([^,\.]+)',
        r'(?:prefer|préfère)\s+([^,\.]+)',
        r'(?:weekends?|week-end)', 'weekends',
        r'(?:weekdays?|semaine)', 'weekdays',
        r'(?:evenings?|soir)', 'evenings',
        r'(?:mornings?|matin)', 'mornings'
    ]
    
    for pattern in availability_patterns:
        if isinstance(pattern, str):
            if re.search(pattern, message_lower):
                match = re.search(pattern, message_lower)
                if match.groups():
                    extracted['availability'] = match.group(1).strip()
                else:
                    extracted['availability'] = pattern
                break
        else:
            if re.search(pattern, message_lower):
                extracted['availability'] = pattern
                break
    
    # Language preference detection
    french_words = ['bonjour', 'salut', 'merci', 'oui', 'non', 'je', 'suis', 'veux', 'peux', 'avoir']
    english_words = ['hello', 'hi', 'thanks', 'yes', 'no', 'i', 'am', 'want', 'can', 'have']
    
    french_count = sum(1 for word in french_words if word in message_lower)
    english_count = sum(1 for word in english_words if word in message_lower)
    
    if french_count > english_count:
        extracted['language_preference'] = 'French'
    elif english_count > french_count:
        extracted['language_preference'] = 'English'
    
    return extracted
