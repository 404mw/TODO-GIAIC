"""Authentication API endpoints.

T077: POST /api/v1/auth/google/callback per api-specification.md Section 2.1
T078: POST /api/v1/auth/refresh per api-specification.md Section 2.2
T079: POST /api/v1/auth/logout per api-specification.md Section 2.3
T080: GET /api/v1/.well-known/jwks.json per authentication.md
T082: 10 req/min rate limit to auth endpoints (FR-061)
"""

import logging

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings, get_settings
from src.dependencies import DBSession, JWTKeyManager, get_jwt_manager
from src.integrations.google_oauth import (
    GoogleOAuthError,
    InvalidGoogleTokenError,
)
from src.middleware.error_handler import UnauthorizedError
from src.middleware.rate_limit import get_limiter, get_ip_key
from src.schemas.auth import (
    GoogleCallbackRequest,
    LogoutRequest,
    RefreshRequest,
    TokenRefreshResponse,
    TokenResponse,
    UserInfo,
)
from src.services.auth_service import (
    AuthService,
    InvalidRefreshTokenError,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

limiter = get_limiter()


# =============================================================================
# T077: POST /api/v1/auth/google/callback
# =============================================================================


@router.post(
    "/google/callback",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Exchange Google ID token for backend tokens",
    description="Verify Google ID token and issue backend JWT tokens.",
    responses={
        200: {"description": "Authentication successful"},
        400: {"description": "Invalid request body"},
        401: {"description": "Google token verification failed"},
        429: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit("10/minute", key_func=get_ip_key)
async def google_callback(
    request: Request,
    body: GoogleCallbackRequest,
    db: DBSession,
    settings: Settings = Depends(get_settings),
) -> TokenResponse:
    """Exchange Google ID token for backend JWT tokens.

    The frontend (BetterAuth) handles the OAuth flow with Google and
    obtains a Google ID token. This endpoint verifies that token and
    issues backend-specific JWT tokens.

    Flow:
    1. Verify Google ID token signature using Google's JWKS
    2. Create new user or update existing user profile
    3. Issue access token (15 min) and refresh token (7 days)
    """
    try:
        auth_service = AuthService(db, settings)

        user, access_token, refresh_token = await auth_service.authenticate_with_google(
            body.id_token
        )

        # Log successful authentication
        logger.info(
            "User authenticated",
            extra={
                "user_id": str(user.id),
                "email": user.email,
                "action": "google_auth",
            },
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=settings.jwt_access_expiry_minutes * 60,
            user=UserInfo(
                id=user.id,
                email=user.email,
                name=user.name,
                avatar_url=user.avatar_url,
                tier=user.tier,
                created_at=user.created_at,
            ),
        )

    except InvalidGoogleTokenError as e:
        logger.warning(f"Google token verification failed: {e}")
        raise UnauthorizedError(
            message="Google authentication failed",
            code="GOOGLE_AUTH_FAILED",
        )
    except GoogleOAuthError as e:
        logger.error(f"Google OAuth error: {e}")
        raise UnauthorizedError(
            message="Google authentication failed",
            code="GOOGLE_AUTH_FAILED",
        )


# =============================================================================
# T078: POST /api/v1/auth/refresh
# =============================================================================


@router.post(
    "/refresh",
    response_model=TokenRefreshResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Exchange refresh token for new access and refresh tokens.",
    responses={
        200: {"description": "Tokens refreshed successfully"},
        401: {"description": "Invalid or expired refresh token"},
        429: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit("10/minute", key_func=get_ip_key)
async def refresh_tokens(
    request: Request,
    body: RefreshRequest,
    db: DBSession,
    settings: Settings = Depends(get_settings),
) -> TokenRefreshResponse:
    """Refresh access token using refresh token.

    Implements token rotation per plan.md AD-001:
    - Old refresh token is revoked after use
    - New access and refresh tokens are issued
    - Cannot reuse the same refresh token twice
    """
    try:
        auth_service = AuthService(db, settings)

        access_token, refresh_token = await auth_service.refresh_tokens(
            body.refresh_token
        )

        logger.info(
            "Tokens refreshed",
            extra={"action": "token_refresh"},
        )

        return TokenRefreshResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=settings.jwt_access_expiry_minutes * 60,
        )

    except InvalidRefreshTokenError as e:
        logger.warning(f"Token refresh failed: {e}")
        raise UnauthorizedError(
            message="Invalid or expired refresh token",
            code="INVALID_REFRESH_TOKEN",
        )


# =============================================================================
# T079: POST /api/v1/auth/logout
# =============================================================================


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout and revoke refresh token",
    description="Revoke the refresh token to end the session.",
    responses={
        204: {"description": "Logout successful"},
        429: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit("10/minute", key_func=get_ip_key)
async def logout(
    request: Request,
    body: LogoutRequest,
    db: DBSession,
    settings: Settings = Depends(get_settings),
):
    """Logout by revoking the refresh token.

    The access token will naturally expire (15 min).
    The refresh token is immediately revoked.
    """
    auth_service = AuthService(db, settings)

    revoked = await auth_service.revoke_refresh_token(body.refresh_token)

    if revoked:
        logger.info("User logged out", extra={"action": "logout"})

    # Always return 204, even if token wasn't found (idempotent)
    return JSONResponse(status_code=204, content=None)


# =============================================================================
# T080: GET /api/v1/.well-known/jwks.json
# =============================================================================


@router.get(
    "/.well-known/jwks.json",
    summary="Get JSON Web Key Set",
    description="Public keys for JWT verification.",
    responses={
        200: {"description": "JWKS returned successfully"},
    },
)
async def get_jwks(
    jwt_manager: JWTKeyManager = Depends(get_jwt_manager),
):
    """Return the JSON Web Key Set (JWKS) for JWT verification.

    Per authentication.md:
    - Returns public keys for verifying JWTs signed by this server
    - Enables key rotation by supporting multiple keys
    - Cache-friendly (24 hour TTL recommended)
    """
    return jwt_manager.get_jwks()
