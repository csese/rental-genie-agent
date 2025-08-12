# 🚀 Heroku Deployment Guide - Rental Genie Backend

## 🎯 **Heroku Dyno Requirements**

### **Recommended Configuration:**
- **Dyno Type**: Basic
- **Plan**: Basic ($7/month)
- **Specs**: 512MB RAM, 1x CPU
- **Perfect for**: Development, testing, and moderate production use

### **Alternative Options:**
- **Standard 1X**: $25/month (better performance, 512MB RAM)
- **Standard 2X**: $50/month (1GB RAM, for high traffic)

---

## 📋 **Prerequisites**

1. **Heroku Account**: Sign up at [heroku.com](https://heroku.com)
2. **Heroku CLI**: Install from [devcenter.heroku.com](https://devcenter.heroku.com/articles/heroku-cli)
3. **GitHub Repository**: Your code should be on GitHub
4. **Credit Card**: Required for Heroku account verification

---

## 🛠️ **Step-by-Step Heroku Deployment**

### **Step 1: Install Heroku CLI**

```bash
# macOS (using Homebrew)
brew tap heroku/brew && brew install heroku

# Or download from Heroku website
# https://devcenter.heroku.com/articles/heroku-cli
```

### **Step 2: Login to Heroku**

```bash
heroku login
```

### **Step 3: Create Heroku App**

```bash
# From your project directory
heroku create rental-genie-backend
```

### **Step 4: Set Environment Variables**

```bash
# Required variables
heroku config:set AIRTABLE_API_KEY=your_airtable_api_key
heroku config:set AIRTABLE_BASE_ID=apph3SwLeTZGolkwK
heroku config:set AIRTABLE_PROPERTIES_TABLE=tblO8k3E5rTXl4IAv
heroku config:set AIRTABLE_TENANTS_TABLE=tblO8k3E5rTXl4IAv
heroku config:set OPENAI_API_KEY=your_openai_api_key

# Optional variables
heroku config:set SLACK_WEBHOOK_RENTAL_GENIE_URL=your_slack_webhook_url
heroku config:set ENABLE_MOCK_DATA=false
heroku config:set LOG_LEVEL=INFO
```

### **Step 5: Deploy Your App**

```bash
# Push to Heroku
git push heroku main

# Or if you're on a different branch
git push heroku your-branch:main
```

### **Step 6: Scale Your Dyno**

```bash
# Scale to Basic dyno ($7/month)
heroku ps:scale web=1

# Check dyno status
heroku ps
```

---

## 💰 **Cost Breakdown**

### **Basic Plan ($7/month)**
- **512MB RAM**: Sufficient for your app
- **1x CPU**: Good performance
- **Sleep after 30 minutes**: Dyno sleeps when inactive
- **Perfect for**: Development and moderate use

### **Standard 1X ($25/month)**
- **512MB RAM**: Same memory, better performance
- **1x CPU**: Better CPU allocation
- **Always on**: Never sleeps
- **Better for**: Production use

### **Standard 2X ($50/month)**
- **1GB RAM**: Double the memory
- **2x CPU**: Better performance
- **Always on**: Never sleeps
- **For**: High traffic applications

---

## 🔧 **Performance Optimization**

### **Dyno Configuration**
```bash
# Check current dyno type
heroku ps:type

# Upgrade to Standard 1X for better performance
heroku ps:type standard-1x

# Scale to multiple dynos (if needed)
heroku ps:scale web=2
```

### **Memory Optimization**
- **Monitor memory usage**: `heroku logs --tail`
- **Optimize if needed**: Consider Standard 2X for more RAM
- **Check dyno metrics**: Heroku dashboard → Metrics tab

---

## 🧪 **Testing Your Deployment**

### **Health Check**
```bash
curl https://your-app-name.herokuapp.com/health
```

### **Test Endpoints**
```bash
# Properties
curl https://your-app-name.herokuapp.com/properties

# Tenants
curl https://your-app-name.herokuapp.com/tenants

# Conversations
curl https://your-app-name.herokuapp.com/conversation
```

### **Check Logs**
```bash
# View real-time logs
heroku logs --tail

# View recent logs
heroku logs --num 100
```

---

## 🔄 **Updating Your App**

### **Automatic Deployment**
```bash
# Make changes locally
git add .
git commit -m "Update backend"
git push heroku main
```

### **Manual Deployment**
```bash
# Force rebuild
git commit --allow-empty -m "Force rebuild"
git push heroku main
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Build Fails**
   ```bash
   # Check build logs
   heroku logs --tail
   
   # Verify requirements.txt
   cat requirements.txt
   ```

2. **App Crashes**
   ```bash
   # Check runtime logs
   heroku logs --tail
   
   # Restart dyno
   heroku restart
   ```

3. **Memory Issues**
   ```bash
   # Check memory usage
   heroku logs --tail | grep "Memory"
   
   # Consider upgrading dyno
   heroku ps:type standard-1x
   ```

4. **Environment Variables**
   ```bash
   # List all config vars
   heroku config
   
   # Set missing variables
   heroku config:set VARIABLE_NAME=value
   ```

---

## 📊 **Monitoring & Analytics**

### **Heroku Dashboard**
- **Metrics**: CPU, memory, response time
- **Logs**: Real-time application logs
- **Dyno Management**: Scale, restart, monitor

### **Add-ons (Optional)**
```bash
# Add monitoring
heroku addons:create papertrail:choklad

# Add error tracking
heroku addons:create sentry:developer
```

---

## 🌐 **Custom Domain (Optional)**

```bash
# Add custom domain
heroku domains:add yourdomain.com

# Configure DNS
# Point CNAME to your-app-name.herokuapp.com
```

---

## 💡 **Best Practices**

### **For Development ($7/month)**
- Use Basic dyno
- Accept sleep after 30 minutes
- Monitor usage in dashboard

### **For Production ($25/month)**
- Use Standard 1X dyno
- Always-on performance
- Set up monitoring

### **For High Traffic ($50/month)**
- Use Standard 2X dyno
- Consider multiple dynos
- Set up load balancing

---

## 🎉 **Next Steps**

1. **✅ Deploy to Heroku** using the guide above
2. ** Test all endpoints** thoroughly
3. **📊 Monitor performance** in Heroku dashboard
4. **🌐 Update dashboard** to use Heroku URL
5. **🔒 Set up monitoring** (optional)

---

## 📞 **Support**

- **Heroku Docs**: [devcenter.heroku.com](https://devcenter.heroku.com)
- **Heroku Support**: [help.heroku.com](https://help.heroku.com)
- **FastAPI Docs**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)

---

## 🎯 **Quick Start Commands**

```bash
# One-click deployment (after setup)
heroku create rental-genie-backend
heroku config:set AIRTABLE_API_KEY=your_key
heroku config:set OPENAI_API_KEY=your_key
git push heroku main
heroku open
```

**🎉 Your Rental Genie backend will be live on Heroku!**
