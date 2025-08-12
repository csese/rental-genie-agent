# Rental Genie Agent

An intelligent agent for rental property inquiries that can collect and manage tenant information throughout the entire rental lifecycle.

## Features

- **Intelligent Conversation**: AI-powered agent that can understand and respond to rental inquiries
- **Tenant Information Collection**: Automatically extracts and stores tenant profiles
- **Status-Based Workflow**: Tracks tenants from prospect to active tenant with status management
- **Persistent Storage**: Tenant data is stored in Airtable for persistence and scalability
- **Multi-language Support**: Handles both English and French conversations
- **Session Management**: Maintains conversation context across multiple interactions
- **Property Integration**: Connects with property listings from Airtable
- **Smart Handoff System**: Automatically escalates complex queries to human property owners
- **Slack Notifications**: Real-time notifications to property owners via Slack

## Setup

### Environment Variables

Create a `.env` file with the following variables:

```bash
AIRTABLE_PERSONAL_ACCESS_TOKEN=your_airtable_token
BASE_ID=your_base_id
PROPERTY_TABLE_NAME=your_property_table_name
TENANT_TABLE_NAME=Tenants  # Optional, defaults to "Tenants"
SLACK_WEBHOOK_RENTAL_GENIE_URL=your_slack_webhook_url  # Optional, for notifications
```

### Slack Setup

To enable notifications:

1. **Create a Slack App**: Go to https://api.slack.com/apps
2. **Enable Incoming Webhooks**: In your app settings, enable incoming webhooks
3. **Create Webhook**: Click "Add New Webhook to Workspace" and select your desired channel
4. **Copy Webhook URL**: The webhook URL will look like `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX`
5. **Set Environment Variable**: Add the webhook URL to your `.env` file as `SLACK_WEBHOOK_RENTAL_GENIE_URL`

**Note**: The webhook URL is tied to a specific channel. All notifications will be sent to that channel. If you need notifications in different channels, you'll need to create separate webhooks for each channel.

### Airtable Setup

#### Property Table
Your property table should contain fields like:
- Name
- Address
- Rent
- Available (date)
- Status

#### Tenant Table (Updated)
Create a table called "Tenants" with the following fields:

| Field Name | Type | Description |
|------------|------|-------------|
| Session ID | Single line text | Unique session identifier |
| Status | Single select | Tenant status (see status values below) |
| Age | Number | Tenant's age |
| Sex | Single select | Male/Female |
| Occupation | Single line text | Tenant's occupation |
| Move In Date | Date | Preferred move-in date |
| Rental Duration | Single line text | How long they want to rent |
| Guarantor Status | Single select | Yes/No/Need/Visale |
| Guarantor Details | Single line text | Details about guarantor |
| Viewing Interest | Checkbox | Whether they want a viewing |
| Availability | Single line text | When they're available |
| Language Preference | Single select | English/French |
| Property Interest | Single line text | Specific property they're interested in |
| Application Date | Date | When application was submitted |
| Lease Start Date | Date | When lease begins |
| Lease End Date | Date | When lease ends |
| Notes | Long text | Additional notes |
| Created At | Date | When profile was created |
| Last Updated | Date | When profile was last updated |
| Conversation Turns | Number | Number of conversation turns |

### Tenant Status Values

The system uses the following status values to track tenant progression:

- **prospect** - Initial inquiry, incomplete profile
- **qualified** - Complete profile, ready for viewing
- **viewing_scheduled** - Viewing arranged
- **application_submitted** - Rental application submitted
- **approved** - Application approved
- **active_tenant** - Currently renting
- **former_tenant** - Past tenant
- **rejected** - Application rejected
- **withdrawn** - Prospect withdrew interest

### Handoff Triggers

The system automatically detects when to handoff conversations to human property owners:

#### Automatic Triggers
- **Confidence Threshold**: When agent confidence drops below 70%
- **Complex Queries**: Questions involving legal, financial, or policy matters
- **Technical Issues**: Property-specific questions the agent can't answer
- **Emotional Situations**: When tenant expresses frustration or urgency
- **Multiple Failed Attempts**: After 3-4 unsuccessful attempts to help

#### Manual Triggers
- **Explicit Requests**: When tenant asks to speak with a human
- **Keyword Detection**: Phrases like "speak to someone", "human agent", "real person"
- **Language Barriers**: When communication becomes difficult

#### Escalation Priorities
- **low**: Standard handoff with normal priority
- **medium**: Moderate urgency requiring attention
- **high**: High urgency requiring immediate attention
- **urgent**: Critical situation requiring immediate response

### TenantStatus Enum

The system uses a Python `Enum` class for type-safe status management:

