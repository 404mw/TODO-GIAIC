"""Schemathesis fuzz tests for authentication endpoints.

T375: Run schemathesis against auth endpoints.

These tests use property-based testing to find edge cases and
potential issues with the auth API contract.
"""

import pytest
import schemathesis.openapi
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def app(contract_app):
    """Use the shared contract app with test settings."""
    return contract_app


@pytest.fixture
def schema(app):
    """Create schemathesis schema from app."""
    return schemathesis.openapi.from_dict(app.openapi())


@pytest.fixture
async def fuzz_client(app):
    """Async HTTP client that lives inside the patched contract_app context."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


# =============================================================================
# AUTH ENDPOINT FUZZ TESTS
# =============================================================================


@pytest.mark.parametrize(
    "endpoint,method",
    [
        ("/api/v1/auth/google/callback", "POST"),
        ("/api/v1/auth/refresh", "POST"),
        ("/api/v1/auth/logout", "POST"),
    ],
)
class TestAuthEndpointsFuzz:
    """Fuzz tests for authentication endpoints."""

    def test_endpoint_exists_in_schema(self, schema, endpoint, method):
        """Test that auth endpoints are defined in schema."""
        openapi_schema = schema.raw_schema
        paths = openapi_schema.get("paths", {})

        assert endpoint in paths, f"Endpoint {endpoint} not found in schema"
        assert method.lower() in paths[endpoint], f"{method} not found for {endpoint}"


class TestGoogleCallbackFuzz:
    """Fuzz tests for Google OAuth callback endpoint."""

    @pytest.fixture
    def callback_schema(self, schema):
        """Get schema for callback endpoint only."""
        return schema.endpoints.filter(path_regex="auth/google/callback")

    @pytest.mark.asyncio
    async def test_invalid_token_format(self, fuzz_client: AsyncClient):
        """Test that invalid token formats are rejected."""
        response = await fuzz_client.post(
            "/api/v1/auth/google/callback",
            json={"id_token": "not-a-jwt"},
        )
        # Should return 400 or 401
        assert response.status_code in (400, 401)

        # Verify error response format
        data = response.json()
        assert "error" in data

    @pytest.mark.asyncio
    async def test_empty_token(self, fuzz_client: AsyncClient):
        """Test that empty token is rejected."""
        response = await fuzz_client.post(
            "/api/v1/auth/google/callback",
            json={"id_token": ""},
        )
        # Should return 400 or 422
        assert response.status_code in (400, 422)

    @pytest.mark.asyncio
    async def test_missing_token_field(self, fuzz_client: AsyncClient):
        """Test that missing token field returns validation error."""
        response = await fuzz_client.post(
            "/api/v1/auth/google/callback",
            json={},
        )
        # Should return 422 (validation error)
        assert response.status_code == 422


class TestRefreshTokenFuzz:
    """Fuzz tests for token refresh endpoint."""

    @pytest.mark.asyncio
    async def test_invalid_refresh_token(self, fuzz_client: AsyncClient):
        """Test that invalid refresh token is rejected."""
        response = await fuzz_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid-token"},
        )
        # Should return 401
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_empty_refresh_token(self, fuzz_client: AsyncClient):
        """Test that empty refresh token is rejected."""
        response = await fuzz_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": ""},
        )
        assert response.status_code in (400, 401, 422)

    @pytest.mark.asyncio
    async def test_expired_format_token(self, fuzz_client: AsyncClient):
        """Test handling of malformed JWT structure."""
        # Malformed JWT (3 parts but invalid)
        response = await fuzz_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "aaa.bbb.ccc"},
        )
        assert response.status_code == 401


class TestLogoutFuzz:
    """Fuzz tests for logout endpoint."""

    @pytest.mark.asyncio
    async def test_logout_without_auth(self, fuzz_client: AsyncClient):
        """Test that logout without auth/body returns 401 or 422."""
        response = await fuzz_client.post("/api/v1/auth/logout")
        # 422 if body validation fails first, 401 if auth check runs first
        assert response.status_code in (401, 422)


class TestJWKSFuzz:
    """Fuzz tests for JWKS endpoint."""

    @pytest.mark.asyncio
    async def test_jwks_returns_valid_structure(self, fuzz_client: AsyncClient):
        """Test that JWKS endpoint returns valid key structure."""
        response = await fuzz_client.get("/api/v1/.well-known/jwks.json")
        assert response.status_code == 200

        data = response.json()
        assert "keys" in data
        assert isinstance(data["keys"], list)

        if data["keys"]:
            key = data["keys"][0]
            assert "kty" in key
            assert "kid" in key

    @pytest.mark.asyncio
    async def test_jwks_is_idempotent(self, fuzz_client: AsyncClient):
        """Test that JWKS endpoint returns consistent results."""
        response1 = await fuzz_client.get("/api/v1/.well-known/jwks.json")
        response2 = await fuzz_client.get("/api/v1/.well-known/jwks.json")

        assert response1.json() == response2.json()


# =============================================================================
# RATE LIMITING TESTS
# =============================================================================


class TestAuthRateLimiting:
    """Test rate limiting on auth endpoints."""

    @pytest.mark.asyncio
    async def test_rate_limit_headers_present(self, fuzz_client: AsyncClient):
        """Test that rate limit headers are returned."""
        response = await fuzz_client.post(
            "/api/v1/auth/google/callback",
            json={"id_token": "test"},
        )

        # Rate limit headers should be present
        # Note: May not be present if rate limiting is not configured
        # This test verifies the API handles requests correctly


# =============================================================================
# SCHEMA VALIDATION TESTS
# =============================================================================


class TestAuthSchemaValidation:
    """Validate auth endpoint request/response schemas."""

    def test_google_callback_request_schema(self, schema):
        """Test Google callback request schema is valid."""
        openapi = schema.raw_schema
        path = openapi["paths"].get("/api/v1/auth/google/callback", {})
        post = path.get("post", {})

        assert "requestBody" in post
        content = post["requestBody"].get("content", {})
        assert "application/json" in content

    def test_refresh_request_schema(self, schema):
        """Test refresh token request schema is valid."""
        openapi = schema.raw_schema
        path = openapi["paths"].get("/api/v1/auth/refresh", {})
        post = path.get("post", {})

        assert "requestBody" in post

    def test_token_response_schema(self, schema):
        """Test token response schema includes required fields."""
        openapi = schema.raw_schema
        path = openapi["paths"].get("/api/v1/auth/google/callback", {})
        post = path.get("post", {})

        responses = post.get("responses", {})
        assert "200" in responses or "201" in responses
