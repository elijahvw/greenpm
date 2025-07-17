"""
Green PM - Authentication Middleware
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging
import time

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication and request logging middleware"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Add request ID for tracing
        import uuid
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request
        logger.info(
            f"Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "client_ip": request.client.host,
                "user_agent": request.headers.get("user-agent", "")
            }
        )
        
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Add headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            # Log response
            logger.info(
                f"Request completed",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "process_time": process_time
                }
            )
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            
            logger.error(
                f"Request failed",
                extra={
                    "request_id": request_id,
                    "error": str(e),
                    "process_time": process_time
                },
                exc_info=True
            )
            
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error", "request_id": request_id},
                headers={"X-Request-ID": request_id}
            )