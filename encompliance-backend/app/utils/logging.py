import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional

from loguru import logger
from pythonjsonlogger import jsonlogger

from app.core.config import settings


class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentation.
    See https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter for logging
    """

    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        super().add_fields(log_record, record, message_dict)
        log_record["timestamp"] = datetime.utcnow().isoformat()
        log_record["level"] = record.levelname
        log_record["environment"] = settings.ENVIRONMENT


def setup_logging() -> None:
    """
    Configure logging for the application
    """
    # Remove all handlers from the root logger
    logging.root.handlers = []
    
    # Set log level based on settings
    log_level = settings.LOG_LEVEL.upper()
    
    # Configure loguru
    logger.configure(
        handlers=[
            {
                "sink": sys.stdout,
                "level": log_level,
                "format": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            }
        ]
    )
    
    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=log_level)
    
    # Update logging levels for some noisy loggers
    for logger_name in ["uvicorn", "uvicorn.error", "fastapi"]:
        logging.getLogger(logger_name).handlers = [InterceptHandler()]
        logging.getLogger(logger_name).propagate = False
    
    # Configure JSON logging for production
    if settings.ENVIRONMENT == "production":
        json_handler = {
            "sink": sys.stdout,
            "level": log_level,
            "format": lambda record: json.dumps(
                {
                    "timestamp": record["time"].isoformat(),
                    "level": record["level"].name,
                    "message": record["message"],
                    "name": record["name"],
                    "function": record["function"],
                    "line": record["line"],
                    "environment": settings.ENVIRONMENT,
                }
            ),
        }
        logger.configure(handlers=[json_handler])
    
    logger.info(f"Logging configured. Level: {log_level}, Environment: {settings.ENVIRONMENT}")
