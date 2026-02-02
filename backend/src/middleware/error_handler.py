"""Global error handler middleware.

T087: Global error handler with standard error response per api-specification.md Section 11
T088: 401 UNAUTHORIZED responses with proper codes
T089: 403 FORBIDDEN for cross-user access
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base application error with standard error response format."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[list] = None,
        extra: Optional[dict] = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        self.extra = extra or {}
        super().__init__(message)


class ValidationError(AppError):
    """Request validation error."""

    def __init__(self, message: str, details: Optional[list] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=400,
            details=details,
        )


class NotFoundError(AppError):
    """Resource not found error."""

    def __init__(self, message: str = "Resource not found", resource_id: Optional[str] = None):
        extra = {"resource_id": resource_id} if resource_id else {}
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=404,
            extra=extra,
        )


class UnauthorizedError(AppError):
    """Authentication required error."""

    def __init__(
        self,
        message: str = "Authentication required",
        code: str = "UNAUTHORIZED",
        refresh_required: bool = False,
    ):
        extra = {"refresh_required": refresh_required} if refresh_required else {}
        super().__init__(
            message=message,
            code=code,
            status_code=401,
            extra=extra,
        )


class TokenExpiredError(UnauthorizedError):
    """Token expired error with refresh hint."""

    def __init__(self, message: str = "Access token expired"):
        super().__init__(
            message=message,
            code="TOKEN_EXPIRED",
            refresh_required=True,
        )


class ForbiddenError(AppError):
    """Access forbidden error.

    T089: 403 FORBIDDEN for cross-user access (FR-005)
    """

    def __init__(
        self,
        message: str = "Access denied",
        resource_id: Optional[str] = None,
        required_tier: Optional[str] = None,
        current_tier: Optional[str] = None,
    ):
        extra = {}
        if resource_id:
            extra["resource_id"] = resource_id
        if required_tier:
            extra["required_tier"] = required_tier
            extra["current_tier"] = current_tier

        code = "TIER_REQUIRED" if required_tier else "FORBIDDEN"

        super().__init__(
            message=message,
            code=code,
            status_code=403,
            extra=extra,
        )


class ConflictError(AppError):
    """Resource conflict error (version mismatch, limit exceeded)."""

    def __init__(
        self,
        message: str,
        code: str = "CONFLICT",
    ):
        super().__init__(
            message=message,
            code=code,
            status_code=409,
        )


class LimitExceededError(ConflictError):
    """Resource limit exceeded error."""

    def __init__(self, message: str = "Resource limit exceeded"):
        super().__init__(
            message=message,
            code="LIMIT_EXCEEDED",
        )


class VersionConflictError(ConflictError):
    """Optimistic locking version conflict."""

    def __init__(self, message: str = "Version conflict - resource was modified"):
        super().__init__(
            message=message,
            code="VERSION_CONFLICT",
        )


class InsufficientCreditsError(AppError):
    """Not enough AI credits."""

    def __init__(self, message: str = "Not enough AI credits"):
        super().__init__(
            message=message,
            code="INSUFFICIENT_CREDITS",
            status_code=402,
        )


class RateLimitExceededError(AppError):
    """Rate limit exceeded error."""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = 60):
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            extra={"retry_after": retry_after},
        )


class ServiceUnavailableError(AppError):
    """External service unavailable."""

    def __init__(self, message: str = "Service temporarily unavailable"):
        super().__init__(
            message=message,
            code="SERVICE_UNAVAILABLE",
            status_code=503,
        )


class AIServiceUnavailableError(ServiceUnavailableError):
    """AI service unavailable."""

    def __init__(self, message: str = "AI service temporarily unavailable"):
        super().__init__(message=message)
        self.code = "AI_SERVICE_UNAVAILABLE"


def create_error_response(code: str, message: str, details: Optional[list] = None) -> dict:
    """Create a standard error response dictionary.

    Used when raising HTTPException with detail parameter.

    Args:
        code: Error code (e.g., 'NOT_FOUND', 'TIER_REQUIRED')
        message: Human-readable error message
        details: Optional list of error details

    Returns:
        Error response dictionary
    """
    response = {
        "error": {
            "code": code,
            "message": message,
        }
    }
    if details:
        response["error"]["details"] = details
    return response


def register_error_handlers(app: FastAPI) -> None:
    """Register global error handlers on the FastAPI app.

    T087: Global error handler with standard error response.
    """

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        """Handle application-specific errors."""
        error_response = {
            "error": {
                "code": exc.code,
                "message": exc.message,
            }
        }

        if exc.details:
            error_response["error"]["details"] = exc.details

        # Add any extra fields
        for key, value in exc.extra.items():
            error_response["error"][key] = value

        # Add request ID if available
        request_id = getattr(request.state, "request_id", None)
        if request_id:
            error_response["error"]["request_id"] = request_id

        return JSONResponse(
            status_code=exc.status_code,
            content=error_response,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle Pydantic validation errors."""
        details = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            details.append({
                "field": field,
                "message": error["msg"],
            })

        error_response = {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": details,
            }
        }

        request_id = getattr(request.state, "request_id", None)
        if request_id:
            error_response["error"]["request_id"] = request_id

        return JSONResponse(
            status_code=422,
            content=error_response,
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        """Handle FastAPI HTTPExceptions."""
        # Map status codes to error codes
        code_map = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            409: "CONFLICT",
            422: "VALIDATION_ERROR",
            429: "RATE_LIMIT_EXCEEDED",
            500: "INTERNAL_ERROR",
            503: "SERVICE_UNAVAILABLE",
        }

        error_code = code_map.get(exc.status_code, "ERROR")

        error_response = {
            "error": {
                "code": error_code,
                "message": exc.detail,
            }
        }

        request_id = getattr(request.state, "request_id", None)
        if request_id:
            error_response["error"]["request_id"] = request_id

        headers = getattr(exc, "headers", None)
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response,
            headers=headers,
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle unexpected errors."""
        logger.exception("Unexpected error", exc_info=exc)

        error_response = {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            }
        }

        request_id = getattr(request.state, "request_id", None)
        if request_id:
            error_response["error"]["request_id"] = request_id

        return JSONResponse(
            status_code=500,
            content=error_response,
        )
