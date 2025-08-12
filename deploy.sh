#!/bin/bash

# 🚀 Rental Genie Deployment Script
# This script helps you prepare and deploy your backend

echo "🚀 Rental Genie Backend Deployment"
echo "=================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing git repository..."
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   Make sure to create .env file with your environment variables"
    echo "   Required variables:"
    echo "   - AIRTABLE_API_KEY"
    echo "   - AIRTABLE_BASE_ID"
    echo "   - AIRTABLE_PROPERTIES_TABLE"
    echo "   - AIRTABLE_TENANTS_TABLE"
    echo "   - OPENAI_API_KEY"
    echo "   - SLACK_WEBHOOK_RENTAL_GENIE_URL"
else
    echo "✅ .env file found"
fi

# Check if all required files exist
echo "📋 Checking required files..."

required_files=("requirements.txt" "Procfile" "runtime.txt" "app/main.py")
missing_files=()

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (missing)"
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -ne 0 ]; then
    echo "❌ Missing required files: ${missing_files[*]}"
    echo "   Please create these files before deploying"
    exit 1
fi

# Check git status
echo ""
echo "📊 Git Status:"
git status --porcelain

# Ask user if they want to commit and push
echo ""
read -p "🤔 Do you want to commit and push to GitHub? (y/n): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📝 Adding files to git..."
    git add .
    
    echo "💬 Creating commit..."
    git commit -m "Prepare for deployment - $(date)"
    
    echo "🚀 Pushing to GitHub..."
    git push origin main
    
    echo "✅ Code pushed to GitHub!"
    echo ""
    echo "🎯 Next Steps:"
    echo "1. Go to https://railway.app"
    echo "2. Sign up with your GitHub account"
    echo "3. Create a new project"
    echo "4. Deploy from GitHub repository"
    echo "5. Add your environment variables in Railway dashboard"
    echo ""
    echo "📖 See DEPLOYMENT.md for detailed instructions"
else
    echo "✅ Files are ready for deployment"
    echo ""
    echo "🎯 Next Steps:"
    echo "1. Push your code to GitHub manually"
    echo "2. Follow the deployment guide in DEPLOYMENT.md"
fi

echo ""
echo "🎉 Deployment preparation complete!"
