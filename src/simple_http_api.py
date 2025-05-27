"""
Direct HTTP API for Crawl4AI
Simple REST endpoints for discord-crawler integration
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import asyncio
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Import Crawl4AI directly
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

# Load environment variables
load_dotenv()

app = FastAPI(title="Crawl4AI HTTP API", version="1.0.0")

# Global crawler instance
crawler = None

class CrawlRequest(BaseModel):
    url: str
    config: Optional[Dict[str, Any]] = {}

class CrawlResponse(BaseModel):
    success: bool
    items: Optional[List[Dict[str, Any]]] = []
    error: Optional[str] = None
    raw_content: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    """Initialize the crawler"""
    global crawler
    browser_config = BrowserConfig(
        headless=True,
        browser_type="chromium"
    )
    crawler = AsyncWebCrawler(browser_config=browser_config)
    await crawler.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup crawler"""
    if crawler:
        await crawler.close()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "crawl4ai-http-api",
        "crawler_ready": crawler is not None
    }

@app.post("/crawl", response_model=CrawlResponse)
async def crawl_page(request: CrawlRequest):
    """Crawl a single page"""
    try:
        if not crawler:
            raise HTTPException(status_code=503, detail="Crawler not initialized")
        
        # Configure the crawl
        crawler_config = CrawlerRunConfig(
            wait_for=request.config.get("wait_for", "networkidle"),
            cache_mode=CacheMode.BYPASS,
            timeout=request.config.get("timeout", 30000),
            remove_overlay_elements=True
        )
        
        # Perform the crawl
        result = await crawler.crawl(request.url, config=crawler_config)
        
        if result.success:
            # Parse content based on URL type
            items = []
            
            if "ebay" in request.url:
                # Parse eBay listings
                items = parse_ebay_content(result.html)
            elif "facebook.com/marketplace" in request.url:
                # Parse Facebook Marketplace
                items = parse_facebook_marketplace(result.html)
            else:
                # Generic parsing
                items = []
            
            return CrawlResponse(
                success=True,
                items=items,
                raw_content=result.cleaned_html if request.config.get("include_raw", False) else None
            )
        else:
            return CrawlResponse(
                success=False,
                error=f"Crawl failed: {result.error_message}"
            )
            
    except Exception as e:
        return CrawlResponse(
            success=False,
            error=str(e)
        )

@app.post("/tools/crawl_single_page")
async def crawl_single_page_tool(params: Dict[str, Any]):
    """MCP-compatible endpoint"""
    request = CrawlRequest(url=params.get("url", ""), config=params)
    response = await crawl_page(request)
    return response.dict()

def parse_ebay_content(html: str) -> List[Dict[str, Any]]:
    """Parse eBay listings from HTML"""
    # This is a simplified parser - you'd want to use BeautifulSoup or similar
    items = []
    # Add parsing logic here
    return items

def parse_facebook_marketplace(html: str) -> List[Dict[str, Any]]:
    """Parse Facebook Marketplace listings"""
    items = []
    # Add parsing logic here
    return items

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)