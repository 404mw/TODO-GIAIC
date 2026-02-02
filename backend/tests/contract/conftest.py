"""Contract testing configuration with schemathesis.

Provides fixtures for API contract fuzzing and schema validation.
"""

from unittest.mock import patch

import pytest
import schemathesis
import schemathesis.openapi
from schemathesis import Case

from tests.conftest import get_test_settings


@pytest.fixture
def contract_app():
    """Create a FastAPI app with test settings for contract testing."""
    from src.config import get_settings

    get_settings.cache_clear()
    test_settings = get_test_settings()

    with patch("src.config.get_settings", return_value=test_settings):
        with patch("src.main.get_settings", return_value=test_settings):
            from src.main import create_app

            app = create_app()

    get_settings.cache_clear()
    return app


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
