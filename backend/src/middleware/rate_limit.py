"""
Green PM - Rate Limiting Middleware
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
import asyncio
from collections import defaultdict, deque
from typing import Dict, Deque
import logging

from src.core.config import settings

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using sliding window"""
    
    def __init__(self, app, requests_per_window: int = None, window_seconds: int = None):
        super().__init__(app)
        self.requests_per_window = requests_per_window or settings.RATE_LIMIT_REQUESTS
        self.window_seconds = window_seconds or settings.RATE_LIMIT_WINDOW
        self.client_requests: Dict[str, Deque[float]] = defaultdict(deque)
        self.cleanup_task = None
        
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks and static files
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Get client identifier
        client_ip = self.get_client_ip(request)
        
        # Check rate limit
        if not await self.is_allowed(client_ip):
            logger.warning(
                f"Rate limit exceeded for client {client_ip}",
                extra={"client_ip": client_ip, "path": request.url.path}
            )
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "retry_after": self.window_seconds
                },
                headers={"Retry-After": str(self.window_seconds)}
            )
        
        # Record the request
        await self.record_request(client_ip)
        
        # Start cleanup task if not running
        if self.cleanup_task is None or self.cleanup_task.done():
            self.cleanup_task = asyncio.create_task(self.cleanup_old_requests())
        
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = await self.get_remaining_requests(client_ip)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_window)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + self.window_seconds)
        
        return response
    
    def get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check for forwarded headers (from load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host
    
    async def is_allowed(self, client_ip: str) -> bool:
        """Check if client is allowed to make a request"""
        now = time.time()
        window_start = now - self.window_seconds
        
        # Get client's request history
        requests = self.client_requests[client_ip]
        
        # Remove old requests
        while requests and requests[0] < window_start:
            requests.popleft()
        
        # Check if under limit
        return len(requests) < self.requests_per_window
    
    async def record_request(self, client_ip: str):
        """Record a request for the client"""
        now = time.time()
        self.client_requests[client_ip].append(now)
    
    async def get_remaining_requests(self, client_ip: str) -> int:
        """Get remaining requests for client"""
        now = time.time()
        window_start = now - self.window_seconds
        
        requests = self.client_requests[client_ip]
        
        # Remove old requests
        while requests and requests[0] < window_start:
            requests.popleft()
        
        return max(0, self.requests_per_window - len(requests))
    
    async def cleanup_old_requests(self):
        """Cleanup old request records periodically"""
        while True:
            try:
                await asyncio.sleep(self.window_seconds)
                now = time.time()
                window_start = now - self.window_seconds
                
                # Clean up old requests for all clients
                clients_to_remove = []
                for client_ip, requests in self.client_requests.items():
                    while requests and requests[0] < window_start:
                        requests.popleft()
                    
                    # Remove clients with no recent requests
                    if not requests:
                        clients_to_remove.append(client_ip)
                
                for client_ip in clients_to_remove:
                    del self.client_requests[client_ip]
                
                logger.debug(f"Cleaned up rate limit data for {len(clients_to_remove)} clients")
                
            except Exception as e:
                logger.error(f"Error in rate limit cleanup: {e}")
                await asyncio.sleep(60)  # Wait a minute before retrying