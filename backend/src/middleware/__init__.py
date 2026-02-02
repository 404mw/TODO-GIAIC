"""FastAPI middleware for cross-cutting concerns."""

from src.middleware.auth import AuthMiddleware
from src.middleware.security import SecurityHeadersMiddleware
from src.middleware.error_handler import (
    AppError,
    ConflictError,
    ForbiddenError,
    InsufficientCreditsError,
    LimitExceededError,
    NotFoundError,
    RateLimitExceededError,
    ServiceUnavailableError,
    TokenExpiredError,
    UnauthorizedError,
    ValidationError,
    VersionConflictError,
    register_error_handlers,
)
from src.middleware.idempotency import IdempotencyMiddleware, cleanup_expired_idempotency_keys
from src.middleware.rate_limit import (
    get_limiter,
    rate_limit_ai,
    rate_limit_auth,
    rate_limit_general,
    setup_rate_limiting,
)
from src.middleware.request_id import RequestIDMiddleware

__all__ = [
    "AuthMiddleware",
    "IdempotencyMiddleware",
    "RequestIDMiddleware",
    "SecurityHeadersMiddleware",
    "AppError",
    "ConflictError",
    "ForbiddenError",
    "InsufficientCreditsError",
    "LimitExceededError",
    "NotFoundError",
    "RateLimitExceededError",
    "ServiceUnavailableError",
    "TokenExpiredError",
    "UnauthorizedError",
    "ValidationError",
    "VersionConflictError",
    "register_error_handlers",
    "cleanup_expired_idempotency_keys",
    "get_limiter",
    "rate_limit_ai",
    "rate_limit_auth",
    "rate_limit_general",
    "setup_rate_limiting",
]
