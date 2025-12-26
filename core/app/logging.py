import structlog
import logging
import sys

def setup_logging():
    structlog.configure(
        processors=[
            # Gom các biến ngữ cảnh (contextvars) vào log
            structlog.contextvars.merge_contextvars,
            # Thêm log level (info, error, ...)
            structlog.stdlib.add_log_level,
            # Thêm timestamp
            structlog.processors.TimeStamper(fmt="iso"),
            # Hỗ trợ in ra console đẹp khi dev, JSON khi production
            structlog.dev.ConsoleRenderer() if sys.stdout.isatty() else structlog.processors.JSONRenderer(),
        ],
        # Sử dụng logger factory của structlog
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

setup_logging()
logger = structlog.get_logger()