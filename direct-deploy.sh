#!/bin/bash
# Direct Railway deployment from local

echo "🚀 Direct Railway Deployment"
echo "==========================="

cd /Users/bigdev/mcp-crawl4ai-rag

# Login to Railway
echo "📝 Logging in to Railway..."
npx railway login

# Link to existing project or create new
echo "🔗 Linking to Railway project..."
npx railway link

echo "⚙️ Setting required environment variables..."
# Read from .env and set in Railway
if [ -f .env ]; then
    while IFS= read -r line; do
        if [[ ! "$line" =~ ^# && -n "$line" ]]; then
            npx railway variables set "$line"
        fi
    done < .env
fi

# Deploy
echo "🚀 Deploying to Railway..."
npx railway up

echo "✅ Deployment initiated!"
echo "📊 Check status: npx railway logs"
echo "🔗 Get URL: npx railway domain"
