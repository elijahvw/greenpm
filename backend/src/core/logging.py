"""
Green PM - Logging Configuration
"""
import logging
import sys
from typing import Dict, Any
import json
from datetime import datetime

from src.core.config import settings

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        
        if hasattr(record, "extra_data"):
            log_entry["extra_data"] = record.extra_data
        
        return json.dumps(log_entry)

def setup_logging():
    """Setup application logging"""
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO if settings.ENVIRONMENT == "prod" else logging.DEBUG)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    
    if settings.ENVIRONMENT == "prod":
        # Use JSON formatter for production (Cloud Logging)
        console_handler.setFormatter(JSONFormatter())
    else:
        # Use simple formatter for development
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
    
    root_logger.addHandler(console_handler)
    
    # Set specific logger levels
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.ENVIRONMENT == "dev" else logging.WARNING
    )
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    
    # Suppress noisy loggers
    logging.getLogger("google.auth").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)