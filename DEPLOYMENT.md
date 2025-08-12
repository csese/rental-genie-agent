# 🚀 Deployment Guide - Rental Genie Backend

## 🎯 **Recommended: Railway Deployment**

### **Why Railway?**
- ✅ **Free tier**: $5 credit monthly (sufficient for development)
- ✅ **Easy setup**: Git-based deployment
- ✅ **Fast performance**: Quick startup times
- ✅ **Environment variables**: Secure configuration
- ✅ **Custom domains**: Free SSL certificates

---

## 📋 **Prerequisites**

1. **GitHub Account**: Your code should be in a GitHub repository
2. **Railway Account**: Sign up at [railway.app](https://railway.app)
3. **Environment Variables**: Prepare your configuration

---

## 🛠️ **Step-by-Step Deployment**

### **Step 1: Prepare Your Repository**

Ensure your repository has these files:
```
rentalGenie/
├── app/
│   ├── main.py
│   ├── agent.py
│   ├── conversation_memory.py
│   ├── notifications.py
│   ├── prompts.py
│   ├── utils.py
│   └── enums.py
├── requirements.txt
├── Procfile
├── runtime.txt
└── .env (local only - don't commit)
```

### **Step 2: Push to GitHub**

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit for deployment"

# Create GitHub repository and push
git remote add origin https://github.com/yourusername/rentalGenie.git
git push -u origin main
```

### **Step 3: Deploy on Railway**

1. **Visit Railway**: Go to [railway.app](https://railway.app)
2. **Sign up/Login**: Use GitHub account
3. **Create New Project**: Click "New Project"
4. **Deploy from GitHub**: Select "Deploy from GitHub repo"
5. **Select Repository**: Choose your `rentalGenie` repository
6. **Deploy**: Railway will automatically detect Python and deploy

### **Step 4: Configure Environment Variables**

In Railway dashboard, go to your project → Variables tab:

```bash
# Required Environment Variables
AIRTABLE_API_KEY=your_airtable_api_key
AIRTABLE_BASE_ID=apph3SwLeTZGolkwK
AIRTABLE_PROPERTIES_TABLE=tblO8k3E5rTXl4IAv
AIRTABLE_TENANTS_TABLE=tblO8k3E5rTXl4IAv
OPENAI_API_KEY=your_openai_api_key
SLACK_WEBHOOK_RENTAL_GENIE_URL=your_slack_webhook_url

# Optional
ENABLE_MOCK_DATA=false
LOG_LEVEL=INFO
```

### **Step 5: Get Your Deployment URL**

Railway will provide a URL like:
```
https://your-app-name.railway.app
```

---

## 🔧 **Alternative: Render Deployment**

If Railway doesn't work, try Render:

### **Step 1: Sign up on Render**
- Visit [render.com](https://render.com)
- Sign up with GitHub

### **Step 2: Create Web Service**
- Click "New Web Service"
- Connect your GitHub repository
- Select the repository

### **Step 3: Configure Service**
- **Name**: `rental-genie-backend`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### **Step 4: Add Environment Variables**
Same as Railway above.

---

## 🧪 **Testing Your Deployment**

### **Health Check**
```bash
curl https://your-app-name.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "Agent is ready to handle messages"
}
```

### **Test Properties Endpoint**
```bash
curl https://your-app-name.railway.app/properties
```

### **Test Tenants Endpoint**
```bash
curl https://your-app-name.railway.app/tenants
```

---

## 🔄 **Updating Your Deployment**

### **Automatic Updates**
Both Railway and Render automatically deploy when you push to your main branch:

```bash
git add .
git commit -m "Update backend"
git push origin main
```

### **Manual Redeploy**
- **Railway**: Go to project → Deployments → Redeploy
- **Render**: Go to service → Manual Deploy

---

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Build Fails**
   - Check `requirements.txt` has all dependencies
   - Verify Python version in `runtime.txt`

2. **Environment Variables Missing**
   - Ensure all required variables are set in Railway/Render
   - Check variable names match your code

3. **App Crashes on Startup**
   - Check logs in Railway/Render dashboard
   - Verify Airtable credentials are correct

4. **CORS Issues**
   - Add CORS middleware to your FastAPI app
   - Configure allowed origins

### **Adding CORS Support**

If you need CORS, add to `app/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 💰 **Costs**

### **Railway**
- **Free tier**: $5 credit/month
- **Small app**: ~$2-3/month
- **Upgrade**: $20/month for more resources

### **Render**
- **Free tier**: Available
- **Paid**: $7/month for better performance

---

## 🎉 **Next Steps**

1. **Deploy backend** using the guide above
2. **Update dashboard** to use production URL
3. **Test all endpoints** thoroughly
4. **Monitor performance** and logs
5. **Set up custom domain** (optional)

---

## 📞 **Support**

- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Render Docs**: [render.com/docs](https://render.com/docs)
- **FastAPI Docs**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
