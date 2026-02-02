"""Common schemas for pagination, responses, and errors.

T055: Common schemas per api-specification.md and FR-060
"""

from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination query parameters.

    Per api-specification.md General Conventions.
    """

    offset: int = Field(default=0, ge=0, description="Pagination offset")
    limit: int = Field(
        default=25,
        ge=1,
        le=100,
        description="Items per page (max 100)",
    )


class PaginationMeta(BaseModel):
    """Pagination metadata in responses.

    Per api-specification.md General Conventions.
    """

    offset: int = Field(description="Current offset")
    limit: int = Field(description="Items per page")
    total: int = Field(description="Total items available")
    has_more: bool = Field(description="Whether more items exist")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper.

    Per FR-060: Pagination with offset-based navigation.
    """

    data: list[T] = Field(description="List of items")
    pagination: PaginationMeta = Field(description="Pagination metadata")


class DataResponse(BaseModel, Generic[T]):
    """Generic single-item response wrapper."""

    data: T = Field(description="Response data")


class ErrorDetail(BaseModel):
    """Individual error detail for validation errors."""

    field: str | None = Field(default=None, description="Field that caused error")
    message: str = Field(description="Error message")


class ErrorResponse(BaseModel):
    """Standard error response format.

    Per api-specification.md Section 11.
    """

    code: str = Field(description="Error code (e.g., 'VALIDATION_ERROR')")
    message: str = Field(description="Human-readable error message")
    details: list[ErrorDetail] | None = Field(
        default=None,
        description="Additional error details",
    )
    request_id: str | None = Field(
        default=None,
        description="Request ID for tracing",
    )


class ErrorWrapper(BaseModel):
    """Error response wrapper."""

    error: ErrorResponse = Field(description="Error details")


class DeleteResponse(BaseModel):
    """Response for successful deletion with tombstone."""

    tombstone_id: UUID = Field(description="ID of created tombstone")
    recoverable_until: datetime = Field(
        description="When recovery option expires"
    )


class MessageResponse(BaseModel):
    """Simple message response."""

    message: str = Field(description="Status message")


class CountResponse(BaseModel):
    """Response with a count."""

    count: int = Field(description="Number of items affected")


# Error codes enum for documentation
class ErrorCode:
    """Standard error codes.

    Per api-specification.md Section 11.
    """

    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    FORBIDDEN = "FORBIDDEN"
    TIER_REQUIRED = "TIER_REQUIRED"
    NOT_FOUND = "NOT_FOUND"
    INSUFFICIENT_CREDITS = "INSUFFICIENT_CREDITS"
    CONFLICT = "CONFLICT"
    LIMIT_EXCEEDED = "LIMIT_EXCEEDED"
    ARCHIVED = "ARCHIVED"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    AI_SERVICE_UNAVAILABLE = "AI_SERVICE_UNAVAILABLE"