```python
from app.conversation_memory import TenantStatus

# Access enum values
TenantStatus.PROSPECT.value  # "prospect"
TenantStatus.QUALIFIED.value  # "qualified"
TenantStatus.ACTIVE_TENANT.value  # "active_tenant"

# Validate status
TenantStatus.is_valid("prospect")  # True
TenantStatus.is_valid("invalid")   # False

# Get display names
TenantStatus.get_display_name("prospect")  # "Prospect"
TenantStatus.get_display_name("active_tenant")  # "Active Tenant"

# Get descriptions
TenantStatus.get_description("prospect")  # "Initial inquiry, incomplete profile"

# Get all values
TenantStatus.get_all_values()  # ["prospect", "qualified", ...]
```

## API Endpoints

### Chat
- `POST /chat` - Main chat endpoint for tenant interactions

### Tenant Management
- `GET /tenants` - Get all tenant profiles (optionally filtered by status)
- `GET /tenants/{session_id}` - Get specific tenant profile
- `PUT /tenants/{session_id}/status` - Update tenant status
- `DELETE /tenants/{session_id}` - Delete tenant profile
- `POST /tenants/load-all` - Load all tenants into memory

### Tenant Status Endpoints
- `GET /tenants/prospects` - Get all prospect tenants
- `GET /tenants/qualified` - Get all qualified prospects
- `GET /tenants/active` - Get all active tenants
- `GET /tenants/stats` - Get tenant statistics by status
- `GET /tenants/status-info` - Get information about all available statuses

### Handoff Management
- `GET /handoff/triggers` - Get information about handoff triggers
- `POST /test/slack` - Test Slack notification functionality
- `POST /test/handoff` - Test handoff trigger functionality

### Conversation Management
- `GET /conversation/{session_id}` - Get conversation info
- `GET /conversation` - Get all conversations
- `DELETE /conversation/{session_id}` - Clear conversation

### Properties
- `GET /properties` - Get available properties

### System
- `GET /health` - Health check
- `GET /prompts` - Get prompt information
- `POST /prompts/switch` - Switch prompt version

## Tenant Information Storage

The system stores tenant information in multiple layers:

1. **In-Memory**: Active conversations and recent data for fast access
2. **Persistent Storage**: Airtable database for long-term storage and backup
3. **Status-Based Workflow**: Tracks tenant progression through the rental process

### Data Flow
1. User sends message → Agent processes and extracts information
2. Information is stored in memory for immediate use
3. Data is automatically synced to Airtable for persistence
4. Status is automatically updated based on profile completion
5. On application restart, data can be loaded back from Airtable

### Handoff Process
1. Agent detects handoff trigger → Evaluates conversation context
2. Agent sends notification to Slack → Property owner receives alert
3. Agent provides final response to tenant → No mention of handoff
4. Session marked as handed off → Agent stops intervening
5. Property owner can view full context → Complete conversation history

### Status Transitions

The system automatically manages status transitions:

- **prospect** → **qualified**: When all required information is collected
- **qualified** → **viewing_scheduled**: When viewing is arranged
- **viewing_scheduled** → **application_submitted**: When application is submitted
- **application_submitted** → **approved**: When application is approved
- **approved** → **active_tenant**: When lease begins
- **active_tenant** → **former_tenant**: When lease ends

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python -m app.main
```

The application will be available at `http://localhost:8000`

## Testing

```bash
# Test the chat functionality
python test_interactive.py

# Test tenant information extraction
python test_extraction.py

# Test conversation memory
python test_conversation_memory.py

# Test tenant storage and status management
python test_tenant_storage.py

# Test Slack notifications
curl -X POST http://localhost:8000/test/slack

# Test handoff functionality
curl -X POST http://localhost:8000/test/handoff \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test_123", "handoff_reason": "Test handoff", "escalation_priority": "medium"}'
```

## Architecture

- **Agent** (`app/agent.py`): Core AI logic and message handling with handoff detection
- **Conversation Memory** (`app/conversation_memory.py`): Session and tenant data management with status tracking
- **Utils** (`app/utils.py`): Airtable integration and data utilities
- **Main** (`app/main.py`): FastAPI application and endpoints
- **Prompts** (`app/prompts.py`): AI prompt management with handoff instructions
- **Notifications** (`app/notifications.py`): Slack notification system for handoffs

## Data Privacy

- Tenant data is stored securely in Airtable
- Sessions can be cleared for privacy compliance
- No sensitive data is logged in application logs
- Data retention policies can be implemented through Airtable
- Status tracking provides audit trail of tenant interactions
- Handoff notifications include only necessary information for property owners
