"""
Enhanced HTTP API for Crawl4AI with marketplace parsing
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import asyncio
import os
import json
import re
from pathlib import Path
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Import Crawl4AI directly
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

# Load environment variables
load_dotenv()

app = FastAPI(title="Crawl4AI HTTP API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        headless=True,        browser_type="chromium",
        extra_headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    )
    crawler = AsyncWebCrawler(browser_config=browser_config)
    await crawler.start()
    print("✅ Crawler initialized successfully")

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
                items = parse_ebay_content(result.html)
            elif "facebook.com/marketplace" in request.url:
                items = parse_facebook_marketplace(result.html)
            
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
    soup = BeautifulSoup(html, 'html.parser')
    items = []
    
    # Find eBay listing cards
    listings = soup.find_all(['div', 'li'], class_=re.compile(r's-item|srp-results'))
    
    for listing in listings[:20]:  # Limit to 20 items
        try:
            # Title
            title_elem = listing.find(['h3', 'a'], class_=re.compile(r's-item__title|s-item__link'))
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            # Price
            price_elem = listing.find(['span', 'div'], class_=re.compile(r's-item__price'))
            price_text = price_elem.get_text(strip=True) if price_elem else "0"
            price = extract_price(price_text)
            
            # URL
            link_elem = listing.find('a', class_=re.compile(r's-item__link'))
            url = link_elem.get('href', '') if link_elem else ""
            
            # Image
            img_elem = listing.find('img')
            image = img_elem.get('src', '') if img_elem else ""
            
            if title and price > 0:
                items.append({
                    "title": title,
                    "price": price,
                    "url": url,
                    "image": image,
                    "marketplace": "ebay"
                })
        except Exception:
            continue
    
    return items

def parse_facebook_marketplace(html: str) -> List[Dict[str, Any]]:
    """Parse Facebook Marketplace listings"""
    soup = BeautifulSoup(html, 'html.parser')
    items = []
    
    # Facebook uses dynamic class names, look for marketplace listing patterns
    listings = soup.find_all('div', {'role': 'article'})
    
    for listing in listings[:20]:
        try:
            # Extract text content
            text_content = listing.get_text(separator=' ', strip=True)
            
            # Try to find price pattern
            price_match = re.search(r'\$[\d,]+', text_content)
            price = extract_price(price_match.group(0)) if price_match else 0
            
            # Title is usually the first substantial text
            title_parts = text_content.split('$')[0].strip() if '$' in text_content else text_content[:100]
            
            # Find image
            img_elem = listing.find('img')
            image = img_elem.get('src', '') if img_elem else ""
            
            # Find link
            link_elem = listing.find('a')
            url = f"https://facebook.com{link_elem.get('href', '')}" if link_elem else ""
            
            if title_parts and price > 0:
                items.append({
                    "title": title_parts,
                    "price": price,
                    "url": url,
                    "image": image,
                    "marketplace": "facebook"
                })
        except Exception:
            continue
    
    return items

def extract_price(price_text: str) -> float:
    """Extract numeric price from text"""
    try:
        # Remove currency symbols and non-numeric characters
        price_clean = re.sub(r'[^\d.]', '', price_text)
        return float(price_clean) if price_clean else 0
    except:
        return 0

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)