"""Authentication middleware for JWT validation.

T075: Auth middleware for JWT validation per authentication.md
T088: 401 UNAUTHORIZED responses with proper codes
"""

from typing import Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.config import get_settings
from src.dependencies import JWTKeyManager


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for JWT token validation.

    Validates JWT tokens on protected routes and attaches
    user claims to the request state.

    Per authentication.md:
    - Validates JWT signature with RS256
    - Checks token expiration
    - Validates issuer and audience claims
    - Sets request.state.user_claims for downstream access
    """

    # Paths that don't require authentication
    EXEMPT_PATHS = {
        "/api/v1/health/live",
        "/api/v1/health/ready",
        "/api/v1/auth/google/callback",
        "/api/v1/auth/refresh",
        "/api/v1/.well-known/jwks.json",
        "/docs",
        "/openapi.json",
        "/redoc",
    }

    # Paths that start with these prefixes are exempt
    EXEMPT_PREFIXES = {
        "/api/v1/webhooks/",  # Webhook endpoints use signature verification
    }

    async def dispatch(self, request: Request, call_next):
        """Process the request through auth middleware."""
        # Skip authentication for exempt paths
        path = request.url.path

        if self._is_exempt(path):
            return await call_next(request)

        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            # No auth header - let endpoint decide if auth is required
            # (using Depends(get_current_user) will raise 401)
            return await call_next(request)

        if not auth_header.startswith("Bearer "):
            return self._unauthorized_response(
                "Invalid Authorization header format",
                code="INVALID_AUTH_HEADER",
            )

        token = auth_header[7:]  # Remove "Bearer " prefix

        # Validate token
        try:
            settings = get_settings()
            jwt_manager = JWTKeyManager(settings)
            claims = jwt_manager.decode_token(token, token_type="access")

            # Attach claims to request state
            request.state.user_claims = claims

        except Exception as e:
            error_message = str(e)

            # Check if it's an expiration error
            if "expired" in error_message.lower():
                return self._unauthorized_response(
                    "Access token expired",
                    code="TOKEN_EXPIRED",
                    refresh_required=True,
                )

            return self._unauthorized_response(
                f"Invalid token: {error_message}",
                code="INVALID_TOKEN",
            )

        return await call_next(request)

    def _is_exempt(self, path: str) -> bool:
        """Check if a path is exempt from authentication."""
        if path in self.EXEMPT_PATHS:
            return True

        for prefix in self.EXEMPT_PREFIXES:
            if path.startswith(prefix):
                return True

        return False

    def _unauthorized_response(
        self,
        message: str,
        code: str = "UNAUTHORIZED",
        refresh_required: bool = False,
    ) -> JSONResponse:
        """Create a 401 Unauthorized response.

        T088: 401 UNAUTHORIZED responses with proper codes (FR-004)
        """
        error_data = {
            "error": {
                "code": code,
                "message": message,
            }
        }

        if refresh_required:
            error_data["error"]["refresh_required"] = True

        return JSONResponse(
            status_code=401,
            content=error_data,
            headers={"WWW-Authenticate": "Bearer"},
        )
