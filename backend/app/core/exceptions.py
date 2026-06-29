"""
Custom exceptions and global FastAPI exception handlers.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse


# ─── Base Exception ───────────────────────────────────────────────────────────
class RewireError(Exception):
    """Base exception for all Rewire errors."""

    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_ERROR",
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


# ─── Auth Errors ──────────────────────────────────────────────────────────────
class AuthenticationError(RewireError):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, "AUTHENTICATION_ERROR")


class InvalidTokenError(RewireError):
    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, "INVALID_TOKEN")


class InsufficientPermissionsError(RewireError):
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, status.HTTP_403_FORBIDDEN, "INSUFFICIENT_PERMISSIONS")


# ─── Resource Errors ──────────────────────────────────────────────────────────
class NotFoundError(RewireError):
    def __init__(self, resource: str = "Resource", identifier: str = ""):
        msg = f"{resource} not found" + (f": {identifier}" if identifier else "")
        super().__init__(msg, status.HTTP_404_NOT_FOUND, "NOT_FOUND")


class ConflictError(RewireError):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, status.HTTP_409_CONFLICT, "CONFLICT")


# ─── Validation Errors ────────────────────────────────────────────────────────
class ValidationError(RewireError):
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY, "VALIDATION_ERROR")


# ─── AI Errors ────────────────────────────────────────────────────────────────
class AIServiceError(RewireError):
    def __init__(self, message: str = "AI service unavailable"):
        super().__init__(message, status.HTTP_503_SERVICE_UNAVAILABLE, "AI_SERVICE_ERROR")


# ─── Rate Limiting ────────────────────────────────────────────────────────────
class RateLimitExceededError(RewireError):
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status.HTTP_429_TOO_MANY_REQUESTS, "RATE_LIMIT_EXCEEDED")


# ─── Exception Handlers ──────────────────────────────────────────────────────
def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers."""

    @app.exception_handler(RewireError)
    async def rewire_error_handler(request: Request, exc: RewireError) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error_code,
                "message": exc.message,
                "status_code": exc.status_code,
            },
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception) -> ORJSONResponse:
        from app.core.logging import get_logger

        logger = get_logger(__name__)
        logger.error("Unhandled exception", error=str(exc), path=request.url.path)

        return ORJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "status_code": 500,
            },
        )
