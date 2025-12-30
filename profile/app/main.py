from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from app.core.config import settings
from app.core.database import create_db_and_tables, close_db
from app.core.logging import setup_logging
from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)
from app.core.health import router as health_router
from app.features.todos import router as todos_router
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.cors import setup_cors
from contextlib import asynccontextmanager
from typing import Generator
import logging

# Import models để đảm bảo chúng được đăng ký với SQLModel metadata
from app.features.todos.model import Todo  # noqa: F401

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> Generator[None, None, None]:
    # Startup: Setup logging, tạo database và tables
    setup_logging()
    logger.info("Starting up application...")
    await create_db_and_tables()
    logger.info("Application started successfully")
    yield
    # Shutdown: Đóng database connections
    logger.info("Shutting down application...")
    await close_db()
    logger.info("Application shut down successfully")


app = FastAPI(
    title=settings.app_name,
    description="FastAPI application with layered architecture",
    version="0.1.0",
    debug=settings.debug,
    lifespan=lifespan,
)

# Setup middleware
app.add_middleware(RequestIDMiddleware)
setup_cors(app)

# Register exception handlers (thứ tự quan trọng - specific trước generic)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Đăng ký routers
app.include_router(health_router)
app.include_router(todos_router)


@app.get("/", tags=["root"])
def read_root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.app_name}!",
        "version": "0.1.0",
        "docs": "/docs",
    }