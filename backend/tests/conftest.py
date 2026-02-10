"""Pytest configuration and fixtures for Perpetua Flow Backend tests.

Provides:
- Async test support with pytest-asyncio
- Test database setup and teardown
- Factory fixtures for test data generation
- HTTP mocking with respx
- API test client
"""

import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any
from uuid import uuid4

import pytest
import respx
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

from src.config import Settings
from src.dependencies import get_db_session, get_settings
from src.models.user import User
from src.schemas.enums import UserTier


# =============================================================================
# TEST SETTINGS
# =============================================================================


def get_test_settings() -> Settings:
    """Get test-specific settings."""
    return Settings(
        database_url="sqlite+aiosqlite:///:memory:",  # In-memory SQLite for tests
        jwt_private_key="""-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA5jhMQ4gU3luRoZxFo14wGJLmSSeQacqotR/i3AhAx0u/VUxR
9p4DASC5mAAllAuKHnxuQqv5ZOrTrs5N6m3rV/k8EEVvEWyJQ44FpjzCSMpi8hO3
Td2UN+KqLC0Frdjrw+ksb/6NvPrcT5zVW1QYsw1MQjUyGcVCbvZQzHqMiq6zBU8L
UtNQAa4tFekHqVSSyQczOKDhnrXsGgEsiH5g8Tt5am7ZbQpc59cOutm5Jn2UoBwo
AMutjp38XUxxf835hYQcPu8IeN0wo9XB+Wx6wVQaHK/jpccwP8LVpd14AxWT4r/2
X8XOl+dHIaWvdisy5WJOjA9+NyxEX9Fes6qy2wIDAQABAoIBAAxgBgLH9liLiIpX
jvYR/Tjc8KG0YugPkOkHjpdwSXciZGW5OrCshrx781ivLVXwwYW+VOOi6z7YUUpU
uaMlMcuNUK65OhgFgw1ivX1VnRtHkcZcdp5/ZNUU4JE2VwH6JpY7MFHRgkdLHtDt
Z8Scgnq2zMdu+kNLXgpT6uegRhy63uKt7vP4m+5yNe9MBr7ymVBlqFaN77syDNXP
beuLxYqFLtGn5EPvcUOdIPsK5JodOKb8YaKx2CV9zxspendj5I123vDT7+75yFDt
5ELkMw4sgvlwpS2wVV0zrDwMxexWDVidynmbzsCgQvRxHlUEkqtQCwsl9WRjSuyQ
dz7vp1ECgYEA9FeOJRfCY5EHvFQaUfDArel++iOwrPVV7wjTQ20ogTY/Rv340GY8
WJL8M4nt+8oUw/0q4BCo+EIMSpW8cFPPx3yttWCFHrZFoaZ3VS6v4r2qtGPd+UmL
VeimZPf4fCMs537IlwSIUDtCgHvqArLgMfDHX7e+RGr/7LKg8MRdqMsCgYEA8TRA
mueER76NiSxXvF9BPQ6ZbaqdtLTfXNGAlCu+obwelLtmgIGyYE1E0AMKKlCvrxvo
y044CTHtWM+S/J2JOiKnEKUcdBRRDHL32et9K4E6fngconRYy6Jnxy/4lQpWTiOS
YWX/tgTVo8zPvFo+u7wT43Fat91k9xLikQdfrDECgYEAqjz6Z3OXV0GrzxYVxHNl
+4WMl4EYTlkch09xyi+aofQGwFKg8anZb6jxGIOIEP7p2udf4P8aiuWRpMGQqf5q
7MU8TfuypARAnXDbAblmiCa3cbmG5XHNJ4zRqdVvBiaH2b5myXk59BRlsBkloL26
IHFup4zgftDCAMswAK//xWMCgYASDmFPt0kVvdQGksU2msLdeTxPE1ie8HNQFXbU
oLmyjcyUQbsYn5zkzKP8Fl4qcMPWDfbNUVushIpJ/a/5LSnaqkFrY5DPt72hevHG
5HQIT7I7SW6LUr5a8Btos9SeA5oWW19X3zTXQWFk064xYWgU0a2DdzbdULuAK2++
f5jP4QKBgQCPnPzVRwK+eu2NMyQir3dXJLBl1v/AHyuU/NGwtYAXHE+XVeot4WeH
mUsxIKNnP67gwF/ahWh8vr3kFOOkyGJRm0kV7n6kOBu5JeipGJoHjPt/gl9tdqti
rp4dWZqb3o3Nn8SAHgYQxdwtkj17IWygkFlLK5Ie51J9hm4Y/FEzeQ==
-----END RSA PRIVATE KEY-----""",
        jwt_public_key="""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA5jhMQ4gU3luRoZxFo14w
GJLmSSeQacqotR/i3AhAx0u/VUxR9p4DASC5mAAllAuKHnxuQqv5ZOrTrs5N6m3r
V/k8EEVvEWyJQ44FpjzCSMpi8hO3Td2UN+KqLC0Frdjrw+ksb/6NvPrcT5zVW1QY
sw1MQjUyGcVCbvZQzHqMiq6zBU8LUtNQAa4tFekHqVSSyQczOKDhnrXsGgEsiH5g
8Tt5am7ZbQpc59cOutm5Jn2UoBwoAMutjp38XUxxf835hYQcPu8IeN0wo9XB+Wx6
wVQaHK/jpccwP8LVpd14AxWT4r/2X8XOl+dHIaWvdisy5WJOjA9+NyxEX9Fes6qy
2wIDAQAB
-----END PUBLIC KEY-----""",
        google_client_id="test-client-id.apps.googleusercontent.com",
        google_client_secret="test-client-secret",
        openai_api_key="sk-test-key",
        deepgram_api_key="test-deepgram-key",
        checkout_secret_key="sk_test_checkout_key",
        checkout_webhook_secret="whsec_test_webhook_secret",
        environment="development",
        debug=True,
    )


