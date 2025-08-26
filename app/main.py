from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from typing import Optional, Dict, Any, List
import logging
import os
import httpx
from .agent import handle_message, get_prompt_info, switch_prompt_version, get_conversation_memory_info, clear_conversation_memory, test_slack_notification
from .supabase_utils import get_all_property_info, get_all_tenant_profiles, get_tenant_profile, delete_tenant_profile, update_tenant_status, get_tenants_by_status, get_prospects, get_qualified_prospects, get_active_tenants, get_tenant_status_info, add_conversation_message, get_conversation_history, increment_conversation_turns, mark_handoff_completed
from .conversation_memory import TenantStatus
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Rental Genie Agent", description="An intelligent agent for rental property inquiries")

# Add CORS middleware for deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production - replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class MessageRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    prompt_version: Optional[str] = "current"  # New field for prompt versioning

class MessageResponse(BaseModel):
    response: str
    status: str
    session_id: Optional[str] = None
    confidence: Optional[float] = None
    prompt_version: Optional[str] = None  # New field to show which prompt was used
    profile_complete: Optional[bool] = None  # New field to show if profile is complete

class HealthResponse(BaseModel):
    status: str
    message: str

class PromptInfoResponse(BaseModel):
    current_version: str
    available_versions: list
    total_versions: int

class PromptVersionRequest(BaseModel):
    version: str

class ConversationMemoryResponse(BaseModel):
    session_id: Optional[str] = None
    profile_complete: Optional[bool] = None
    missing_info: Optional[list] = None
    conversation_turns: Optional[int] = None
    last_updated: Optional[str] = None
    active_sessions: Optional[int] = None
    session_ids: Optional[list] = None

class TenantProfileResponse(BaseModel):
    session_id: Optional[str] = None
    status: str = "prospect"
    age: Optional[int] = None
    sex: Optional[str] = None
    occupation: Optional[str] = None
    move_in_date: Optional[str] = None
    rental_duration: Optional[str] = None
    guarantor_status: Optional[str] = None
    guarantor_details: Optional[str] = None
    viewing_interest: Optional[bool] = None
    availability: Optional[str] = None
    language_preference: Optional[str] = None
    property_interest: Optional[str] = None
    application_date: Optional[str] = None
    lease_start_date: Optional[str] = None
    lease_end_date: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None
    last_updated: Optional[str] = None
    conversation_turns: Optional[int] = None

class TenantsListResponse(BaseModel):
    tenants: List[TenantProfileResponse]
    total_count: int

class StatusUpdateRequest(BaseModel):
    status: str
    additional_data: Optional[Dict[str, Any]] = None

class TenantStatsResponse(BaseModel):
    total_tenants: int
    prospects: int
    qualified: int
    viewing_scheduled: int
    application_submitted: int
    approved: int
    active_tenants: int
    former_tenants: int
    rejected: int
    withdrawn: int

class TenantStatusInfoResponse(BaseModel):
    statuses: List[Dict[str, str]]
    valid_values: List[str]

class SlackTestResponse(BaseModel):
    success: bool
    message: str

class HandoffTestRequest(BaseModel):
    session_id: str
    handoff_reason: str
    escalation_priority: str = "medium"

# Global property data cache
property_data_cache = None

