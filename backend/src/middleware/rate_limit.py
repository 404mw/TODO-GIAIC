"""Rate limiting middleware using slowapi.

T081: Rate limiting middleware with slowapi per research.md Section 9
T082: Apply 10 req/min rate limit to auth endpoints (FR-061)
"""

from typing import Callable, Optional

from fastapi import FastAPI, Request, Response
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse

from src.config import get_settings


def get_rate_limit_key(request: Request) -> str:
    """Get the rate limiting key based on user or IP.

    Per research.md Section 9:
    - Per-user limits use JWT sub claim
    - Per-IP limits for unauthenticated endpoints (auth)
    """
    # Check if user is authenticated
    user_claims = getattr(request.state, "user_claims", None)

    if user_claims and "sub" in user_claims:
        # Use user ID for authenticated requests
        return f"user:{user_claims['sub']}"

    # Use IP address for unauthenticated requests
    return f"ip:{get_remote_address(request)}"


def get_ip_key(request: Request) -> str:
    """Get rate limiting key based on IP only (for auth endpoints)."""
    return f"ip:{get_remote_address(request)}"


# Create limiter instance
limiter = Limiter(key_func=get_rate_limit_key)


def rate_limit_exceeded_handler(
    request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    """Custom handler for rate limit exceeded errors.

    Returns standard error format per api-specification.md Section 11.
    """
    # Parse retry-after from the exception
    retry_after = 60  # Default to 60 seconds
    if exc.detail:
        # Try to parse the retry time from the detail message
        try:
            # Format is usually "Rate limit exceeded: X per Y"
            pass
        except Exception:
            pass

    error_response = {
        "error": {
            "code": "RATE_LIMIT_EXCEEDED",
            "message": "Rate limit exceeded",
            "retry_after": retry_after,
        }
    }

    request_id = getattr(request.state, "request_id", None)
    if request_id:
        error_response["error"]["request_id"] = request_id

    return JSONResponse(
        status_code=429,
        content=error_response,
        headers={
            "Retry-After": str(retry_after),
            "X-RateLimit-Limit": str(exc.detail) if exc.detail else "unknown",
            "X-RateLimit-Remaining": "0",
        },
    )


def setup_rate_limiting(app: FastAPI) -> None:
    """Configure rate limiting for the FastAPI app.

    Per plan.md Rate Limiting Strategy:
    - General API: 100 requests per minute per user
    - AI Endpoints: 20 requests per minute per user
    - Auth Endpoints: 10 requests per minute per IP
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)


# Rate limit decorators for different endpoint categories
def rate_limit_general(func: Callable) -> Callable:
    """Apply general API rate limit (100/minute).

    Use this for standard CRUD endpoints.
    """
    settings = get_settings()
    limit = f"{settings.rate_limit_general}/minute"
    return limiter.limit(limit)(func)


def rate_limit_ai(func: Callable) -> Callable:
    """Apply AI endpoint rate limit (20/minute).

    Use this for AI chat, subtask generation, etc.
    """
    settings = get_settings()
    limit = f"{settings.rate_limit_ai}/minute"
    return limiter.limit(limit)(func)


def rate_limit_auth(func: Callable) -> Callable:
    """Apply auth endpoint rate limit (10/minute per IP).

    T082: Apply 10 req/min rate limit to auth endpoints (FR-061)
    Use this for login, refresh, etc.
    """
    settings = get_settings()
    limit = f"{settings.rate_limit_auth}/minute"
    return limiter.limit(limit, key_func=get_ip_key)(func)


# Direct limiter access for inline limits
def get_limiter() -> Limiter:
    """Get the limiter instance for direct use."""
    return limiter
