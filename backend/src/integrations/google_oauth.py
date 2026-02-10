"""Google OAuth client for ID token verification.

T069: GoogleOAuthClient with JWKS caching per research.md Section 1
T070: ID token verification with audience validation
T085: CSRF protection via state parameter
"""

import time
from typing import Any

import httpx
from cachetools import TTLCache
from jwt import PyJWK, PyJWKClient
from jwt.exceptions import InvalidTokenError

from src.config import Settings


class GoogleOAuthError(Exception):
    """Base exception for Google OAuth errors."""

    pass


class InvalidGoogleTokenError(GoogleOAuthError):
    """Raised when Google ID token is invalid."""

    pass


class GoogleTokenExpiredError(GoogleOAuthError):
    """Raised when Google ID token has expired."""

    pass


class GoogleOAuthClient:
    """Client for Google OAuth ID token verification.

    Verifies Google ID tokens using Google's public JWKS endpoint.
    Implements caching for JWKS keys (24-hour TTL).

    Per research.md Section 1:
    - JWKS URL: https://www.googleapis.com/oauth2/v3/certs
    - Cache JWKS with 24-hour TTL
    - Validate issuer is https://accounts.google.com
    - Validate audience matches our client ID
    """

    GOOGLE_JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"
    GOOGLE_ISSUERS = ["https://accounts.google.com", "accounts.google.com"]
    CACHE_TTL = 86400  # 24 hours in seconds

    def __init__(self, settings: Settings):
        self.settings = settings
        self.client_id = settings.google_client_id
        self._jwks_client: PyJWKClient | None = None
        self._jwks_cache: TTLCache = TTLCache(maxsize=10, ttl=self.CACHE_TTL)

    def _get_jwks_client(self) -> PyJWKClient:
        """Get or create the JWKS client with caching."""
        if self._jwks_client is None:
            self._jwks_client = PyJWKClient(
                self.GOOGLE_JWKS_URL,
                cache_jwk_set=True,
                lifespan=self.CACHE_TTL,
            )
        return self._jwks_client

    async def verify_id_token(self, id_token: str) -> dict[str, Any]:
        """Verify a Google ID token and extract user claims.

        Args:
            id_token: The Google ID token to verify

        Returns:
            Dictionary containing verified user claims:
            - sub: Google user ID
            - email: User email
            - name: User's display name
            - picture: Profile picture URL

        Raises:
            InvalidGoogleTokenError: If token is invalid
            GoogleTokenExpiredError: If token has expired
        """
        import jwt

        try:
            # Get the signing key from Google's JWKS
            jwks_client = self._get_jwks_client()
            signing_key = jwks_client.get_signing_key_from_jwt(id_token)

            # Decode and verify the token
            payload = jwt.decode(
                id_token,
                signing_key.key,
                algorithms=["RS256"],
                audience=self.client_id,
                issuer=self.GOOGLE_ISSUERS,
                options={
                    "verify_signature": True,
                    "verify_aud": True,
                    "verify_iss": True,
                    "verify_exp": True,
                    "require": ["sub", "email", "iss", "aud", "exp", "iat"],
                },
            )

            # Ensure email is verified
            if not payload.get("email_verified", False):
                raise InvalidGoogleTokenError("Email not verified with Google")

            return {
                "sub": payload["sub"],
                "email": payload["email"],
                "name": payload.get("name", payload["email"].split("@")[0]),
                "picture": payload.get("picture"),
            }

        except jwt.ExpiredSignatureError:
            raise GoogleTokenExpiredError("Google ID token has expired")
        except jwt.InvalidTokenError as e:
            raise InvalidGoogleTokenError(f"Invalid Google ID token: {e}")
        except Exception as e:
            raise GoogleOAuthError(f"Failed to verify Google ID token: {e}")

    def generate_state_token(self) -> str:
        """Generate a CSRF state token for OAuth flow.

        T085: CSRF protection via state parameter.

        Returns:
            A secure random state token
        """
        import secrets

        return secrets.token_urlsafe(32)

    def validate_state_token(
        self, provided_state: str, expected_state: str
    ) -> bool:
        """Validate the OAuth state parameter for CSRF protection.

        T085: CSRF protection via state parameter.

        Args:
            provided_state: The state from the callback
            expected_state: The expected state from the session

        Returns:
            True if states match, False otherwise
        """
        import hmac

        return hmac.compare_digest(provided_state, expected_state)


def get_google_oauth_client(settings: Settings) -> GoogleOAuthClient:
    """Get a GoogleOAuthClient instance."""
    return GoogleOAuthClient(settings)
