from typing import Dict
from pydantic import Field, BaseModel


class CompletedTaskResponse(BaseModel):
    """Response when task is completed"""
    status: str = "completed"
    result: Dict[str, int]
