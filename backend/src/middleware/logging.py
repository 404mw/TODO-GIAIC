"""Structured JSON logging middleware for observability (FR-065).

Provides structured logging with:
- Request ID correlation
- Timestamp in ISO 8601 format
- User ID (when authenticated)
- Action and outcome
- Request/response details
"""

import time
from typing import Any

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

# Configure structlog for JSON output
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(0),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured JSON logging of all requests.

    Logs request start, completion, and errors with structured data:
    - request_id: Correlation ID
    - user_id: Authenticated user ID (if available)
    - method: HTTP method
    - path: Request path
    - status_code: Response status
    - duration_ms: Request duration in milliseconds
    """

    # Paths to exclude from logging (health checks, metrics)
    EXCLUDE_PATHS = {"/health/live", "/health/ready", "/metrics"}

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process request and log details."""
        # Skip logging for excluded paths
        if request.url.path in self.EXCLUDE_PATHS:
            return await call_next(request)

        # Get request ID from state (set by RequestIDMiddleware)
        request_id = getattr(request.state, "request_id", "unknown")

        # Build base log context
        log_context: dict[str, Any] = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query": str(request.query_params) if request.query_params else None,
            "client_ip": self._get_client_ip(request),
        }

        # Add user ID if authenticated
        if hasattr(request.state, "user") and request.state.user:
            log_context["user_id"] = str(request.state.user.id)

        # Log request start
        logger.info("request_started", **log_context)

        # Process request and measure duration
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Add user ID after authentication (may have been set during request)
            if hasattr(request.state, "user") and request.state.user:
                log_context["user_id"] = str(request.state.user.id)

            # Log successful request
            logger.info(
                "request_completed",
                **log_context,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )

            return response

        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log error
            logger.error(
                "request_failed",
                **log_context,
                error=str(exc),
                error_type=type(exc).__name__,
                duration_ms=round(duration_ms, 2),
                exc_info=True,
            )

            raise

    def _get_client_ip(self, request: Request) -> str:
        """Get the client IP address, considering proxy headers."""
        # Check X-Forwarded-For header (set by proxies/load balancers)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()

        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to direct client
        if request.client:
            return request.client.host

        return "unknown"


def get_logger() -> structlog.BoundLogger:
    """Get a structlog logger for use in services and handlers."""
    return logger
