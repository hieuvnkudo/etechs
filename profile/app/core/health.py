from typing import Dict, Any
from fastapi import APIRouter, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import async_session_maker
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """Health check endpoint - kiểm tra trạng thái của service"""
    return {
        "status": "healthy",
        "service": "api",
    }


@router.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_check() -> Dict[str, Any]:
    """Readiness check - kiểm tra service có sẵn sàng nhận traffic không"""
    checks: Dict[str, Any] = {
        "status": "ready",
        "checks": {},
    }
    
    # Kiểm tra database connection
    try:
        async with async_session_maker() as session:
            result = await session.execute(text("SELECT 1"))
            result.scalar()
        checks["checks"]["database"] = "ok"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        checks["checks"]["database"] = "error"
        checks["status"] = "not_ready"
    
    return checks


@router.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness_check() -> Dict[str, Any]:
    """Liveness check - kiểm tra service còn sống không"""
    return {
        "status": "alive",
    }

