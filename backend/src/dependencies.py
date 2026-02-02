"""Dependency injection for FastAPI.

Provides database sessions, authentication, and other shared dependencies.
"""

from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import UUID, uuid4

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import select

from src.config import Settings, get_settings
from src.models.user import User

# =============================================================================
# DATABASE ENGINE AND SESSION
# =============================================================================

_engine = None
_session_maker = None


def get_engine(settings: Settings = Depends(get_settings)):
    """Get or create the async database engine."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.database_url.get_secret_value(),
            echo=settings.debug,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )
    return _engine


def get_session_maker(settings: Settings = Depends(get_settings)):
    """Get or create the async session maker."""
    global _session_maker
    if _session_maker is None:
        engine = get_engine(settings)
        _session_maker = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _session_maker


async def get_db_session(
    settings: Settings = Depends(get_settings),
) -> AsyncGenerator[AsyncSession, None]:
    """Provide an async database session for request handling.

    Sessions are automatically committed on success and rolled back on error.
    """
    session_maker = get_session_maker(settings)
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# Type alias for dependency injection
DBSession = Annotated[AsyncSession, Depends(get_db_session)]


# =============================================================================
# JWT KEY MANAGER
# =============================================================================


class JWTKeyManager:
    """Manages JWT signing and verification with RS256.

    Handles key rotation by supporting multiple active public keys.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self._private_key = settings.jwt_private_key.get_secret_value()
        self._public_key = settings.jwt_public_key
        self._algorithm = settings.jwt_algorithm
        self._kid = "perpetua-flow-v1"  # Key ID for rotation support

    @property
    def algorithm(self) -> str:
        """Get the JWT signing algorithm."""
        return self._algorithm

    @property
    def public_key(self) -> str:
        """Get the public key for verification."""
        return self._public_key

    @property
    def key_id(self) -> str:
        """Get the key ID for JWKS."""
        return self._kid

    def create_access_token(
        self,
        user_id: UUID,
        email: str,
        tier: str,
        extra_claims: dict | None = None,
    ) -> str:
        """Create a new access token.

        Args:
            user_id: The user's unique identifier
            email: The user's email address
            tier: The user's subscription tier (free/pro)
            extra_claims: Additional claims to include

        Returns:
            Encoded JWT access token
        """
        now = datetime.now(UTC)
        expires = now + timedelta(minutes=self.settings.jwt_access_expiry_minutes)

        payload = {
            "sub": str(user_id),
            "email": email,
            "tier": tier,
            "type": "access",
            "iat": now,
            "exp": expires,
            "iss": "perpetua-flow",
            "jti": uuid4().hex,
            **(extra_claims or {}),
        }

        return jwt.encode(
            payload,
            self._private_key,
            algorithm=self._algorithm,
            headers={"kid": self._kid},
        )

    def create_refresh_token(self, user_id: UUID) -> str:
        """Create a new refresh token.

        Args:
            user_id: The user's unique identifier

        Returns:
            Encoded JWT refresh token
        """
        now = datetime.now(UTC)
        expires = now + timedelta(days=self.settings.jwt_refresh_expiry_days)

        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "iat": now,
            "exp": expires,
            "iss": "perpetua-flow",
        }

        return jwt.encode(
            payload,
            self._private_key,
            algorithm=self._algorithm,
            headers={"kid": self._kid},
        )

    def decode_token(self, token: str, token_type: str = "access") -> dict:
        """Decode and validate a JWT token.

        Args:
            token: The JWT token to decode
            token_type: Expected token type ('access' or 'refresh')

        Returns:
            Decoded token payload

        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                self._public_key,
                algorithms=[self._algorithm],
                issuer="perpetua-flow",
            )

            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token type. Expected {token_type}.",
                )

            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"X-Refresh-Required": "true"} if token_type == "access" else None,
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {e!s}",
            )

    def get_jwks(self) -> dict:
        """Get the JSON Web Key Set (JWKS) for public key distribution.

        Returns:
            JWKS dictionary with public keys
        """
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        import base64

        # Parse the public key
        public_key = serialization.load_pem_public_key(self._public_key.encode())

        if not isinstance(public_key, rsa.RSAPublicKey):
            raise ValueError("Only RSA keys are supported")

        # Get the public numbers
        numbers = public_key.public_numbers()

        # Convert to base64url encoding
        def int_to_base64url(n: int, length: int) -> str:
            data = n.to_bytes(length, byteorder="big")
            return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

        # RSA modulus and exponent
        n = int_to_base64url(numbers.n, (numbers.n.bit_length() + 7) // 8)
        e = int_to_base64url(numbers.e, 3)

        return {
            "keys": [
                {
                    "kty": "RSA",
                    "use": "sig",
                    "alg": self._algorithm,
                    "kid": self._kid,
                    "n": n,
                    "e": e,
                }
            ]
        }


def get_jwt_manager(settings: Settings = Depends(get_settings)) -> JWTKeyManager:
    """Get the JWT key manager instance."""
    return JWTKeyManager(settings)


JWTManager = Annotated[JWTKeyManager, Depends(get_jwt_manager)]


# =============================================================================
# AUTHENTICATION DEPENDENCIES
# =============================================================================

security = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    settings: Settings = Depends(get_settings),
    db: AsyncSession = Depends(get_db_session),
) -> User | None:
    """Get the current user if authenticated, None otherwise.

    Does not raise an error if no token is provided.
    """
    if credentials is None:
        return None

    jwt_manager = JWTKeyManager(settings)

    try:
        payload = jwt_manager.decode_token(credentials.credentials, token_type="access")
        user_id = UUID(payload["sub"])

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user is None:
            return None

        # Attach user to request state for middleware access
        request.state.user = user
        return user

    except HTTPException:
        return None


async def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    settings: Settings = Depends(get_settings),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    """Get the current authenticated user.

    Raises 401 if not authenticated.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    jwt_manager = JWTKeyManager(settings)
    payload = jwt_manager.decode_token(credentials.credentials, token_type="access")
    user_id = UUID(payload["sub"])

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Attach user to request state for middleware access
    request.state.user = user
    return user


# Type alias for dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[User | None, Depends(get_current_user_optional)]


def require_pro_tier(user: CurrentUser) -> User:
    """Require the user to have Pro tier subscription.

    Raises 403 if user is not Pro tier.
    """
    if user.tier != "pro":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Pro subscription required for this feature",
        )
    return user


ProUser = Annotated[User, Depends(require_pro_tier)]


# =============================================================================
# RESOURCE OWNERSHIP CHECK
# =============================================================================


def check_resource_ownership(resource_user_id: UUID, current_user: User) -> None:
    """Check that the current user owns the resource.

    Args:
        resource_user_id: The user ID of the resource owner
        current_user: The currently authenticated user

    Raises:
        HTTPException: 403 if user does not own the resource
    """
    if resource_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this resource",
        )