# =============================================================================
# EVENT LOOP CONFIGURATION
# =============================================================================


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# =============================================================================
# DATABASE FIXTURES
# =============================================================================


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine with in-memory SQLite."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # Cleanup
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide a clean database session for each test."""
    session_maker = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with session_maker() as session:
        yield session
        await session.rollback()


# =============================================================================
# SETTINGS AND APP FIXTURES
# =============================================================================


@pytest.fixture
def settings() -> Settings:
    """Provide test settings."""
    return get_test_settings()


@pytest.fixture
def app(settings: Settings, db_session: AsyncSession) -> FastAPI:
    """Create test FastAPI application."""
    from unittest.mock import patch

    from src.config import get_settings as _get_settings

    # Clear cache and prime lru_cache with test settings.
    # This ensures all code (including middleware) that calls get_settings()
    # gets the test settings from cache, not just DI-resolved code.
    _get_settings.cache_clear()
    with patch("src.config.Settings", return_value=settings):
        _get_settings()  # Primes the lru_cache with test settings

    from src.main import create_app

    app = create_app()

    # Override dependencies for FastAPI DI
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_db_session] = lambda: db_session

    yield app

    _get_settings.cache_clear()


@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Provide async HTTP client for testing."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


# =============================================================================
# USER FIXTURES
# =============================================================================


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        id=uuid4(),
        google_id=f"google-{uuid4()}",
        email=f"test-{uuid4()}@example.com",
        name="Test User",
        tier=UserTier.FREE,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def pro_user(db_session: AsyncSession) -> User:
    """Create a Pro tier test user."""
    user = User(
        id=uuid4(),
        google_id=f"google-pro-{uuid4()}",
        email=f"pro-{uuid4()}@example.com",
        name="Pro User",
        tier=UserTier.PRO,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User, settings: Settings) -> dict[str, str]:
    """Generate auth headers for the test user."""
    from src.dependencies import JWTKeyManager

    jwt_manager = JWTKeyManager(settings)
    token = jwt_manager.create_access_token(
        user_id=test_user.id,
        email=test_user.email,
        tier=test_user.tier.value,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def pro_auth_headers(pro_user: User, settings: Settings) -> dict[str, str]:
    """Generate auth headers for the Pro user."""
    from src.dependencies import JWTKeyManager

    jwt_manager = JWTKeyManager(settings)
    token = jwt_manager.create_access_token(
        user_id=pro_user.id,
        email=pro_user.email,
        tier=pro_user.tier.value,
    )
    return {"Authorization": f"Bearer {token}"}


# =============================================================================
# HTTP MOCKING FIXTURES
# =============================================================================


@pytest.fixture
def mock_google_oauth() -> Generator[respx.MockRouter, None, None]:
    """Mock Google OAuth endpoints."""
    with respx.mock(assert_all_called=False) as respx_mock:
        # Mock JWKS endpoint
        respx_mock.get("https://www.googleapis.com/oauth2/v3/certs").respond(
            json={
                "keys": [
                    {
                        "kty": "RSA",
                        "use": "sig",
                        "alg": "RS256",
                        "kid": "test-key-id",
                        "n": "test-modulus",
                        "e": "AQAB",
                    }
                ]
            }
        )
        yield respx_mock


@pytest.fixture
def mock_openai() -> Generator[respx.MockRouter, None, None]:
    """Mock OpenAI API endpoints.

    T239: Enhanced respx mock for OpenAI in tests/conftest.py

    Provides mocked responses for:
    - Chat completions (non-streaming)
    - JSON mode responses for structured output
    """
    with respx.mock(assert_all_called=False) as respx_mock:
        # Mock chat completions (non-streaming)
        respx_mock.post("https://api.openai.com/v1/chat/completions").respond(
            json={
                "id": "chatcmpl-test",
                "object": "chat.completion",
                "created": 1234567890,
                "model": "gpt-4-turbo",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "Based on your tasks, I suggest focusing on the highest priority items first. Let me help you organize your day effectively.",
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 50, "completion_tokens": 100, "total_tokens": 150},
            }
        )
        yield respx_mock


@pytest.fixture
def mock_openai_subtasks() -> Generator[respx.MockRouter, None, None]:
    """Mock OpenAI API for subtask generation with JSON response."""
    with respx.mock(assert_all_called=False) as respx_mock:
        respx_mock.post("https://api.openai.com/v1/chat/completions").respond(
            json={
                "id": "chatcmpl-subtasks",
                "object": "chat.completion",
                "created": 1234567890,
                "model": "gpt-4-turbo",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": '{"subtasks": [{"title": "Research requirements", "rationale": "Understand scope"}, {"title": "Draft outline", "rationale": "Structure work"}, {"title": "Review and refine", "rationale": "Quality check"}], "task_understanding": "Breaking down the task into actionable steps"}',
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 30, "completion_tokens": 80, "total_tokens": 110},
            }
        )
        yield respx_mock


@pytest.fixture
def mock_openai_error() -> Generator[respx.MockRouter, None, None]:
    """Mock OpenAI API to simulate service errors."""
    with respx.mock(assert_all_called=False) as respx_mock:
        respx_mock.post("https://api.openai.com/v1/chat/completions").respond(
            status_code=503,
            json={"error": {"message": "Service temporarily unavailable", "type": "server_error"}},
        )
        yield respx_mock


@pytest.fixture
def mock_deepgram() -> Generator[respx.MockRouter, None, None]:
    """Mock Deepgram API endpoints.

    T271: Add respx mock for Deepgram in tests/conftest.py

    Provides mocked responses for:
    - Transcription endpoint (POST /v1/listen)
    - With standard NOVA2 response format
    """
    with respx.mock(assert_all_called=False) as respx_mock:
        # Mock transcription endpoint with full response format
        respx_mock.post("https://api.deepgram.com/v1/listen").respond(
            json={
                "results": {
                    "channels": [
                        {
                            "alternatives": [
                                {
                                    "transcript": "This is a test transcription from Deepgram.",
                                    "confidence": 0.95,
                                    "words": [
                                        {"word": "This", "start": 0.0, "end": 0.2, "confidence": 0.98},
                                        {"word": "is", "start": 0.2, "end": 0.3, "confidence": 0.99},
                                        {"word": "a", "start": 0.3, "end": 0.4, "confidence": 0.99},
                                        {"word": "test", "start": 0.4, "end": 0.6, "confidence": 0.97},
                                        {"word": "transcription", "start": 0.6, "end": 1.1, "confidence": 0.95},
                                        {"word": "from", "start": 1.1, "end": 1.3, "confidence": 0.98},
                                        {"word": "Deepgram", "start": 1.3, "end": 1.8, "confidence": 0.94},
                                    ],
                                }
                            ]
                        }
                    ]
                },
                "metadata": {
                    "detected_language": "en",
                    "duration": 2.0,
                    "channels": 1,
                    "model": "nova-2",
                },
            }
        )
        yield respx_mock


@pytest.fixture
def mock_deepgram_error() -> Generator[respx.MockRouter, None, None]:
    """Mock Deepgram API to simulate service errors.

    T271: Error case for Deepgram integration tests.
    """
    with respx.mock(assert_all_called=False) as respx_mock:
        respx_mock.post("https://api.deepgram.com/v1/listen").respond(
            status_code=503,
            json={"error": {"message": "Service temporarily unavailable"}},
        )
        yield respx_mock


@pytest.fixture
def mock_deepgram_timeout() -> Generator[respx.MockRouter, None, None]:
    """Mock Deepgram API to simulate timeout.

    T271: Timeout case for Deepgram integration tests.
    """
    import httpx

    with respx.mock(assert_all_called=False) as respx_mock:
        respx_mock.post("https://api.deepgram.com/v1/listen").side_effect = (
            httpx.TimeoutException("Connection timed out")
        )
        yield respx_mock


@pytest.fixture
def mock_checkout() -> Generator[respx.MockRouter, None, None]:
    """Mock Checkout.com API endpoints.

    T332: Enhanced respx mock for Checkout.com in tests/conftest.py

    Provides mocked responses for:
    - Payment links (checkout session creation)
    - Subscription cancellation
    """
    with respx.mock(assert_all_called=False) as respx_mock:
        # Mock payment link creation (checkout session)
        respx_mock.post("https://api.checkout.com/payment-links").respond(
            json={
                "id": "pl_test_123",
                "redirect_url": "https://checkout.com/pay/pl_test_123",
            }
        )

        # Mock subscription cancellation
        respx_mock.post(
            url__regex=r"https://api\.checkout\.com/subscriptions/.*/cancel"
        ).respond(json={"status": "cancelled"})

        yield respx_mock


# =============================================================================
# UTILITY FIXTURES
# =============================================================================


@pytest.fixture
def idempotency_key() -> str:
    """Generate a unique idempotency key for testing."""
    return str(uuid4())
