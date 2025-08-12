# Tests Directory

This directory contains test scripts and utilities for the Rental Genie Agent project.

## Contents

### Slack Notifications Testing
- **`test_slack_quick.py`** - Quick test for basic Slack notification functionality
- **`test_slack_notifications.py`** - Comprehensive test suite for all Slack notification scenarios
- **`SLACK_TESTING.md`** - Complete documentation for Slack notification testing
- **`run_all_tests.py`** - Script to run all tests in organized categories

### Other Test Files
The following test files are located in the `unit_tests/` directory and are unit tests for core functionality:
- `unit_tests/test_agent.py` - Agent functionality testing
- `unit_tests/test_airtable.py` - Airtable integration testing
- `unit_tests/test_conversation_memory.py` - Conversation memory testing
- `unit_tests/test_extraction.py` - Information extraction testing
- `unit_tests/test_interactive.py` - Interactive testing
- `unit_tests/test_prompts.py` - Prompt testing
- `unit_tests/test_tenant_storage.py` - Tenant storage testing
- `unit_tests/test_curl.sh` - cURL-based testing utilities

## Usage

### Running Tests

```bash
# Run all tests (organized by category)
python integration_tests/run_all_tests.py

# Run Slack tests only
python integration_tests/test_slack_quick.py          # Quick test
python integration_tests/test_slack_notifications.py  # Comprehensive test
```

### Prerequisites

For Slack notification tests, you need to set the `SLACK_WEBHOOK_RENTAL_GENIE_URL` environment variable:

```bash
export SLACK_WEBHOOK_RENTAL_GENIE_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

See `SLACK_TESTING.md` for detailed setup instructions.

## Organization

This tests directory is organized to separate:
- **Integration tests** (like Slack notifications) that require external services
- **Unit tests** (like agent, memory, extraction) that test internal functionality

## Future Additions

As the project grows, additional test categories may be added:
- API endpoint testing
- Database integration testing
- Performance testing
- End-to-end testing
