from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

from logger import app_logger

router = APIRouter()

class LogEntry(BaseModel):
    timestamp: str
    level: str
    component: str
    action: str
    details: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]

@router.post("/logs")
async def store_log(log_entry: LogEntry):
    """Store logs from frontend."""
    try:
        # Convert ISO timestamp to datetime
        timestamp = datetime.fromisoformat(log_entry.timestamp.replace('Z', '+00:00'))
        
        # Format the log message
        log_message = (
            f"[Frontend] {log_entry.component} - {log_entry.action}"
            f" - Details: {log_entry.details or {}}"
            f" - Metadata: {log_entry.metadata or {}}"
        )

        # Log using appropriate level
        if log_entry.level == "ERROR":
            app_logger.error(log_message)
        elif log_entry.level == "WARN":
            app_logger.warning(log_message)
        elif log_entry.level == "DEBUG":
            app_logger.debug(log_message)
        else:
            app_logger.info(log_message)

        return {"status": "success", "message": "Log stored successfully"}
    except Exception as e:
        app_logger.error(f"Error storing frontend log: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to store log")
