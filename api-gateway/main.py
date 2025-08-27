from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, Response, JSONResponse
import httpx
import uvicorn
import logging
from typing import Optional, Dict, Any, Union
import os
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API Gateway",
    description="Gateway for routing requests to microservices",
    version="1.0.0"
)

# Add CORS middleware
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")
PROPERTY_SERVICE_URL = os.getenv("PROPERTY_SERVICE_URL", "http://property-service:8002") 
STOCK_SERVICE_URL = os.getenv("STOCK_SERVICE_URL", "http://stock-ai-service:8002")

async def proxy_request(request: Request, service_url: str, path: str) -> Union[RedirectResponse, JSONResponse, Response]:
    """Enhanced proxy function that handles all request types properly"""
    try:
        # Get headers and filter out problematic ones
        headers: Dict[str, str] = dict(request.headers)
        # Remove headers that should not be forwarded
        problematic_headers = {
            'host', 'content-length', 'content-encoding', 
            'transfer-encoding', 'connection', 'upgrade',
            'proxy-authenticate', 'proxy-authorization',
            'te', 'trailers'
        }
        for header in problematic_headers:
            headers.pop(header, None)
        
        params: Dict[str, str] = dict(request.query_params)
        
        # Handle request body properly
        body_content: Optional[bytes] = None
        json_data: Optional[Dict[str, Any]] = None
        
        if request.method in ["POST", "PUT", "PATCH"]:
            raw_body: bytes = await request.body()
            if raw_body:
                content_type: str = request.headers.get("content-type", "")
                if "application/json" in content_type:
                    try:
                        json_data = json.loads(raw_body)
                    except json.JSONDecodeError:
                        body_content = raw_body
                else:
                    body_content = raw_body
        
        async with httpx.AsyncClient(follow_redirects=False) as client:
            url = f"{service_url}{path}"
            
            # Build request parameters
            request_params: Dict[str, Any] = {
                "method": request.method,
                "url": url,
                "headers": headers,
                "params": params,
                "timeout": 30.0
            }
            
            # Add body content appropriately
            if json_data is not None:
                request_params["json"] = json_data
            elif body_content:
                request_params["content"] = body_content
            
            response: httpx.Response = await client.request(**request_params)
            
            # Handle redirects with proper cookie forwarding
            if response.status_code in (301, 302, 307, 308):
                redirect_response = RedirectResponse(
                    url=response.headers.get("location"),
                    status_code=response.status_code
                )
                
                # Forward Set-Cookie headers from the original response
                set_cookie_headers = response.headers.get_list("set-cookie")
                for cookie_header in set_cookie_headers:
                    redirect_response.headers.append("set-cookie", cookie_header)
                
                logger.info(f"🍪 Gateway: Forwarding {len(set_cookie_headers)} cookies in redirect")
                return redirect_response
            
            # Handle different content types appropriately
            content_type: str = response.headers.get("content-type", "")
            set_cookie_headers = response.headers.get_list("set-cookie")
            
            if "application/json" in content_type:
                # For JSON responses, use JSONResponse to preserve cookies
                try:
                    json_data = response.json()
                    json_response = JSONResponse(
                        content=json_data,
                        status_code=response.status_code,
                        headers={k: v for k, v in response.headers.items() if k.lower() != "content-length"}
                    )
                    
                    # Forward Set-Cookie headers
                    for cookie_header in set_cookie_headers:
                        json_response.headers.append("set-cookie", cookie_header)
                    
                    if set_cookie_headers:
                        logger.info(f"🍪 Gateway: Forwarding {len(set_cookie_headers)} cookies in JSON response")
                    
                    return json_response
                except (ValueError, json.JSONDecodeError):
                    # If JSON parsing fails, fall back to plain response
                    return Response(
                        content=response.content,
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        media_type=content_type
                    )
            else:
                # For non-JSON responses (text, HTML, etc.), use regular Response
                text_response = Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers={k: v for k, v in response.headers.items() if k.lower() != "content-length"},
                    media_type=content_type
                )
                
                # Forward Set-Cookie headers
                for cookie_header in set_cookie_headers:
                    text_response.headers.append("set-cookie", cookie_header)
                
                if set_cookie_headers:
                    logger.info(f"🍪 Gateway: Forwarding {len(set_cookie_headers)} cookies in text response")
                
                return text_response
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Service timeout")
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")
    except Exception as e:
        logger.error(f"Proxy error: {e}")
        raise HTTPException(status_code=500, detail=f"Proxy error: {str(e)}")

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """API Gateway health check"""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "version": "1.0.0"
    }

# ===== AUTH SERVICE ROUTES =====
@app.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"], response_class=Response)
async def auth_proxy(request: Request, path: str):
    """Proxy requests to auth service"""
    logger.info(f"🌐 API Gateway: Proxying {request.method} /auth/{path} to auth-service")
    return await proxy_request(request, AUTH_SERVICE_URL, f"/auth/{path}")

# ===== PROPERTY SERVICE ROUTES =====
@app.api_route("/properties", methods=["GET", "POST"], response_class=Response)
async def property_root_proxy(request: Request):
    """Proxy root property requests to property service"""
    return await proxy_request(request, PROPERTY_SERVICE_URL, "/properties")

@app.api_route("/properties/{path:path}", methods=["GET", "POST", "PUT", "DELETE"], response_class=Response)
async def property_proxy(request: Request, path: str):
    """Proxy requests to property service"""
    return await proxy_request(request, PROPERTY_SERVICE_URL, f"/properties/{path}")

# ===== STOCK SERVICE ROUTES =====
@app.api_route("/stock/{path:path}", methods=["GET", "POST", "PUT", "DELETE"], response_class=Response)
async def stock_proxy(request: Request, path: str):
    """Proxy requests to stock AI service"""
    return await proxy_request(request, STOCK_SERVICE_URL, f"/{path}")

@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint"""
    return {
        "message": "API Gateway is running",
        "services": {
            "auth": f"{AUTH_SERVICE_URL}",
            "property": f"{PROPERTY_SERVICE_URL}",
            "stock": f"{STOCK_SERVICE_URL}"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )