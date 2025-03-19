from pydantic import BaseModel, Field


class ErrorTaskResponse(BaseModel):
    """Response when task had an error"""
    status: str = "error"
    message: str