def load_property_data():
    """Load and cache property data"""
    global property_data_cache
    try:
        if property_data_cache is None:
            property_data_cache = get_all_property_info()
            logger.info("Property data loaded successfully")
        return property_data_cache
    except Exception as e:
        logger.error(f"Error loading property data: {e}")
        # Provide fallback property data for testing
        return [{"fields": {"Name": "Sample Property", "Address": "123 Main St", "Rent": "$1500/month", "Available": "January 2024"}}]

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(status="healthy", message="Rental Genie Agent is running")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check"""
    try:
        property_data = load_property_data()
        if property_data:
            return HealthResponse(status="healthy", message="Agent is ready to handle messages")
        else:
            return HealthResponse(status="warning", message="Agent is running but property data is unavailable")
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(status="error", message=f"Health check failed: {str(e)}")

@app.post("/chat", response_model=MessageResponse)
async def chat_endpoint(request: MessageRequest):
    """Main chat endpoint for receiving messages and getting responses"""
    try:
        # Load property data
        property_data = load_property_data()
        if not property_data:
            raise HTTPException(status_code=500, detail="Property data not available")
        
        # Convert property data to string for the agent
        property_data_str = str(property_data)
        
        # Use session_id if provided, otherwise generate one
        session_id = request.session_id or f"session_{request.user_id or 'anonymous'}_{int(time.time())}"
        
        # Handle the message through the agent with conversation memory
        response = handle_message(
            request.message, 
            property_data_str, 
            session_id,
            request.prompt_version
        )
        
        # Get conversation memory info
        memory_info = get_conversation_memory_info(session_id)
        
        # Create response
        return MessageResponse(
            response=response,
            status="success",
            session_id=session_id,
            confidence=0.9,
            prompt_version=request.prompt_version,
            profile_complete=memory_info.get("profile_complete", False)
        )
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.get("/prompts", response_model=PromptInfoResponse)
async def get_prompts():
    """Get information about available prompt versions"""
    try:
        prompt_info = get_prompt_info()
        return PromptInfoResponse(**prompt_info)
    except Exception as e:
        logger.error(f"Error getting prompt info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/prompts/switch")
async def switch_prompt(request: PromptVersionRequest):
    """Switch to a different prompt version"""
    try:
        result = switch_prompt_version(request.version)
        return {"message": result, "current_version": request.version}
    except Exception as e:
        logger.error(f"Error switching prompt version: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversation/{session_id}", response_model=ConversationMemoryResponse)
async def get_conversation_info(session_id: str):
    """Get conversation memory information for a specific session"""
    try:
        memory_info = get_conversation_memory_info(session_id)
        return ConversationMemoryResponse(**memory_info)
    except Exception as e:
        logger.error(f"Error getting conversation info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversation", response_model=ConversationMemoryResponse)
async def get_all_conversations():
    """Get information about all active conversations"""
    try:
        memory_info = get_conversation_memory_info()
        return ConversationMemoryResponse(**memory_info)
    except Exception as e:
        logger.error(f"Error getting conversations info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/conversation/{session_id}")
async def clear_conversation(session_id: str):
    """Clear conversation memory for a specific session"""
    try:
        result = clear_conversation_memory(session_id)
        return {"message": result}
    except Exception as e:
        logger.error(f"Error clearing conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/webhook")
async def facebook_webhook_verification(request: Request):
    """Facebook webhook verification endpoint"""
    try:
        # Get query parameters
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")
        
        # Your verify token (set this in Facebook Developer Console)
        verify_token = os.environ.get("FACEBOOK_VERIFY_TOKEN")
        
        # Check if mode and token are correct
        if mode == "subscribe" and token == verify_token:
            logger.info("Facebook webhook verified successfully")
            return int(challenge)
        else:
            logger.error(f"Facebook webhook verification failed: mode={mode}, token={token}")
            raise HTTPException(status_code=403, detail="Forbidden")
            
    except Exception as e:
        logger.error(f"Facebook webhook verification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook")
async def facebook_webhook(request: Request):
    """Facebook webhook endpoint for receiving messages"""
    try:
        data = await request.json()
        logger.info(f"Received Facebook webhook: {data}")
        
        # Validate signature for security (add this)
        signature = request.headers.get('X-Hub-Signature-256')
        if not signature:
            logger.error("Missing X-Hub-Signature-256")
            raise HTTPException(status_code=403, detail="Invalid signature")
        
        # Compute expected signature (use your app secret from Facebook App dashboard)
        app_secret = os.environ.get("FACEBOOK_APP_SECRET")
        if not app_secret:
            logger.error("FACEBOOK_APP_SECRET not set")
            raise HTTPException(status_code=500, detail="App secret not configured")
        
        # Hash the body with HMAC-SHA256 and app secret
        import hmac
        import hashlib
        expected_sig = 'sha256=' + hmac.new(
            app_secret.encode('utf-8'),
            await request.body(),
            hashlib.sha256
        ).hexdigest()
        
        if signature != expected_sig:
            logger.error(f"Signature mismatch: received {signature}, expected {expected_sig}")
            raise HTTPException(status_code=403, detail="Invalid signature")
        
        # Handle Facebook webhook format
        if 'entry' in data and len(data['entry']) > 0:
            for entry in data['entry']:
                if 'messaging' in entry and len(entry['messaging']) > 0:
                    for messaging in entry['messaging']:
                        if 'message' in messaging and 'text' in messaging['message']:
                            user_msg = messaging['message']['text']
                            user_id = messaging['sender']['id']
                            
                            logger.info(f"Processing message from user {user_id}: {user_msg}")
                            
                            # Load property data and convert to string
                            property_data = load_property_data()
                            if not property_data:
                                logger.error("Property data not available")
                                continue
                            property_data_str = str(property_data)
                            
                            # Generate session_id based on user_id (for conversation tracking)
                            session_id = f"fb_{user_id}_{int(time.time())}"  # Or use a persistent store
                            
                            # Handle the message (fix: add missing params)
                            response = handle_message(
                                user_msg, 
                                property_data_str, 
                                session_id,
                                prompt_version="current"  # Default
                            )
                            
                            # Send response back via Facebook API
                            await send_facebook_message(user_id, response)
                            
                            logger.info(f"Sent response to user {user_id}: {response}")
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Facebook webhook error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

async def send_facebook_message(user_id: str, message: str):
    """Send message to Facebook user via Facebook API"""
    try:
        # Get Facebook access token from environment
        access_token = os.environ.get("FACEBOOK_ACCESS_TOKEN")
        if not access_token:
            logger.error("FACEBOOK_ACCESS_TOKEN not set")
            return
        
        # Facebook Messenger API endpoint - use page ID instead of 'me'
        # First, try to get the page ID from the access token
        page_id = None
        try:
            # Get page info from access token
            page_url = f"https://graph.facebook.com/v23.0/me?access_token={access_token}"
            async with httpx.AsyncClient() as client:
                page_response = await client.get(page_url)
                if page_response.status_code == 200:
                    page_data = page_response.json()
                    page_id = page_data.get('id')
                    logger.info(f"Using page ID: {page_id}")
                else:
                    logger.error(f"Failed to get page info: {page_response.text}")
                    return
        except Exception as e:
            logger.error(f"Error getting page info: {e}")
            return
        
        if not page_id:
            logger.error("Could not determine page ID from access token")
            return
        
        # Use page ID in the messages endpoint
        url = f"https://graph.facebook.com/v23.0/{page_id}/messages?access_token={access_token}"
        
        # Message payload
        payload = {
            "recipient": {"id": user_id},
            "message": {"text": message}
        }
        
        # Send message
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            
            if response.status_code == 200:
                logger.info(f"Message sent successfully to user {user_id}")
            else:
                logger.error(f"Failed to send message to user {user_id}: {response.text}")
                
    except Exception as e:
        logger.error(f"Error sending Facebook message: {e}")

@app.post("/webhook/generic")
async def generic_webhook(request: Request):
    """Generic webhook endpoint for any platform"""
    try:
        data = await request.json()
        
        # Extract message from generic format
        user_msg = data.get('message', '')
        user_id = data.get('user_id', '')
        session_id = data.get('session_id', '')
        
        if not user_msg:
            return JSONResponse(status_code=400, content={"error": "No message provided"})
        
        # Load property data
        property_data = load_property_data()
        if not property_data:
            return JSONResponse(status_code=500, content={"error": "Property data not available"})
        
        # Handle the message
        response = handle_message(user_msg, property_data)
        
        return {
            "status": "success",
            "response": response,
            "user_id": user_id,
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"Generic webhook error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/properties")
async def get_properties():
    """Endpoint to get available properties"""
    try:
        property_data = load_property_data()
        if not property_data:
            raise HTTPException(status_code=500, detail="Property data not available")
        
        return {"properties": property_data, "count": len(property_data)}
        
    except Exception as e:
        logger.error(f"Error fetching properties: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/properties/{property_id}")
async def get_property_by_id(property_id: str):
    """Get a specific property by ID"""
    try:
        property_data = load_property_data()
        if not property_data:
            raise HTTPException(status_code=500, detail="Property data not available")
        
        # Find the property by ID
        for prop in property_data:
            if prop.get('id') == property_id:
                return prop
        
        raise HTTPException(status_code=404, detail="Property not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching property: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class PropertyUpdateRequest(BaseModel):
    """Request model for property updates"""
    property_name: Optional[str] = None
    address_street: Optional[str] = None
    city: Optional[str] = None
    zip_code: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    rent_amount: Optional[float] = None
    utilities_amount: Optional[float] = None
    date_of_availability: Optional[str] = None
    deposit_amount: Optional[float] = None
    room_sub_name: Optional[str] = None
    apartment_name: Optional[str] = None

class BulkTenantUpdateRequest(BaseModel):
    """Request model for bulk tenant updates"""
    session_ids: List[str]
    status: str
    additional_data: Optional[Dict[str, Any]] = None

@app.put("/properties/{property_id}")
async def update_property(property_id: str, request: PropertyUpdateRequest):
    """Update a specific property"""
    try:
        # For now, we'll update the cached data
        # In a production system, this would update Airtable directly
        global property_data_cache
        
        if property_data_cache is None:
            property_data_cache = load_property_data()
        
        # Find and update the property
        for prop in property_data_cache:
            if prop.get('id') == property_id:
                fields = prop.get('fields', {})
                
                # Update only the fields that are provided
                if request.property_name is not None:
                    fields['property_name'] = request.property_name
                if request.address_street is not None:
                    fields['address_street'] = request.address_street
                if request.city is not None:
                    fields['city'] = request.city
                if request.zip_code is not None:
                    fields['zip_code'] = request.zip_code
                if request.description is not None:
                    fields['Description'] = request.description
                if request.status is not None:
                    fields['status'] = request.status
                if request.rent_amount is not None:
                    fields['rent_amount'] = request.rent_amount
                if request.utilities_amount is not None:
                    fields['utilities_amout'] = request.utilities_amount
                if request.date_of_availability is not None:
                    fields['date_of_availability'] = request.date_of_availability
                if request.deposit_amount is not None:
                    fields['deposit_amount'] = request.deposit_amount
                if request.room_sub_name is not None:
                    fields['room_sub_name'] = request.room_sub_name
                if request.apartment_name is not None:
                    fields['apartment_name'] = request.apartment_name
                
                logger.info(f"Property {property_id} updated successfully")
                return {"message": "Property updated successfully", "property_id": property_id}
        
        raise HTTPException(status_code=404, detail="Property not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating property: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/tenants/bulk-update")
async def bulk_update_tenants(request: BulkTenantUpdateRequest):
    """Bulk update tenant statuses"""
    try:
        # Validate status using enum
        if not TenantStatus.is_valid(request.status):
            valid_statuses = TenantStatus.get_all_values()
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status '{request.status}'. Must be one of: {valid_statuses}"
            )
        
        updated_count = 0
        failed_updates = []
        
        for session_id in request.session_ids:
            try:
                success = update_tenant_status(session_id, request.status, request.additional_data)
                if success:
                    updated_count += 1
                else:
                    failed_updates.append(session_id)
            except Exception as e:
                logger.error(f"Error updating tenant {session_id}: {e}")
                failed_updates.append(session_id)
        
        return {
            "message": f"Bulk update completed",
            "updated_count": updated_count,
            "failed_count": len(failed_updates),
            "failed_session_ids": failed_updates
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk tenant update: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tenants", response_model=TenantsListResponse)
async def get_all_tenants(status: Optional[str] = None):
    """Get all tenant profiles from persistent storage, optionally filtered by status"""
    try:
        if status:
            tenants_data = get_tenants_by_status(status)
        else:
            tenants_data = get_all_tenant_profiles()
        
        tenants = []
        for tenant_data in tenants_data:
            session_id = tenant_data.get("session_id")
            if session_id is None:
                session_id = f"tenant_{len(tenants)}"  # Generate a default session_id
                
            tenant = TenantProfileResponse(
                session_id=session_id,
                status=tenant_data.get("status", "prospect"),
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
                property_interest=tenant_data.get("property_interest"),
                application_date=tenant_data.get("application_date"),
                lease_start_date=tenant_data.get("lease_start_date"),
                lease_end_date=tenant_data.get("lease_end_date"),
                notes=tenant_data.get("notes"),
                created_at=tenant_data.get("created_at"),
                last_updated=tenant_data.get("last_updated"),
                conversation_turns=tenant_data.get("conversation_turns")
            )
            tenants.append(tenant)
        
        return TenantsListResponse(tenants=tenants, total_count=len(tenants))
        
    except Exception as e:
        logger.error(f"Error fetching tenants: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tenants/{session_id}", response_model=TenantProfileResponse)
async def get_tenant_by_session(session_id: str):
    """Get a specific tenant profile by session ID"""
    try:
        tenant_data = get_tenant_profile(session_id)
        
        if not tenant_data:
            raise HTTPException(status_code=404, detail="Tenant profile not found")
        
        tenant = TenantProfileResponse(
            session_id=session_id,
            status=tenant_data.get("status", "prospect"),
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
            property_interest=tenant_data.get("property_interest"),
            application_date=tenant_data.get("application_date"),
            lease_start_date=tenant_data.get("lease_start_date"),
            lease_end_date=tenant_data.get("lease_end_date"),
            notes=tenant_data.get("notes"),
            created_at=tenant_data.get("created_at"),
            last_updated=tenant_data.get("last_updated"),
            conversation_turns=tenant_data.get("conversation_turns")
        )
        
        return tenant
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching tenant profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/tenants/{session_id}/status")
async def update_tenant_status_endpoint(session_id: str, request: StatusUpdateRequest):
    """Update tenant status and optionally add additional data"""
    try:
        # Validate status using enum
        if not TenantStatus.is_valid(request.status):
            valid_statuses = TenantStatus.get_all_values()
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status '{request.status}'. Must be one of: {valid_statuses}"
            )
        
        success = update_tenant_status(session_id, request.status, request.additional_data)
        
        if not success:
            raise HTTPException(status_code=404, detail="Tenant profile not found")
        
        display_name = TenantStatus.get_display_name(request.status)
        return {"message": f"Tenant status updated to '{display_name}' successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tenant status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tenants/stats", response_model=TenantStatsResponse)
async def get_tenant_stats():
    """Get statistics about tenants by status"""
    try:
        all_tenants = get_all_tenant_profiles()
        
        # Initialize stats with all possible statuses
        stats = {
            "total_tenants": len(all_tenants),
            "prospects": 0,
            "qualified": 0,
            "viewing_scheduled": 0,
            "application_submitted": 0,
            "approved": 0,
            "active_tenants": 0,
            "former_tenants": 0,
            "rejected": 0,
            "withdrawn": 0
        }
        
        for tenant in all_tenants:
            status = tenant.get("status", TenantStatus.PROSPECT.value)
            if status in stats:
                stats[status] += 1
        
        return TenantStatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Error fetching tenant stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tenants/status-info", response_model=TenantStatusInfoResponse)
async def get_tenant_status_info_endpoint():
    """Get information about all available tenant statuses"""
    try:
        status_info = get_tenant_status_info()
        return TenantStatusInfoResponse(**status_info)
        
    except Exception as e:
        logger.error(f"Error fetching tenant status info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tenants/prospects", response_model=TenantsListResponse)
async def get_prospects_endpoint():
    """Get all prospect tenants"""
    try:
        prospects_data = get_prospects()
        
        prospects = []
        for tenant_data in prospects_data:
            tenant = TenantProfileResponse(
                session_id=tenant_data.get("session_id", ""),
                status=tenant_data.get("status", "prospect"),
                age=tenant_data.get("age"),
                sex=tenant_data.get("sex"),
                occupation=tenant_data.get("occupation"),
                move_in_date=tenant_data.get("move_in_date"),
                rental_duration=tenant_data.get("rental_duration"),
                guarantor_status=tenant_data.get("guarantor_status"),
                viewing_interest=tenant_data.get("viewing_interest"),
                created_at=tenant_data.get("created_at"),
                last_updated=tenant_data.get("last_updated")
            )
            prospects.append(tenant)
        
        return TenantsListResponse(tenants=prospects, total_count=len(prospects))
        
    except Exception as e:
        logger.error(f"Error fetching prospects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tenants/qualified", response_model=TenantsListResponse)
async def get_qualified_prospects_endpoint():
    """Get all qualified prospects"""
    try:
        qualified_data = get_qualified_prospects()
        
        qualified = []
        for tenant_data in qualified_data:
            tenant = TenantProfileResponse(
                session_id=tenant_data.get("session_id", ""),
                status=tenant_data.get("status", "qualified"),
                age=tenant_data.get("age"),
                sex=tenant_data.get("sex"),
                occupation=tenant_data.get("occupation"),
                move_in_date=tenant_data.get("move_in_date"),
                rental_duration=tenant_data.get("rental_duration"),
                guarantor_status=tenant_data.get("guarantor_status"),
                viewing_interest=tenant_data.get("viewing_interest"),
                created_at=tenant_data.get("created_at"),
                last_updated=tenant_data.get("last_updated")
            )
            qualified.append(tenant)
        
        return TenantsListResponse(tenants=qualified, total_count=len(qualified))
        
    except Exception as e:
        logger.error(f"Error fetching qualified prospects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tenants/active", response_model=TenantsListResponse)
async def get_active_tenants_endpoint():
    """Get all active tenants"""
    try:
        active_data = get_active_tenants()
        
        active = []
        for tenant_data in active_data:
            tenant = TenantProfileResponse(
                session_id=tenant_data.get("session_id", ""),
                status=tenant_data.get("status", "active_tenant"),
                age=tenant_data.get("age"),
                sex=tenant_data.get("sex"),
                occupation=tenant_data.get("occupation"),
                lease_start_date=tenant_data.get("lease_start_date"),
                lease_end_date=tenant_data.get("lease_end_date"),
                created_at=tenant_data.get("created_at"),
                last_updated=tenant_data.get("last_updated")
            )
            active.append(tenant)
        
        return TenantsListResponse(tenants=active, total_count=len(active))
        
    except Exception as e:
        logger.error(f"Error fetching active tenants: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/tenants/{session_id}")
async def delete_tenant(session_id: str):
    """Delete a tenant profile by session ID"""
    try:
        success = delete_tenant_profile(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Tenant profile not found")
        
        return {"message": f"Tenant profile for session {session_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting tenant profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tenants/load-all")
async def load_all_tenants_to_memory():
    """Load all tenant profiles from persistent storage into memory"""
    try:
        from .conversation_memory import conversation_memory
        conversation_memory.load_all_from_persistent_storage()
        
        return {"message": "All tenant profiles loaded into memory successfully"}
        
    except Exception as e:
        logger.error(f"Error loading tenants to memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test/slack", response_model=SlackTestResponse)
async def test_slack_notification_endpoint():
    """Test Slack notification functionality"""
    try:
        success = test_slack_notification()
        if success:
            return SlackTestResponse(success=True, message="Slack notification test successful")
        else:
            return SlackTestResponse(success=False, message="Slack notification test failed")
    except Exception as e:
        logger.error(f"Error testing Slack notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test/handoff")
async def test_handoff_trigger(request: HandoffTestRequest):
    """Test handoff trigger functionality"""
    try:
        from .notifications import send_handoff_notification
        
        # Send test handoff notification
        success = send_handoff_notification(
            session_id=request.session_id,
            handoff_reason=request.handoff_reason,
            confidence_level="medium",
            escalation_priority=request.escalation_priority,
            conversation_summary="This is a test handoff notification to verify the system is working correctly.",
            tenant_age=30,
            tenant_occupation="Software Engineer",
            tenant_language="English",
            property_interest="2-bedroom apartment",
            move_in_date="January 2024",
            rental_duration="12 months",
            guarantor_status="yes",
            viewing_interest=True,
            availability="weekends"
        )
        
        if success:
            return {"message": f"Test handoff notification sent successfully for session {request.session_id}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send test handoff notification")
            
    except Exception as e:
        logger.error(f"Error testing handoff: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/handoff/triggers")
async def get_handoff_triggers():
    """Get information about handoff triggers"""
    try:
        triggers_info = {
            "automatic_triggers": [
                "Confidence Threshold: When agent confidence drops below 70%",
                "Complex Queries: Questions involving legal, financial, or policy matters",
                "Technical Issues: Property-specific questions agent cannot answer",
                "Emotional Situations: When tenant expresses frustration or urgency",
                "Multiple Failed Attempts: After 3-4 unsuccessful attempts to help"
            ],
            "manual_triggers": [
                "Explicit Requests: When tenant asks to speak with a human",
                "Keyword Detection: Phrases like 'speak to someone', 'human agent'",
                "Language Barriers: When communication becomes difficult"
            ],
            "escalation_priorities": [
                "low: Standard handoff with normal priority",
                "medium: Moderate urgency requiring attention",
                "high: High urgency requiring immediate attention",
                "urgent: Critical situation requiring immediate response"
            ]
        }
        
        return triggers_info
        
    except Exception as e:
        logger.error(f"Error getting handoff triggers info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)