from dataclasses import Field

from pydantic import BaseModel


class PendingTaskResponse(BaseModel):
    """Response when task is still processing"""
    status: str = "pending"
    message: str = "Task is still in progress."