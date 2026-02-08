"""Contract testing configuration with schemathesis.

Provides fixtures for API contract fuzzing and schema validation.
"""

from unittest.mock import patch

import pytest
import respx
import schemathesis
import schemathesis.openapi
from schemathesis import Case

from tests.conftest import get_test_settings


# =============================================================================
# EXTERNAL API MOCKING (autouse for all contract tests)
# =============================================================================


@pytest.fixture(autouse=True)
def mock_external_apis():
    """Auto-mock all external APIs to prevent real HTTP calls in contract tests.

    Ensures contract tests never hit real OpenAI, Deepgram, or Checkout APIs
    even when the test doesn't explicitly request a mock fixture.
    """
    with respx.mock(assert_all_called=False) as mock:
        # Mock OpenAI chat completions
        mock.post("https://api.openai.com/v1/chat/completions").respond(
            json={
                "id": "chatcmpl-contract-test",
                "object": "chat.completion",
                "created": 1234567890,
                "model": "gpt-4-turbo",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "Based on your tasks, I suggest focusing on the highest priority items first.",
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 50,
                    "completion_tokens": 100,
                    "total_tokens": 150,
                },
            }
        )

        # Mock OpenAI models list (used by SDK discovery)
        mock.get("https://api.openai.com/v1/models").respond(
            json={"data": [], "object": "list"}
        )

        # Mock Deepgram transcription
        mock.post("https://api.deepgram.com/v1/listen").respond(
            json={
                "results": {
                    "channels": [
                        {
                            "alternatives": [
                                {
                                    "transcript": "Test transcription.",
                                    "confidence": 0.95,
                                    "words": [],
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

        # Mock Checkout.com payment links
        mock.post("https://api.checkout.com/payment-links").respond(
            json={
                "id": "pl_test_contract",
                "redirect_url": "https://checkout.com/pay/pl_test_contract",
            }
        )

        # Mock Google JWKS (for OAuth tests)
        mock.get("https://www.googleapis.com/oauth2/v3/certs").respond(
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

        yield mock


@pytest.fixture
def contract_app(db_session):
    """Create a FastAPI app with test settings for contract testing.

    Primes the ``lru_cache`` on ``get_settings()`` with test settings so
    that every call site — regardless of how it imported the function —
    receives the same test configuration.  This mirrors the approach used
    by the root ``app`` fixture in ``tests/conftest.py``.
    """
    from src.config import get_settings
    from src.dependencies import get_db_session, get_settings as dep_get_settings

    get_settings.cache_clear()
    test_settings = get_test_settings()

    # Patch the Settings *class* and call get_settings() once to prime the
    # lru_cache with test settings.  After the patch context exits the
    # cached value persists, so every module that calls get_settings() will
    # receive the test settings for the lifetime of this fixture.
    with patch("src.config.Settings", return_value=test_settings):
        get_settings()  # primes lru_cache

    from src.main import create_app

    app = create_app()

    # Also override FastAPI's DI so that any endpoint that declares
    # ``settings = Depends(get_settings)`` gets the test settings.
    app.dependency_overrides[dep_get_settings] = lambda: test_settings
    # Override get_db_session to use the test SQLite session instead of
    # the real engine which passes PostgreSQL-specific pool arguments.
    app.dependency_overrides[get_db_session] = lambda: db_session

    yield app

    get_settings.cache_clear()


@pytest.fixture
def openapi_schema(contract_app):
    """Load the OpenAPI schema from the running application."""
    return contract_app.openapi()


@pytest.fixture
def schema(openapi_schema):
    """Create a schemathesis schema for fuzzing."""
    return schemathesis.openapi.from_dict(openapi_schema)


# =============================================================================
# SCHEMATHESIS HELPERS
# =============================================================================


def add_idempotency_key(case: Case) -> None:
    """Add idempotency key header to POST/PATCH test cases."""
    if case.method.upper() in ("POST", "PATCH"):
        import uuid

        case.headers = case.headers or {}
        case.headers["Idempotency-Key"] = str(uuid.uuid4())


# =============================================================================
# CONTRACT TEST HELPERS
# =============================================================================


def validate_error_response(response, expected_status: int):
    """Validate that an error response follows the standard format."""
    assert response.status_code == expected_status

    data = response.json()
    assert "error" in data
    assert "code" in data["error"]
    assert "message" in data["error"]


def validate_paginated_response(response):
    """Validate that a response follows the pagination format."""
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert "pagination" in data
    assert isinstance(data["data"], list)

    pagination = data["pagination"]
    assert "offset" in pagination
    assert "limit" in pagination
    assert "total" in pagination
    assert "has_more" in pagination
