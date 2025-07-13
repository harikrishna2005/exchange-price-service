# models.py
from pydantic import BaseModel
from typing import Any, Optional


class APIResponse(BaseModel):
    status: str
    message: str
    data: Optional[Any]
    trace_id: Optional[str]


# utils.py

def success_response(message: str, data: Any = None, trace_id: str = None):
    return APIResponse(
        status="success",
        message=message,
        data=data,
        trace_id=trace_id
    )


def error_response(message: str, trace_id: str = None):
    return APIResponse(
        status="error",
        message=message,
        data=None,
        trace_id=trace_id
    )
