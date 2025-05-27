#!/bin/bash
# MCP Server Railway Deployment Script

echo "🚀 MCP Crawl4AI Server Railway Deployment"
echo "=========================================="

# Check if logged in
if ! npx railway whoami > /dev/null 2>&1; then
    echo "❌ Not logged in to Railway"
    echo "Please run: npx railway login"
    exit 1
fi

echo "✅ Logged in to Railway"

# Create new project or link existing
echo "🔗 Setting up Railway project..."
npx railway link || npx railway create --name mcp-crawl4ai-server

# Set environment variables from .env
echo "⚙️  Setting environment variables..."
if [ -f .env ]; then
    echo "Reading from .env file..."
    # Read .env and set variables (excluding comments and empty lines)
    while IFS= read -r line; do
        if [[ ! "$line" =~ ^# && -n "$line" ]]; then
            echo "Setting: $line"
            npx railway variables set "$line"
        fi
    done < .env
else
    echo "❌ No .env file found. Please create one from .env.example"
    exit 1
fi

# Deploy
echo "🚀 Deploying MCP Server to Railway..."
npx railway up

echo ""
echo "✅ MCP Server deployment complete!"
echo "📊 Check status: npx railway status"
echo "🌐 Get URL: npx railway domain"
echo ""
echo "⚠️  IMPORTANT: Note down the Railway URL for your MCP server"
echo "    You'll need to update MCP_SERVER_URL in your discord-crawler"
