import functools
import httpx
from typing import Callable


class AppException(Exception):
    """Base exception for all application errors."""
    pass


class ExternalServiceError(AppException):
    """Error when calling an external service."""
    def __init__(self, service: str, detail: str):
        self.service = service
        self.detail = detail
        super().__init__(f"{service} error: {detail}")


class UnsupportedFileTypeError(AppException):
    """Error when file type is not supported."""
    def __init__(self, accepted: list[str]):
        self.accepted = accepted
        super().__init__(f"Unsupported file type. Accepted: {', '.join(accepted)}")


def handle_external_errors(service_name: str):
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
                
            except httpx.RequestError as exc:
                raise ExternalServiceError(
                    service=service_name,
                    detail=f"Request error: {str(exc)}"
                ) from exc
                
            except ExternalServiceError:
                raise
                
            except Exception as exc:
                raise ExternalServiceError(
                    service=service_name,
                    detail=f"Unexpected error: {str(exc)}"
                ) from exc
                
        return wrapper
    return decorator