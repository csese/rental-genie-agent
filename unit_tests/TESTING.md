# Testing Guide for Rental Genie Agent

This guide covers all the different ways you can test your Rental Genie Agent to ensure it's working correctly.

## Prerequisites

Before testing, make sure you have:

1. **Environment Variables Set**: Create a `.env` file with your API keys:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   BASE_ID=your_airtable_base_id
   AIRTABLE_API_KEY=your_airtable_api_key
   PROPERTY_TABLE_NAME=your_property_table_name
   ```

2. **Dependencies Installed**: Install all required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Server Running**: Start the FastAPI server:
   ```bash
   python -m app.main
   ```

## Testing Methods

### 1. Quick API Tests (curl)

The fastest way to test basic functionality:

```bash
./test_curl.sh
```

This script tests:
- Health endpoints
- Chat functionality
- Error handling
- Webhook endpoints

### 2. Interactive Testing

For conversational testing with the agent:

```bash
python test_interactive.py
```

This provides:
- Interactive chat interface
- Predefined test scenarios
- Real-time conversation testing

### 3. Comprehensive Test Suite

For thorough testing including unit tests:

```bash
python test_agent.py
```

This includes:
- Unit tests for agent functions
- Integration tests for API endpoints
- Manual test scenarios
- Edge case testing

## Test Scenarios

### Basic Functionality Tests

1. **Health Check**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Simple Chat**
   ```bash
   curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Hi, I am interested in renting a property"}'
   ```

3. **Tenant Information Collection**
   ```bash
   curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "I am 25 years old and work as a software engineer"}'
   ```

### Conversation Flow Tests

Test these conversation sequences:

1. **Property Inquiry Flow**:
   - "Hi, I'm interested in renting a property"
   - "What properties do you have available?"
   - "What are the requirements?"
   - "How much is the rent?"

2. **Tenant Qualification Flow**:
   - "I'm 28 years old"
   - "I work as a data analyst"
   - "My annual income is $75,000"
   - "I want to move in on March 1st"
   - "I can stay for 12 months"

3. **Guarantor Information Flow**:
   - "Do you need a guarantor?"
   - "I have a guarantor"
   - "My guarantor is my father who works as an accountant"

### Edge Case Tests

1. **Empty Messages**:
   ```bash
   curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message": ""}'
   ```

2. **Very Long Messages**:
   ```bash
   curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "A" * 1000}'
   ```

3. **Special Characters**:
   ```bash
   curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello! 😊 How are you?"}'
   ```

## Webhook Testing

### Generic Webhook
```bash
curl -X POST http://localhost:8000/webhook/generic \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello from webhook",
    "user_id": "webhook_user",
    "session_id": "webhook_session"
  }'
```

### Facebook Webhook (Mock)
```bash
curl -X POST http://localhost:8000/webhook/facebook \
  -H "Content-Type: application/json" \
  -d '{
    "entry": [{
      "messaging": [{
        "sender": {"id": "123456"},
        "message": {"text": "Hello from Facebook"}
      }]
    }]
  }'
```

## Property Data Testing

Test property data loading:

```bash
curl http://localhost:8000/properties
```

This should return your Airtable property data if configured correctly.

## Error Handling Tests

1. **Invalid JSON**:
   ```bash
   curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "test"'
   ```

2. **Missing Required Fields**:
   ```bash
   curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"user_id": "test_user"}'
   ```

3. **Server Not Running**:
   ```bash
   curl http://localhost:8001/health
   ```

## Performance Testing

### Load Testing (Optional)
For basic load testing, you can use tools like `ab` (Apache Bench):

```bash
# Install ab if not available
# On macOS: brew install httpd
# On Ubuntu: sudo apt-get install apache2-utils

# Test with 100 requests, 10 concurrent
ab -n 100 -c 10 -T application/json -p test_payload.json http://localhost:8000/chat
```

Create `test_payload.json`:
```json
{"message": "Test message", "user_id": "load_test_user"}
```

## Debugging Tips

### 1. Check Server Logs
When running the server, watch for error messages:
```bash
python -m app.main
```

### 2. Test Environment Variables
```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('OPENAI_API_KEY:', 'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET')
print('BASE_ID:', 'SET' if os.getenv('BASE_ID') else 'NOT SET')
print('AIRTABLE_API_KEY:', 'SET' if os.getenv('AIRTABLE_API_KEY') else 'NOT SET')
"
```

### 3. Test Property Data Loading
```bash
python -c "
from app.utils import get_all_property_info
try:
    data = get_all_property_info()
    print(f'Property data loaded: {len(data)} records')
except Exception as e:
    print(f'Error loading property data: {e}')
"
```

## Expected Behaviors

### Agent Responses Should:
1. **Be Conversational**: Respond naturally to user messages
2. **Collect Information**: Ask for missing tenant information
3. **Provide Property Info**: Share relevant property details
4. **Handle Errors Gracefully**: Give helpful error messages
5. **Maintain Context**: Remember previous conversation details

### API Responses Should:
1. **Return 200**: For successful requests
2. **Return 422**: For invalid request data
3. **Return 500**: For server errors
4. **Include Required Fields**: `response`, `status`, `session_id`
5. **Handle Timeouts**: Respond within reasonable time

## Troubleshooting

### Common Issues:

1. **Server Won't Start**:
   - Check if port 8000 is available
   - Verify all dependencies are installed
   - Check environment variables

2. **Property Data Not Loading**:
   - Verify Airtable credentials
   - Check table name and base ID
   - Ensure internet connection

3. **Agent Not Responding**:
   - Check OpenAI API key
   - Verify API quota/credits
   - Check network connectivity

4. **Tests Failing**:
   - Ensure server is running
   - Check all environment variables
   - Verify test data format

## Next Steps

After testing:
1. Review any failed tests
2. Check server logs for errors
3. Verify agent responses are appropriate
4. Test with real property data
5. Consider adding more specific test cases

For more advanced testing, consider:
- Integration with CI/CD pipelines
- Automated testing frameworks (pytest)
- Performance monitoring
- User acceptance testing



