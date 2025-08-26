# Facebook Messenger Setup Guide

## Current Issue
Your Facebook page has the correct permissions (`pages_messaging: granted`), but the messaging endpoint is failing. This usually means the page isn't properly connected to Messenger.

## Step-by-Step Fix

### Step 1: Enable Messenger for Your Page

1. **Go to your Facebook page**: https://www.facebook.com/your-page-name
2. **Click "Settings"** in the left sidebar
3. **Click "Messaging"** in the left menu
4. **Enable "Allow people to contact my Page privately"**
5. **Save changes**

### Step 2: Connect Page to Messenger App

1. **Go to Facebook Developers**: https://developers.facebook.com/
2. **Select your app**
3. **Go to "Messaging" → "Settings"**
4. **Under "Page Messaging"**, click "Add Page"
5. **Select your page** (Charles Sese)
6. **Authorize the app** to send messages

### Step 3: Verify Page is Connected

1. **In your app dashboard**, go to "Messaging" → "Settings"
2. **Check that your page appears** in the "Connected Pages" section
3. **Verify the page status** shows as "Connected"

### Step 4: Test the Connection

Run this test script to verify everything is working:

```bash
python test_facebook_token.py
```

### Step 5: Alternative Solutions

If the above doesn't work, try these alternatives:

#### Option A: Use Page Access Token from Graph API Explorer
1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your page from the dropdown
3. Click "Generate Access Token"
4. Copy the new token and update your environment variable

#### Option B: Check Page Publishing Status
1. Go to your Facebook page
2. Check if the page is published (not unpublished)
3. Make sure the page is not in development mode

#### Option C: Verify App Review Status
1. In your Facebook app dashboard
2. Go to "App Review" → "Permissions and Features"
3. Make sure `pages_messaging` is approved
4. Check if your app is in development mode

## Common Issues and Solutions

### Issue: "Object with ID 'me' does not exist"
**Solution**: The page isn't properly connected to Messenger. Follow Step 1-3 above.

### Issue: "Missing permissions"
**Solution**: Request the `pages_messaging` permission in App Review.

### Issue: "Page not found"
**Solution**: Make sure you're using the correct page ID and the page is published.

### Issue: "App not approved"
**Solution**: Submit your app for review or use development mode for testing.

## Testing Your Setup

After completing the setup, test with:

```bash
# Test the token
python test_facebook_token.py

# Send a test message to your Facebook page
# The webhook should now work properly
```

## Environment Variables

Make sure these are set correctly:

```bash
# In Heroku
heroku config:set FACEBOOK_ACCESS_TOKEN="your-page-access-token"
heroku config:set FACEBOOK_APP_SECRET="your-app-secret"
heroku config:set FACEBOOK_VERIFY_TOKEN="your-verify-token"
```

## Next Steps

1. **Complete the Messenger setup** (Steps 1-3 above)
2. **Test the connection** with the test script
3. **Deploy the updated code** to Heroku
4. **Send a test message** to your Facebook page

The key issue is that your page needs to be properly connected to the Messenger platform, not just have the permissions.
