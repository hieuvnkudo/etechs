import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware để thêm Request ID vào mỗi request"""
    
    async def dispatch(self, request: Request, call_next):
        # Tạo hoặc lấy request ID từ header
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Thêm request ID vào request state
        request.state.request_id = request_id
        
        # Log request
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={"request_id": request_id},
        )
        
        # Process request
        response = await call_next(request)
        
        # Thêm request ID vào response header
        response.headers["X-Request-ID"] = request_id
        
        # Log response
        logger.info(
            f"Request completed: {request.method} {request.url.path} - "
            f"Status: {response.status_code}",
            extra={"request_id": request_id},
        )
        
        return response

