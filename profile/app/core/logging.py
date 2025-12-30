import logging
import sys
from typing import Any, Dict
from app.core.config import settings


def setup_logging() -> None:
    """Setup logging configuration cho ứng dụng"""
    
    # Log level dựa trên debug mode
    log_level = logging.DEBUG if settings.debug else logging.INFO
    
    # Log format
    log_format = (
        "%(asctime)s - %(name)s - %(levelname)s - "
        "%(message)s - [%(pathname)s:%(lineno)d]"
    )
    
    # Date format
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )
    
    # Set log levels cho các thư viện bên ngoài
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.DEBUG if settings.debug else logging.WARNING
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured - Level: {logging.getLevelName(log_level)}")


def get_logger(name: str) -> logging.Logger:
    """Get logger với tên cụ thể"""
    return logging.getLogger(name)

