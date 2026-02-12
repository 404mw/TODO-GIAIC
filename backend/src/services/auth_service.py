"""Authentication service for user management and token operations.

T071: AuthService.create_or_update_user
T072: AuthService.generate_tokens with RS256
T073: AuthService.refresh_tokens with rotation
T074: AuthService.revoke_refresh_token for logout
"""

import hashlib
import logging
import secrets
import time
from datetime import datetime, timedelta, timezone, UTC
from typing import Tuple
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.config import Settings
from src.dependencies import JWTKeyManager
from src.integrations.google_oauth import GoogleOAuthClient, InvalidGoogleTokenError
from src.middleware.metrics import record_auth_operation, record_auth_latency
from src.models.auth import RefreshToken
from src.models.user import User
from src.schemas.enums import UserTier


logger = logging.getLogger(__name__)


class AuthServiceError(Exception):
    """Base exception for authentication service errors."""

    pass


class InvalidRefreshTokenError(AuthServiceError):
    """Raised when refresh token is invalid, expired, or revoked."""

    pass


class UserNotFoundError(AuthServiceError):
    """Raised when user is not found."""

    pass


class AuthService:
    """Service for authentication operations.

    Handles:
    - User creation/update from Google OAuth
    - JWT token generation (access + refresh)
    - Token refresh with rotation
    - Token revocation (logout)
    """

    def __init__(self, session: AsyncSession, settings: Settings):
        self.session = session
        self.settings = settings
        self.jwt_manager = JWTKeyManager(settings)
        self.google_client = GoogleOAuthClient(settings)

    async def verify_google_token(self, id_token: str) -> dict:
        """Verify a Google ID token and extract user data.

        T069: GoogleOAuthClient with JWKS caching
        T070: ID token verification with audience validation

        Args:
            id_token: Google ID token from frontend

        Returns:
            Dictionary with user data (sub, email, name, picture)

        Raises:
            InvalidGoogleTokenError: If token is invalid
        """
        return await self.google_client.verify_id_token(id_token)

    async def create_or_update_user(self, google_user_data: dict) -> User:
        """Create a new user or update existing user from Google OAuth data.

        T071: AuthService.create_or_update_user

        Args:
            google_user_data: Dictionary containing:
                - sub: Google user ID
                - email: User email
                - name: Display name
                - picture: Avatar URL

        Returns:
            The created or updated User object
        """
        google_id = google_user_data["sub"]
        email = google_user_data["email"]
        name = google_user_data["name"]
        picture = google_user_data.get("picture")

        # Check if user exists by Google ID
        result = await self.session.execute(
            select(User).where(User.google_id == google_id)
        )
        user = result.scalar_one_or_none()

        if user is not None:
            # Update existing user's profile data from Google
            user.name = name
            if picture:
                user.avatar_url = picture
            # Email is not updated (we use Google ID as primary identifier)
            self.session.add(user)
            await self.session.flush()
            return user

        # Create new user
        user = User(
            id=uuid4(),
            google_id=google_id,
            email=email,
            name=name,
            avatar_url=picture,
            tier=UserTier.FREE,
            timezone="UTC",
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)

        return user

    async def generate_tokens(self, user: User) -> Tuple[str, str]:
        """Generate access and refresh tokens for a user.

        T072: AuthService.generate_tokens with RS256

        Args:
            user: The user to generate tokens for

        Returns:
            Tuple of (access_token, refresh_token)
        """
        # Generate access token using JWT manager
        access_token = self.jwt_manager.create_access_token(
            user_id=user.id,
            email=user.email,
            tier=user.tier.value if hasattr(user.tier, 'value') else str(user.tier),
        )

        # Generate refresh token (opaque token stored in DB)
        raw_refresh_token = secrets.token_urlsafe(64)
        token_hash = hashlib.sha256(raw_refresh_token.encode()).hexdigest()

        # Calculate expiration
        expires_at = datetime.now(UTC) + timedelta(
            days=self.settings.jwt_refresh_expiry_days
        )

        # Revoke any existing refresh tokens for this user (single active session)
        await self._revoke_user_tokens(user.id)

        # Store refresh token in database
        refresh_token_record = RefreshToken(
            id=uuid4(),
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            revoked=False,
        )
        self.session.add(refresh_token_record)
        await self.session.flush()

        return access_token, raw_refresh_token

    async def refresh_tokens(self, refresh_token: str) -> Tuple[str, str]:
        """Refresh tokens using a valid refresh token.

        T073: AuthService.refresh_tokens with rotation

        Implements token rotation: old token is revoked, new tokens issued.

        Args:
            refresh_token: The refresh token to use

        Returns:
            Tuple of (new_access_token, new_refresh_token)

        Raises:
            InvalidRefreshTokenError: If token is invalid, expired, or revoked
        """
        start = time.perf_counter()
        try:
            # Hash the provided token
            token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

            # Look up the token in the database
            result = await self.session.execute(
                select(RefreshToken).where(RefreshToken.token_hash == token_hash)
            )
            token_record = result.scalar_one_or_none()

            if token_record is None:
                raise InvalidRefreshTokenError("Refresh token not found")

            if token_record.revoked_at is not None:
                raise InvalidRefreshTokenError("Refresh token has been revoked")

            # Normalize to aware datetime for comparison (DB may store naive)
            expires_at = token_record.expires_at
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if expires_at < datetime.now(UTC):
                raise InvalidRefreshTokenError("Refresh token has expired")

            # Get the user
            result = await self.session.execute(
                select(User).where(User.id == token_record.user_id)
            )
            user = result.scalar_one_or_none()

            if user is None:
                raise InvalidRefreshTokenError("User not found for refresh token")

            # Revoke the old token (rotation)
            token_record.revoked_at = datetime.now(UTC)
            self.session.add(token_record)

            # Generate new tokens
            new_tokens = await self.generate_tokens(user)

            # T084: Record token refresh success
            record_auth_operation("token_refresh", "success")
            record_auth_latency("token_refresh", time.perf_counter() - start)

            return new_tokens
        except InvalidRefreshTokenError:
            # T084: Record token refresh failure
            record_auth_operation("token_refresh", "failure")
            record_auth_latency("token_refresh", time.perf_counter() - start)
            raise

    async def revoke_refresh_token(self, refresh_token: str) -> bool:
        """Revoke a refresh token (logout).

        T074: AuthService.revoke_refresh_token for logout

        Args:
            refresh_token: The refresh token to revoke

        Returns:
            True if token was revoked, False if not found
        """
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        token_record = result.scalar_one_or_none()

        if token_record is None:
            return False

        token_record.revoked_at = datetime.now(UTC)
        self.session.add(token_record)
        await self.session.flush()

        return True

    async def _revoke_user_tokens(self, user_id: UUID) -> int:
        """Revoke all refresh tokens for a user.

        Args:
            user_id: The user's ID

        Returns:
            Number of tokens revoked
        """
        result = await self.session.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
            )
        )
        tokens = result.scalars().all()

        count = 0
        now = datetime.now(UTC)
        for token in tokens:
            token.revoked_at = now
            self.session.add(token)
            count += 1

        if count > 0:
            await self.session.flush()

        return count

    async def authenticate_with_google(
        self, id_token: str
    ) -> Tuple[User, str, str]:
        """Complete authentication flow with Google ID token.

        Combines token verification, user creation/update, and token generation.

        Args:
            id_token: Google ID token from frontend

        Returns:
            Tuple of (user, access_token, refresh_token)
        """
        start = time.perf_counter()
        try:
            # Verify the Google token
            google_data = await self.verify_google_token(id_token)

            # Create or update user
            user = await self.create_or_update_user(google_data)

            # Generate tokens
            access_token, refresh_token = await self.generate_tokens(user)

            # T084: Record login success
            record_auth_operation("login", "success")
            record_auth_latency("login", time.perf_counter() - start)

            return user, access_token, refresh_token
        except Exception:
            # T084: Record login failure
            record_auth_operation("login", "failure")
            record_auth_latency("login", time.perf_counter() - start)
            raise


def get_auth_service(
    session: AsyncSession, settings: Settings
) -> AuthService:
    """Get an AuthService instance."""
    return AuthService(session, settings)
