"""
Minimal HTTP API for Discord Crawler
Direct implementation without complex dependencies
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import httpx
import asyncio
import os
import json
import re

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

app = FastAPI(title="Minimal MCP Bridge API", version="1.0.0")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CrawlRequest(BaseModel):
    url: str
    config: Optional[Dict[str, Any]] = {}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "minimal-mcp-bridge"}

@app.post("/crawl")
async def crawl_page(request: CrawlRequest):
    """Simple HTTP crawl without browser automation"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = await client.get(request.url, headers=headers)
            
            if response.status_code == 200:
                items = []
                if "ebay" in request.url:
                    items = parse_ebay_simple(response.text)
                
                return JSONResponse({
                    "success": True,
                    "items": items,
                    "error": None
                })
            else:
                return JSONResponse({
                    "success": False,
                    "items": [],
                    "error": f"HTTP {response.status_code}"
                })
    except Exception as e:
        return JSONResponse({
            "success": False,
            "items": [],
            "error": str(e)
        })

@app.post("/tools/crawl_single_page")
async def mcp_compatible_endpoint(params: Dict[str, Any]):
    request = CrawlRequest(url=params.get("url", ""), config=params)
    response = await crawl_page(request)
    return response.body

def parse_ebay_simple(html: str) -> List[Dict[str, Any]]:
    """Simplified eBay parser"""
    if not BeautifulSoup:
        # Fallback regex parsing if BeautifulSoup not available
        items = []
        # Simple regex to find prices
        price_pattern = r'\$[\d,]+\.?\d*'
        prices = re.findall(price_pattern, html)
        for i, price in enumerate(prices[:10]):
            items.append({
                "title": f"Item {i+1}",
                "price": float(re.sub(r'[^\d.]', '', price)),
                "url": "",
                "marketplace": "ebay"
            })
        return items
    
    soup = BeautifulSoup(html, 'html.parser')
    items = []
    
    # Find items by common patterns
    for item in soup.find_all(['div', 'li'], class_=re.compile(r's-item')):
        try:
            title = item.find(['h3', 'span'], class_=re.compile(r'title|s-item__title'))
            price = item.find(['span'], class_=re.compile(r'price|s-item__price'))
            link = item.find('a', href=True)
            
            if title and price:
                items.append({
                    "title": title.get_text(strip=True),
                    "price": float(re.sub(r'[^\d.]', '', price.get_text())),
                    "url": link.get('href', '') if link else "",
                    "marketplace": "ebay"
                })
        except:
            continue
    
    return items[:20]  # Limit to 20 items

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
