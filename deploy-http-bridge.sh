#!/bin/bash
# Deploy MCP HTTP Bridge as separate Railway service

echo "🌉 Deploying MCP HTTP Bridge to Railway"
echo "======================================="

cd /Users/bigdev/mcp-crawl4ai-rag

# Create new Railway service for HTTP API
npx railway login
npx railway create --name mcp-http-bridge

# Set to use HTTP Dockerfile
npx railway variables set RAILWAY_DOCKERFILE_PATH="Dockerfile.http"

# Copy environment variables from .env
if [ -f .env ]; then
    source .env
    npx railway variables set \
        SUPABASE_URL="$SUPABASE_URL" \
        SUPABASE_KEY="$SUPABASE_KEY" \
        TOGETHER_API_KEY="$TOGETHER_API_KEY"
fi

# Deploy
echo "🚀 Deploying HTTP Bridge..."
npx railway up

# Get the URL
echo "🔗 Getting bridge URL..."
npx railway domain

echo ""
echo "✅ HTTP Bridge deployed!"
echo "📝 Update your discord-crawler .env with the new URL"