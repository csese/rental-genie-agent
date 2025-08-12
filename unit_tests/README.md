# Unit Tests Directory

This directory contains unit tests for the core functionality of the Rental Genie Agent project.

## Contents

### Core Functionality Tests
- **`test_agent.py`** - Agent functionality and message handling testing
- **`test_conversation_memory.py`** - Conversation memory and session management testing
- **`test_extraction.py`** - Information extraction and parsing testing
- **`test_interactive.py`** - Interactive chat functionality testing
- **`test_prompts.py`** - Prompt management and versioning testing
- **`test_tenant_storage.py`** - Tenant storage and status management testing
- **`test_airtable.py`** - Airtable integration and data persistence testing

### Testing Utilities
- **`test_curl.sh`** - cURL-based testing utilities for API endpoints
- **`TESTING.md`** - General testing documentation and guidelines

## Usage

### Running Individual Tests

```bash
# Test agent functionality
python unit_tests/test_agent.py

# Test conversation memory
python unit_tests/test_conversation_memory.py

# Test information extraction
python unit_tests/test_extraction.py

# Test interactive chat
python unit_tests/test_interactive.py

# Test prompt management
python unit_tests/test_prompts.py

# Test tenant storage
python unit_tests/test_tenant_storage.py

# Test Airtable integration
python unit_tests/test_airtable.py
```

### Running All Unit Tests

```bash
# From the project root
python -m pytest unit_tests/

# Or run the comprehensive test suite
python tests/run_all_tests.py
```

### Running cURL Tests

```bash
# Test API endpoints (when server is running)
bash unit_tests/test_curl.sh
```

## Test Categories

### Agent Tests (`test_agent.py`)
- Message processing and response generation
- Handoff detection and triggers
- Conversation flow management
- Error handling and edge cases

### Memory Tests (`test_conversation_memory.py`)
- Session creation and management
- Conversation history tracking
- Tenant profile data storage
- Memory persistence and retrieval

### Extraction Tests (`test_extraction.py`)
- Information extraction from messages
- Data parsing and validation
- Field mapping and transformation
- Extraction accuracy testing

### Interactive Tests (`test_interactive.py`)
- End-to-end conversation flows
- User interaction simulation
- Response quality assessment
- Integration testing

### Prompt Tests (`test_prompts.py`)
- Prompt version management
- Prompt switching functionality
- Prompt content validation
- Prompt effectiveness testing

### Storage Tests (`test_tenant_storage.py`)
- Tenant data persistence
- Status management and transitions
- Data validation and integrity
- Storage performance testing

### Integration Tests (`test_airtable.py`)
- Airtable API connectivity
- Data synchronization
- Error handling and retries
- Performance and rate limiting

## Prerequisites

Most unit tests require:
- Python dependencies installed (`pip install -r requirements.txt`)
- Proper environment variables set (see main README.md)
- Airtable credentials (for integration tests)

## Test Organization

Unit tests are organized to:
- **Test individual components** in isolation
- **Verify core functionality** without external dependencies
- **Ensure data integrity** and proper error handling
- **Validate business logic** and workflow correctness

## Integration with Main Application

These unit tests complement the integration tests in the `tests/` directory:
- **Unit tests** focus on individual components and functions
- **Integration tests** focus on external service interactions
- **Both** are essential for comprehensive testing coverage

## Future Additions

As the project grows, additional unit test categories may be added:
- Performance testing
- Security testing
- Data validation testing
- Configuration testing
