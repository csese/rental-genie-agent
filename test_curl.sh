#!/bin/bash

# Rental Genie Agent - Quick API Tests with curl
# Make sure the server is running on localhost:8000

echo "🏠 Rental Genie Agent - Quick API Tests"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# Test 1: Health Check
echo -e "\n${BLUE}1. Testing Health Endpoint${NC}"
response=$(curl -s -w "%{http_code}" http://localhost:8000/health)
http_code="${response: -3}"
body="${response%???}"
print_status $([ "$http_code" = "200" ] && echo 0 || echo 1) "Health check returned $http_code"
echo "Response: $body"

# Test 2: Root Endpoint
echo -e "\n${BLUE}2. Testing Root Endpoint${NC}"
response=$(curl -s -w "%{http_code}" http://localhost:8000/)
http_code="${response: -3}"
body="${response%???}"
print_status $([ "$http_code" = "200" ] && echo 0 || echo 1) "Root endpoint returned $http_code"
echo "Response: $body"

# Test 3: Properties Endpoint
echo -e "\n${BLUE}3. Testing Properties Endpoint${NC}"
response=$(curl -s -w "%{http_code}" http://localhost:8000/properties)
http_code="${response: -3}"
body="${response%???}"
print_status $([ "$http_code" = "200" ] && echo 0 || echo 1) "Properties endpoint returned $http_code"
echo "Response: $body"

# Test 4: Get Prompt Information
echo -e "\n${BLUE}4. Testing Prompt Information Endpoint${NC}"
response=$(curl -s -w "%{http_code}" http://localhost:8000/prompts)
http_code="${response: -3}"
body="${response%???}"
print_status $([ "$http_code" = "200" ] && echo 0 || echo 1) "Prompts endpoint returned $http_code"
echo "Response: $body"

# Test 5: Basic Chat Message (v2 prompt)
echo -e "\n${BLUE}5. Testing Basic Chat Message (v2 prompt)${NC}"
response=$(curl -s -w "%{http_code}" -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{
        "message": "Hi, I am interested in renting a property",
        "user_id": "test_user_123",
        "session_id": "test_session_456",
        "prompt_version": "v2"
    }')
http_code="${response: -3}"
body="${response%???}"
print_status $([ "$http_code" = "200" ] && echo 0 || echo 1) "Chat endpoint (v2) returned $http_code"
echo "Response: $body"

# Test 6: Chat Message with v1 prompt
echo -e "\n${BLUE}6. Testing Chat Message (v1 prompt)${NC}"
response=$(curl -s -w "%{http_code}" -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{
        "message": "Hi, I am interested in renting a property",
        "user_id": "test_user_123",
        "session_id": "test_session_456",
        "prompt_version": "v1"
    }')
http_code="${response: -3}"
body="${response%???}"
print_status $([ "$http_code" = "200" ] && echo 0 || echo 1) "Chat endpoint (v1) returned $http_code"
echo "Response: $body"

# Test 7: Switch Prompt Version
echo -e "\n${BLUE}7. Testing Prompt Version Switch${NC}"
response=$(curl -s -w "%{http_code}" -X POST http://localhost:8000/prompts/switch \
    -H "Content-Type: application/json" \
    -d '{"version": "v1"}')
http_code="${response: -3}"
body="${response%???}"
print_status $([ "$http_code" = "200" ] && echo 0 || echo 1) "Prompt switch returned $http_code"
echo "Response: $body"

# Test 8: Chat after prompt switch
echo -e "\n${BLUE}8. Testing Chat After Prompt Switch${NC}"
response=$(curl -s -w "%{http_code}" -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{
        "message": "Hi, I am interested in renting a property",
        "user_id": "test_user_123",
        "session_id": "test_session_456"
    }')
http_code="${response: -3}"
body="${response%???}"
print_status $([ "$http_code" = "200" ] && echo 0 || echo 1) "Chat after switch returned $http_code"
echo "Response: $body"

# Test 9: Switch back to v2
echo -e "\n${BLUE}9. Switching Back to v2 Prompt${NC}"
response=$(curl -s -w "%{http_code}" -X POST http://localhost:8000/prompts/switch \
    -H "Content-Type: application/json" \
    -d '{"version": "v2"}')
http_code="${response: -3}"
body="${response%???}"
print_status $([ "$http_code" = "200" ] && echo 0 || echo 1) "Switch back to v2 returned $http_code"
echo "Response: $body"

# Test 10: Tenant Information Message
echo -e "\n${BLUE}10. Testing Tenant Information Message${NC}"
response=$(curl -s -w "%{http_code}" -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{
        "message": "I am 25 years old and work as a software engineer",
        "user_id": "test_user_123",
        "session_id": "test_session_456"
    }')
http_code="${response: -3}"
body="${response%???}"
print_status $([ "$http_code" = "200" ] && echo 0 || echo 1) "Tenant info chat returned $http_code"
echo "Response: $body"

# Test 11: Move-in Date Question
echo -e "\n${BLUE}11. Testing Move-in Date Question${NC}"
response=$(curl -s -w "%{http_code}" -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{
        "message": "When can I move in?",
        "user_id": "test_user_123",
        "session_id": "test_session_456"
    }')
http_code="${response: -3}"
body="${response%???}"
print_status $([ "$http_code" = "200" ] && echo 0 || echo 1) "Move-in date question returned $http_code"
echo "Response: $body"

# Test 12: Invalid JSON (Error Handling)
echo -e "\n${BLUE}12. Testing Error Handling - Invalid JSON${NC}"
response=$(curl -s -w "%{http_code}" -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "test"')
http_code="${response: -3}"
body="${response%???}"
print_status $([ "$http_code" = "422" ] && echo 0 || echo 1) "Invalid JSON returned $http_code (expected 422)"
echo "Response: $body"

# Test 13: Missing Message (Error Handling)
echo -e "\n${BLUE}13. Testing Error Handling - Missing Message${NC}"
response=$(curl -s -w "%{http_code}" -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"user_id": "test_user_123"}')
http_code="${response: -3}"
body="${response%???}"
print_status $([ "$http_code" = "422" ] && echo 0 || echo 1) "Missing message returned $http_code (expected 422)"
echo "Response: $body"

# Test 14: Generic Webhook
echo -e "\n${BLUE}14. Testing Generic Webhook${NC}"
response=$(curl -s -w "%{http_code}" -X POST http://localhost:8000/webhook/generic \
    -H "Content-Type: application/json" \
    -d '{
        "message": "Hello from webhook",
        "user_id": "webhook_user",
        "session_id": "webhook_session"
    }')
http_code="${response: -3}"
body="${response%???}"
print_status $([ "$http_code" = "200" ] && echo 0 || echo 1) "Generic webhook returned $http_code"
echo "Response: $body"

echo -e "\n${YELLOW}🎉 API Testing Complete!${NC}"
echo -e "${BLUE}To start the server, run: python -m app.main${NC}"
echo -e "${BLUE}For interactive testing, run: python test_interactive.py${NC}"
echo -e "${BLUE}For prompt testing, run: python test_prompts.py${NC}"
