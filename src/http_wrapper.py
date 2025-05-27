"""
HTTP API wrapper for MCP Crawl4AI server
Provides REST endpoints that communicate with the MCP server
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
import os
import json
from mcp import Client
from mcp.client.sse import sse_client

app = FastAPI(title="MCP Crawl4AI HTTP Wrapper")

# MCP client instance
mcp_client = None

class CrawlRequest(BaseModel):
    url: str
    wait_for: str = "networkidle"
    remove_overlay_elements: bool = True
    exclude_external_links: bool = True
    exclude_external_images: bool = True
    headers: Optional[Dict[str, str]] = None
    
class ToolRequest(BaseModel):
    params: Dict[str, Any]

@app.on_event("startup")
async def startup_event():
    """Initialize MCP client connection"""
    global mcp_client
    # Connect to local MCP server
    mcp_url = os.getenv("MCP_LOCAL_URL", "http://localhost:8765")
    async with sse_client(mcp_url) as (read, write):
        mcp_client = Client(read, write)
        await mcp_client.initialize()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "mcp-crawl4ai-http-wrapper"}

@app.post("/crawl")
async def crawl_page(request: CrawlRequest):
    """Crawl a single page using MCP"""
    try:
        if not mcp_client:
            raise HTTPException(status_code=503, detail="MCP client not initialized")
            
        # Call MCP crawl_single_page tool
        result = await mcp_client.call_tool(
            "crawl_single_page",
            arguments=request.dict()
        )
        
        return JSONResponse(content=result)
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.post("/tools/{tool_name}")
async def call_mcp_tool(tool_name: str, request: ToolRequest):
    """Generic endpoint to call any MCP tool"""
    try:
        if not mcp_client:
            raise HTTPException(status_code=503, detail="MCP client not initialized")
            
        # Call the specified MCP tool
        result = await mcp_client.call_tool(tool_name, arguments=request.params)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.post("/search")
async def search_knowledge_base(query: str, num_results: int = 5):
    """Search the knowledge base"""
    try:
        if not mcp_client:
            raise HTTPException(status_code=503, detail="MCP client not initialized")
            
        result = await mcp_client.call_tool(
            "search_knowledge_base",
            arguments={"query": query, "num_results": num_results}
        )
        
        return JSONResponse(content=result)
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
