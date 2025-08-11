from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from typing import Optional, Dict, Any
import logging
from .agent import handle_message
from .utils import get_all_property_info

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Rental Genie Agent", description="An intelligent agent for rental property inquiries")

# Pydantic models for request/response
class MessageRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class MessageResponse(BaseModel):
    response: str
    status: str
    session_id: Optional[str] = None
    confidence: Optional[float] = None

class HealthResponse(BaseModel):
    status: str
    message: str

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
        return None

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
        
        # Handle the message through the agent
        response = handle_message(request.message, property_data)
        
        # Create response
        return MessageResponse(
            response=response,
            status="success",
            session_id=request.session_id,
            confidence=0.9  # You can implement confidence scoring
        )
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.post("/webhook/facebook")
async def facebook_webhook(request: Request):
    """Facebook webhook endpoint (existing functionality)"""
    try:
        data = await request.json()
        
        # Extract message from Facebook webhook format
        if 'entry' in data and len(data['entry']) > 0:
            entry = data['entry'][0]
            if 'messaging' in entry and len(entry['messaging']) > 0:
                messaging = entry['messaging'][0]
                if 'message' in messaging and 'text' in messaging['message']:
                    user_msg = messaging['message']['text']
                    user_id = messaging['sender']['id']
                    
                    # Load property data
                    property_data = load_property_data()
                    if not property_data:
                        return JSONResponse(status_code=500, content={"error": "Property data not available"})
                    
                    # Handle the message
                    response = handle_message(user_msg, property_data)
                    
                    # TODO: Send response back via Facebook API
                    # You would implement Facebook API call here
                    
                    return {"status": "ok", "response": response}
        
        return {"status": "ok", "message": "No valid message found"}
        
    except Exception as e:
        logger.error(f"Facebook webhook error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)