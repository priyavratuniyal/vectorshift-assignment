import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional

# Create logs directory if it doesn't exist
LOGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(os.path.join(LOGS_DIR, "integrations"), exist_ok=True)

# Configure logging format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up a logger with both file and console handlers.
    
    Args:
        name: Name of the logger
        log_file: Path to the log file (relative to LOGS_DIR)
        level: Logging level
        max_bytes: Maximum size of each log file
        backup_count: Number of backup files to keep
    
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Add file handler if log_file is specified
    if log_file:
        file_path = os.path.join(LOGS_DIR, log_file)
        file_handler = RotatingFileHandler(
            file_path,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

# Create application-wide loggers
app_logger = setup_logger("app", "app.log")
error_logger = setup_logger("error", "error.log", level=logging.ERROR)
redis_logger = setup_logger("redis", "redis.log")

# Create integration-specific loggers
hubspot_logger = setup_logger("hubspot", "integrations/hubspot.log")
notion_logger = setup_logger("notion", "integrations/notion.log")
airtable_logger = setup_logger("airtable", "integrations/airtable.log")

def log_request(logger: logging.Logger, method: str, path: str, status_code: int, duration: float):
    """Log an HTTP request with its details."""
    logger.info(
        "Request: %s %s - Status: %d - Duration: %.2fms",
        method,
        path,
        status_code,
        duration * 1000
    )

def log_error(logger: logging.Logger, error: Exception, context: dict = None):
    """Log an error with optional context."""
    error_msg = f"Error: {type(error).__name__} - {str(error)}"
    if context:
        error_msg += f" - Context: {context}"
    logger.error(error_msg, exc_info=True)

def log_integration_event(
    logger: logging.Logger,
    event_type: str,
    integration: str,
    user_id: str,
    org_id: str,
    details: dict = None
):
    """Log an integration-related event."""
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "integration": integration,
        "user_id": user_id,
        "org_id": org_id
    }
    if details:
        log_data["details"] = details
    logger.info("Integration Event: %s", log_data)
