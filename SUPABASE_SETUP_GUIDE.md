# Supabase Setup Guide for Rental Genie

## Overview

This guide will help you migrate from Airtable to Supabase, which will solve your current issues and provide better performance, real-time capabilities, and scalability.

## Why Supabase is Better

✅ **No field name issues** - Flexible JSON structure  
✅ **Real-time capabilities** - Perfect for chat applications  
✅ **Better performance** - No rate limits like Airtable  
✅ **Cost-effective** - Generous free tier  
✅ **PostgreSQL** - Full SQL database with advanced features  

## Step 1: Create Supabase Project

### 1.1 Sign Up
1. Go to [supabase.com](https://supabase.com)
2. Sign up with your GitHub account
3. Click "New Project"

### 1.2 Create Project
- **Organization**: Select your organization
- **Name**: `rental-genie-db`
- **Database Password**: Generate a strong password (save this!)
- **Region**: Choose closest to your users (e.g., West Europe for France)
- Click "Create new project"

### 1.3 Get Credentials
Once created, go to **Settings → API** and copy:
- **Project URL** (looks like: `https://your-project.supabase.co`)
- **Anon Key** (public key)
- **Service Role Key** (private key - keep secret!)

## Step 2: Set Up Database Schema

### 2.1 Run SQL Schema
1. In your Supabase dashboard, go to **SQL Editor**
2. Copy the contents of `supabase_schema.sql`
3. Paste and run the SQL
4. This creates all tables, indexes, and sample data

### 2.2 Verify Setup
After running the SQL, you should see:
- ✅ 5 tables created (properties, tenants, chat_sessions, conversation_messages, property_applications)
- ✅ Sample properties inserted
- ✅ Indexes created for performance
- ✅ Views and functions created

## Step 3: Set Environment Variables

### 3.1 Local Development
Add to your `.env` file:
```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# Keep Airtable for now (we'll migrate later)
AIRTABLE_PERSONAL_ACCESS_TOKEN=your-airtable-token
BASE_ID=your-base-id
TENANT_TABLE_NAME=your-table-name
```

### 3.2 Heroku Deployment
Set the environment variables in Heroku:
```bash
heroku config:set SUPABASE_URL="https://your-project.supabase.co"
heroku config:set SUPABASE_ANON_KEY="your-anon-key"
heroku config:set SUPABASE_SERVICE_KEY="your-service-key"
```

## Step 4: Test Supabase Connection

### 4.1 Run Migration Tool
```bash
# Activate virtual environment
source venv/bin/activate

# Run the migration tool
python migrate_to_supabase.py
```

This will:
- ✅ Test Supabase connection
- ✅ Create sample data
- ✅ Offer to migrate from Airtable

### 4.2 Verify in Supabase Dashboard
1. Go to **Table Editor** in Supabase
2. Check that tables are created
3. Verify sample data exists

## Step 5: Update Your Code

### 5.1 Install Dependencies
The Supabase client uses `httpx` which is already in your requirements.

### 5.2 Update Environment Variables
Update your `app.json` to include Supabase variables:
```json
{
  "env": {
    "SUPABASE_URL": {
      "description": "Supabase project URL",
      "required": true
    },
    "SUPABASE_ANON_KEY": {
      "description": "Supabase anonymous key",
      "required": true
    },
    "SUPABASE_SERVICE_KEY": {
      "description": "Supabase service role key",
      "required": true
    }
  }
}
```

## Step 6: Migrate Data (Optional)

### 6.1 Run Migration
If you want to migrate your existing Airtable data:
```bash
python migrate_to_supabase.py
```
When prompted, type `y` to migrate.

### 6.2 Verify Migration
Check in Supabase dashboard that your data was migrated correctly.

## Step 7: Update Application Code

### 7.1 Replace Airtable Functions
The `supabase_client.py` provides drop-in replacements for your Airtable functions:

| Airtable Function | Supabase Function |
|------------------|-------------------|
| `get_tenant_profile()` | `get_tenant()` |
| `store_tenant_profile()` | `create_tenant()` |
| `update_tenant_status()` | `update_tenant()` |
| `get_all_property_info()` | `get_all_properties()` |

### 7.2 Update Your Main Application
Replace Airtable imports with Supabase:
```python
# Old (Airtable)
from .utils import get_tenant_profile, store_tenant_profile

# New (Supabase)
from .supabase_client import get_supabase_client
```

## Step 8: Deploy and Test

### 8.1 Deploy to Heroku
```bash
git add .
git commit -m "Add Supabase integration"
git push heroku main
```

### 8.2 Test Facebook Integration
1. Send a message to your Facebook page
2. Check Heroku logs: `heroku logs --tail`
3. Verify data is stored in Supabase dashboard

## Troubleshooting

### Issue: "Missing Supabase environment variables"
**Solution**: Make sure you've set all three Supabase environment variables

### Issue: "Supabase API error: 401"
**Solution**: Check that your API keys are correct and not expired

### Issue: "Table does not exist"
**Solution**: Run the SQL schema in Supabase SQL Editor

### Issue: "Permission denied"
**Solution**: Check Row Level Security (RLS) policies in Supabase

## Benefits After Migration

### Performance Improvements
- ⚡ **Faster queries** - No more Airtable rate limits
- 🔄 **Real-time updates** - Perfect for chat applications
- 📊 **Better analytics** - Full SQL capabilities

### Developer Experience
- 🛠️ **Flexible schema** - No more field name issues
- 🔍 **Better debugging** - Full SQL logs
- 📈 **Scalability** - Handles high traffic better

### Cost Savings
- 💰 **Free tier** - 500MB database, 50MB file storage
- 📊 **No per-record costs** - Unlike Airtable
- 🚀 **Better value** - More features for less money

## Next Steps

1. **Test thoroughly** - Make sure everything works
2. **Monitor performance** - Check Supabase dashboard metrics
3. **Optimize queries** - Use the created indexes
4. **Set up backups** - Supabase provides automatic backups
5. **Consider real-time features** - Enable real-time subscriptions for live updates

## Support

If you encounter issues:
1. Check Supabase dashboard logs
2. Verify environment variables
3. Test with the migration tool
4. Check Heroku logs for errors

The migration will solve your current Facebook integration issues and provide a much more robust foundation for your rental management system!
