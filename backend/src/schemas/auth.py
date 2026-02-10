"""Authentication schemas for OAuth and JWT tokens.

T046: Auth schemas per api-specification.md Section 2
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.schemas.enums import UserTier


class GoogleCallbackRequest(BaseModel):
    """Request body for Google OAuth callback.

    Per api-specification.md Section 2.1.
    """

    id_token: str = Field(
        min_length=1,
        description="Google ID token from frontend BetterAuth",
    )


class RefreshRequest(BaseModel):
    """Request body for token refresh.

    Per api-specification.md Section 2.2.
    """

    refresh_token: str = Field(
        min_length=1,
        description="Refresh token to exchange for new tokens",
    )


class LogoutRequest(BaseModel):
    """Request body for logout.

    Per api-specification.md Section 2.3.
    """

    refresh_token: str = Field(
        min_length=1,
        description="Refresh token to revoke",
    )


class UserInfo(BaseModel):
    """User information included in token response."""

    id: UUID = Field(description="User ID")
    email: str = Field(description="User email")
    name: str = Field(description="Display name")
    avatar_url: str | None = Field(default=None, description="Profile picture URL")
    tier: UserTier = Field(description="Subscription tier")
    created_at: datetime = Field(description="Account creation time")


class TokenResponse(BaseModel):
    """Token response for authentication.

    Per api-specification.md Section 2.1 and 2.2.
    """

    access_token: str = Field(description="JWT access token")
    refresh_token: str = Field(description="Opaque refresh token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(description="Access token expiry in seconds")
    user: UserInfo | None = Field(
        default=None,
        description="User info (included on initial auth)",
    )


class TokenRefreshResponse(BaseModel):
    """Response for token refresh (no user info).

    Per api-specification.md Section 2.2.
    """

    access_token: str = Field(description="New JWT access token")
    refresh_token: str = Field(description="New refresh token (rotation)")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(description="Access token expiry in seconds")


class JWKSResponse(BaseModel):
    """JWKS (JSON Web Key Set) response.

    Per authentication.md for /.well-known/jwks.json endpoint.
    """

    keys: list[dict] = Field(description="Array of JWK objects")
