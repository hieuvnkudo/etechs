from typing import Any, Dict, Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger(__name__)


class BaseAPIException(HTTPException):
    """Base exception cho tất cả API exceptions"""
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code or f"ERROR_{status_code}"


class NotFoundError(BaseAPIException):
    """Exception khi không tìm thấy resource"""
    def __init__(self, resource: str, resource_id: Any):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} with id {resource_id} not found",
            error_code="NOT_FOUND",
        )


class APIValidationError(BaseAPIException):
    """Exception cho validation errors"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR",
        )


class ConflictError(BaseAPIException):
    """Exception khi có conflict (ví dụ: duplicate)"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code="CONFLICT",
        )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handler cho HTTPException"""
    logger.warning(
        f"HTTP {exc.status_code} error: {exc.detail}",
        extra={"path": request.url.path, "method": request.method},
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": getattr(exc, "error_code", f"HTTP_{exc.status_code}"),
                "message": exc.detail,
                "path": request.url.path,
            }
        },
        headers=exc.headers,
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handler cho validation errors"""
    errors = exc.errors()
    logger.warning(
        f"Validation error: {errors}",
        extra={"path": request.url.path, "method": request.method},
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation failed",
                "details": errors,
                "path": request.url.path,
            }
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler cho unhandled exceptions"""
    logger.exception(
        f"Unhandled exception: {str(exc)}",
        extra={"path": request.url.path, "method": request.method},
        exc_info=exc,
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred",
                "path": request.url.path,
            }
        },
    )

