"""Unit tests for error handler middleware and error classes.

T087: Global error handler with standard error response
T088: 401 UNAUTHORIZED responses with proper codes
T089: 403 FORBIDDEN for cross-user access
"""

import pytest

from src.middleware.error_handler import (
    AIServiceUnavailableError,
    AppError,
    ConflictError,
    ForbiddenError,
    InsufficientCreditsError,
    LimitExceededError,
    NotFoundError,
    RateLimitExceededError,
    ServiceUnavailableError,
    TokenExpiredError,
    UnauthorizedError,
    ValidationError,
    VersionConflictError,
    create_error_response,
)


# =============================================================================
# ERROR CLASSES
# =============================================================================


class TestAppError:
    """Test base application error."""

    def test_default_values(self):
        err = AppError("Something went wrong")
        assert err.message == "Something went wrong"
        assert err.code == "INTERNAL_ERROR"
        assert err.status_code == 500
        assert err.details is None
        assert err.extra == {}

    def test_custom_values(self):
        err = AppError(
            message="Custom error",
            code="CUSTOM",
            status_code=418,
            details=[{"field": "foo"}],
            extra={"key": "value"},
        )
        assert err.code == "CUSTOM"
        assert err.status_code == 418
        assert err.details == [{"field": "foo"}]
        assert err.extra == {"key": "value"}

    def test_is_exception(self):
        err = AppError("test")
        assert isinstance(err, Exception)
        assert str(err) == "test"


class TestValidationError:
    """Test validation error."""

    def test_default_values(self):
        err = ValidationError("Invalid input")
        assert err.code == "VALIDATION_ERROR"
        assert err.status_code == 400
        assert err.message == "Invalid input"

    def test_with_details(self):
        details = [{"field": "email", "message": "Invalid email"}]
        err = ValidationError("Validation failed", details=details)
        assert err.details == details


class TestNotFoundError:
    """Test not found error."""

    def test_default_message(self):
        err = NotFoundError()
        assert err.message == "Resource not found"
        assert err.code == "NOT_FOUND"
        assert err.status_code == 404

    def test_with_resource_id(self):
        err = NotFoundError(resource_id="abc-123")
        assert err.extra["resource_id"] == "abc-123"

    def test_custom_message(self):
        err = NotFoundError("Task not found")
        assert err.message == "Task not found"


class TestUnauthorizedError:
    """Test unauthorized error."""

    def test_default_values(self):
        err = UnauthorizedError()
        assert err.code == "UNAUTHORIZED"
        assert err.status_code == 401
        assert err.extra == {}

    def test_with_refresh_required(self):
        err = UnauthorizedError(refresh_required=True)
        assert err.extra["refresh_required"] is True


class TestTokenExpiredError:
    """Test token expired error."""

    def test_default_values(self):
        err = TokenExpiredError()
        assert err.code == "TOKEN_EXPIRED"
        assert err.status_code == 401
        assert err.extra["refresh_required"] is True


class TestForbiddenError:
    """Test forbidden error (FR-005)."""

    def test_default_values(self):
        err = ForbiddenError()
        assert err.code == "FORBIDDEN"
        assert err.status_code == 403

    def test_with_resource_id(self):
        err = ForbiddenError(resource_id="task-123")
        assert err.extra["resource_id"] == "task-123"

    def test_with_tier_info(self):
        err = ForbiddenError(
            message="Pro tier required",
            required_tier="pro",
            current_tier="free",
        )
        assert err.code == "TIER_REQUIRED"
        assert err.extra["required_tier"] == "pro"
        assert err.extra["current_tier"] == "free"


class TestConflictError:
    """Test conflict error."""

    def test_default_code(self):
        err = ConflictError("Already exists")
        assert err.code == "CONFLICT"
        assert err.status_code == 409

    def test_custom_code(self):
        err = ConflictError("Version mismatch", code="VERSION_CONFLICT")
        assert err.code == "VERSION_CONFLICT"


class TestLimitExceededError:
    """Test limit exceeded error."""

    def test_default_values(self):
        err = LimitExceededError()
        assert err.code == "LIMIT_EXCEEDED"
        assert err.status_code == 409


class TestVersionConflictError:
    """Test version conflict error."""

    def test_default_values(self):
        err = VersionConflictError()
        assert err.code == "VERSION_CONFLICT"
        assert err.status_code == 409


class TestInsufficientCreditsError:
    """Test insufficient credits error."""

    def test_default_values(self):
        err = InsufficientCreditsError()
        assert err.code == "INSUFFICIENT_CREDITS"
        assert err.status_code == 402


class TestRateLimitExceededError:
    """Test rate limit exceeded error."""

    def test_default_values(self):
        err = RateLimitExceededError()
        assert err.code == "RATE_LIMIT_EXCEEDED"
        assert err.status_code == 429
        assert err.extra["retry_after"] == 60

    def test_custom_retry_after(self):
        err = RateLimitExceededError(retry_after=120)
        assert err.extra["retry_after"] == 120


class TestServiceUnavailableError:
    """Test service unavailable error."""

    def test_default_values(self):
        err = ServiceUnavailableError()
        assert err.code == "SERVICE_UNAVAILABLE"
        assert err.status_code == 503


class TestAIServiceUnavailableError:
    """Test AI service unavailable error."""

    def test_default_values(self):
        err = AIServiceUnavailableError()
        assert err.code == "AI_SERVICE_UNAVAILABLE"
        assert err.status_code == 503


# =============================================================================
# create_error_response TESTS
# =============================================================================


class TestCreateErrorResponse:
    """Test error response creation utility."""

    def test_basic_response(self):
        result = create_error_response("NOT_FOUND", "Resource not found")
        assert result["error"]["code"] == "NOT_FOUND"
        assert result["error"]["message"] == "Resource not found"
        assert "details" not in result["error"]

    def test_with_details(self):
        details = [{"field": "email", "message": "Invalid"}]
        result = create_error_response("VALIDATION_ERROR", "Validation failed", details)
        assert result["error"]["details"] == details

    def test_without_details(self):
        result = create_error_response("ERROR", "Something wrong", None)
        assert "details" not in result["error"]
