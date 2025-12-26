import uuid
import time
import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger()

async def logging_middleware(request: Request, call_next):
    # 1. Tạo request_id duy nhất
    request_id = str(uuid.uuid4())
    
    # 2. Gắn thông tin vào contextvars để dùng chung cho toàn bộ request
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
    )

    start_time = time.time()
    
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error("request_failed", error=str(e))
        raise e
    
    process_time = time.time() - start_time
    
    # 3. Log kết quả sau khi xử lý xong
    logger.info(
        "request_finished",
        status_code=response.status_code,
        duration=f"{process_time:.4f}s"
    )
    
    # Trả về request_id trong header
    response.headers["X-Request-ID"] = request_id
    
    return response

