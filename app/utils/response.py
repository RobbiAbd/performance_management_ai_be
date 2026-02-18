from typing import Any, Optional


def success_response(data: Any, message: str = "Success", code: int = 200) -> dict:
    """Standard success response format."""
    return {
        "message": message,
        "status": "success",
        "code": code,
        "data": data,
    }


def error_response(
    message: str, code: int = 400, data: Optional[Any] = None
) -> dict:
    """Standard error response format."""
    return {
        "message": message,
        "status": "error",
        "code": code,
        "data": data,
    }
