
from typing import Dict, Optional
from pydantic import BaseModel


class TaskResult(BaseModel):
    status: str
    result: Optional[Dict[str, int]] = None
    message: Optional[str] = None