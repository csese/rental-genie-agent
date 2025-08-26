# Facebook Integration Setup Guide

## Issues Identified

Based on your logs, there are two main issues:

### 1. Airtable Field Name Issue
**Error**: `"Unknown field names: session id"`

**Problem**: The code expects a field named `"Session ID"` but your Airtable table has a different field name.

**Solution**: 
- Run the debug script to check your actual field names
- Update your Airtable table or the code to match

### 2. Facebook Graph API Permission Issue
**Error**: `"Object with ID 'me' does not exist, cannot be loaded due to missing permissions"`

**Problem**: The Facebook access token doesn't have the correct permissions or is the wrong type.

**Solution**: Use a Page Access Token, not a User Access Token.

## Step-by-Step Fix

### Step 1: Check Your Airtable Configuration

Run the debug script to see your actual field names:

```bash
python debug_airtable.py
```

This will show you:
- Available field names in your Airtable table
- Whether environment variables are set correctly
- Potential Session ID field names

### Step 2: Fix Airtable Field Names

If the debug script shows that your field name is different from `"Session ID"`, you have two options:

**Option A: Update your Airtable table**
1. Go to your Airtable base
2. Find the field that should store session IDs
3. Rename it to exactly `"Session ID"` (with capital letters and space)

**Option B: Update the code**
The code has been updated to try multiple field name variations, so it should work with most common formats.

### Step 3: Set Up Facebook Environment Variables

You need to set these environment variables in Heroku:

```bash
# Set Facebook environment variables
heroku config:set FACEBOOK_ACCESS_TOKEN="your_page_access_token"
heroku config:set FACEBOOK_APP_SECRET="your_app_secret"
heroku config:set FACEBOOK_VERIFY_TOKEN="your_verify_token"
```

### Step 4: Get the Correct Facebook Access Token

**Important**: You need a **Page Access Token**, not a User Access Token.

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Select your app
3. Go to "Tools" → "Graph API Explorer"
4. Select your page from the dropdown (not your user account)
5. Click "Generate Access Token"
6. Make sure you have these permissions:
   - `pages_messaging`
   - `pages_messaging_subscriptions`
   - `pages_show_list`

### Step 5: Configure Facebook App Permissions

1. In your Facebook app dashboard, go to "App Review" → "Permissions and Features"
2. Request these permissions:
   - `pages_messaging`
   - `pages_messaging_subscriptions`
   - `pages_show_list`

### Step 6: Set Up Facebook Webhook

1. In your Facebook app dashboard, go to "Messaging" → "Settings"
2. Add your webhook URL: `https://your-heroku-app.herokuapp.com/webhook`
3. Set the verify token (same as `FACEBOOK_VERIFY_TOKEN`)
4. Subscribe to these events:
   - `messages`
   - `messaging_postbacks`

### Step 7: Test the Integration

1. Deploy your updated code to Heroku
2. Send a message to your Facebook page
3. Check the logs: `heroku logs --tail`

## Environment Variables Summary

Make sure these are set in Heroku:

```bash
# Airtable
AIRTABLE_PERSONAL_ACCESS_TOKEN=your_airtable_token
BASE_ID=your_base_id
TENANT_TABLE_NAME=your_table_name

# Facebook
FACEBOOK_ACCESS_TOKEN=your_page_access_token
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_VERIFY_TOKEN=your_verify_token

# Other
OPENAI_API_KEY=your_openai_key
SLACK_WEBHOOK_RENTAL_GENIE_URL=your_slack_webhook
```

## Common Issues and Solutions

### Issue: "Invalid field names"
**Solution**: Check your Airtable field names with the debug script

### Issue: "Object with ID 'me' does not exist"
**Solution**: Use a Page Access Token, not a User Access Token

### Issue: "Missing permissions"
**Solution**: Request the required permissions in Facebook App Review

### Issue: "Webhook verification failed"
**Solution**: Make sure `FACEBOOK_VERIFY_TOKEN` matches what you set in Facebook

## Testing

After setup, test with:

```bash
# Check configuration
python debug_airtable.py

# Test webhook locally (if needed)
curl -X POST https://your-heroku-app.herokuapp.com/webhook \
  -H "Content-Type: application/json" \
  -d '{"entry":[{"messaging":[{"sender":{"id":"123"},"message":{"text":"test"}}]}]}'
```

## Support

If you're still having issues:
1. Run the debug script and share the output
2. Check Heroku logs: `heroku logs --tail`
3. Verify Facebook app permissions
4. Make sure you're using a Page Access Token
