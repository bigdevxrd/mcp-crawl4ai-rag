#!/bin/bash
# Update MCP Server to use HTTP API on Railway

echo "🔄 Updating MCP Server to HTTP API mode"
echo "======================================="

cd /Users/bigdev/mcp-crawl4ai-rag

# Check if running from GitHub or local
if [ -d ".git" ]; then
    echo "📦 Local repository detected"
    
    # Update railway.toml to use HTTP
    echo "📝 Updating railway.toml..."
    cp railway-http.toml railway.toml
    
    # Commit the change
    echo "💾 Committing changes..."
    git add railway.toml
    git commit -m "Switch to HTTP API mode for discord-crawler compatibility"
    git push
    
    echo "✅ Changes pushed to GitHub"
    echo "🔄 Railway should auto-deploy from GitHub"
else
    echo "⚠️  Not a git repository"
    echo "You need to manually update railway.toml on Railway"
fi

echo ""
echo "📋 Next steps:"
echo "1. Check Railway dashboard for deployment status"
echo "2. Once deployed, test with:"
echo "   curl https://agentic-mcp-crawler.up.railway.app/health"
echo "3. Run discord-crawler bridge test:"
echo "   cd /Users/bigdev/dealhawk-standalone/discord-crawler"
echo "   node test-railway-bridge.js"