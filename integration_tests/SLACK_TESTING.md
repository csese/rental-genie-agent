# Slack Notifications Testing Guide

This guide explains how to test the Slack notifications functionality in the Rental Genie Agent.

## Prerequisites

1. **Slack Webhook URL**: You need a Slack webhook URL to send notifications to your Slack channel.
2. **Environment Variable**: Set the `SLACK_WEBHOOK_RENTAL_GENIE_URL` environment variable with your webhook URL.

## Setup

### 1. Get a Slack Webhook URL

1. Go to your Slack workspace
2. Create a new app or use an existing one
3. Enable "Incoming Webhooks"
4. Create a webhook for your desired channel
5. Copy the webhook URL

### 2. Set Environment Variable

```bash
# Option 1: Set for current session
export SLACK_WEBHOOK_RENTAL_GENIE_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# Option 2: Add to your shell profile (.bashrc, .zshrc, etc.)
echo 'export SLACK_WEBHOOK_RENTAL_GENIE_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"' >> ~/.zshrc
source ~/.zshrc

# Option 3: Create a .env file in the project root
echo 'SLACK_WEBHOOK_RENTAL_GENIE_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL' > .env
```

## Test Scripts

### Quick Test (`test_slack_quick.py`)

For a fast test of basic functionality:

```bash
python test_slack_quick.py
```

This script will:
- Check if the webhook URL is configured
- Test basic integration
- Send a handoff notification
- Send a session notification
- Provide a quick summary

### Comprehensive Test (`test_slack_notifications.py`)

For thorough testing of all notification types and scenarios:

```bash
python test_slack_notifications.py
```

This script includes:
- Basic integration testing
- Multiple handoff notification scenarios (low, high, urgent priority)
- Session notifications with various data
- Function wrapper testing
- Error handling scenarios
- Detailed test summary

## Test Scenarios

### Handoff Notifications

The comprehensive test includes three types of handoff notifications:

1. **Low Priority**: Regular handoff for standard assistance
2. **High Priority**: Urgent handoff for immediate needs
3. **Urgent Priority**: Critical handoff for complex situations

Each test includes:
- Tenant information (name, age, occupation)
- Handoff reason and priority
- Conversation summary
- Property interests
- Move-in details
- Conversation history

### Session Notifications

Tests new session notifications with:
- Basic tenant information
- Initial message
- Extracted information from the conversation
- Various data scenarios

## Expected Output

### Successful Test
```
🧪 Quick Slack Notification Test
========================================
✅ Webhook URL found: https://hooks.slack.com/ser...

1️⃣ Testing basic integration...
   ✅ Passed

2️⃣ Testing handoff notification...
   ✅ Passed

3️⃣ Testing session notification...
   ✅ Passed

========================================
📊 Results: 3/3 tests passed
🎉 All tests passed! Slack integration is working correctly.
```

### Failed Test (No Webhook)
```
🧪 Quick Slack Notification Test
========================================
❌ SLACK_WEBHOOK_RENTAL_GENIE_URL not found!
💡 Set the environment variable to enable Slack notifications
```

## Troubleshooting

### Common Issues

1. **"Webhook URL not found"**
   - Make sure you've set the `SLACK_WEBHOOK_RENTAL_GENIE_URL` environment variable
   - Check that the variable name is exactly correct (case-sensitive)

2. **"Failed to send Slack notification"**
   - Verify your webhook URL is correct
   - Check that your Slack app has the necessary permissions
   - Ensure the webhook is active and not disabled

3. **Network errors**
   - Check your internet connection
   - Verify that your firewall isn't blocking the requests
   - Try testing the webhook URL directly in a browser

### Testing Webhook URL

You can test your webhook URL directly using curl:

```bash
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test message from Rental Genie"}' \
  https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### Debug Mode

To see more detailed error information, you can modify the test scripts to include debug output or check the console output for specific error messages.

## Integration with Main Application

The notification system is integrated into the main Rental Genie Agent and will automatically send notifications when:

- A new tenant session starts
- A handoff is required (based on agent logic)
- Important events occur during conversations

The test scripts help verify that this integration will work correctly in production.

## Security Notes

- Never commit your webhook URL to version control
- Use environment variables or secure configuration management
- Regularly rotate your webhook URLs
- Monitor your Slack app permissions and usage
