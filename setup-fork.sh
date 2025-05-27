#!/bin/bash
# Setup fork and push changes

echo "🍴 Setting up your fork of mcp-crawl4ai-rag"
echo "==========================================="

# Get GitHub username
read -p "Enter your GitHub username: " GITHUB_USER

# Add your fork as a remote
echo "📡 Adding your fork as remote..."
git remote add myfork "https://github.com/${GITHUB_USER}/mcp-crawl4ai-rag.git"

# Show remotes
echo "📋 Current remotes:"
git remote -v

# Push to your fork
echo "🚀 Pushing to your fork..."
git push myfork main

echo ""
echo "✅ Done! Your changes are now on your fork."
echo "🔗 View at: https://github.com/${GITHUB_USER}/mcp-crawl4ai-rag"
echo ""
echo "📦 Next steps for Railway:"
echo "1. Go to Railway dashboard"
echo "2. Connect to GitHub"
echo "3. Select your fork: ${GITHUB_USER}/mcp-crawl4ai-rag"
echo "4. Railway will auto-deploy with HTTP API!"
