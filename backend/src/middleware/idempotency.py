"""Idempotency middleware for POST/PATCH request deduplication.

T371: Implement idempotency middleware per FR-059

Client sends Idempotency-Key header with unique identifier.
Server stores response for duplicate detection within TTL window.
"""

import hashlib
import json
import logging
from datetime import UTC, datetime, timedelta
from typing import Callable
from uuid import UUID

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models.idempotency import IdempotencyKey

logger = logging.getLogger(__name__)

# Idempotency key TTL (24 hours per best practices)
IDEMPOTENCY_TTL_HOURS = 24

# Methods that require idempotency support
IDEMPOTENT_METHODS = {"POST", "PATCH"}


class IdempotencyMiddleware(BaseHTTPMiddleware):
    """Middleware for handling idempotent requests.

    Per FR-059 and research.md Section 12:
    - Accepts Idempotency-Key header on POST/PATCH requests
    - Returns cached response for duplicate requests
    - Stores response for TTL window (24 hours)
    - Returns 409 if same key used with different request body
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process request with idempotency handling."""
        # Only handle POST/PATCH methods
        if request.method not in IDEMPOTENT_METHODS:
            return await call_next(request)

        # Check for Idempotency-Key header
        idempotency_key = request.headers.get("Idempotency-Key")
        if not idempotency_key:
            # No idempotency key - proceed normally
            return await call_next(request)

        # Get user ID from request state (set by auth middleware)
        user = getattr(request.state, "user", None)
        if not user:
            # No authenticated user - proceed normally
            # Idempotency only works for authenticated requests
            return await call_next(request)

        user_id = user.id

        # Read request body for hashing
        body = await request.body()
        request_hash = self._hash_request(body)

        # Get database session
        try:
            db_session: AsyncSession = request.state.db_session
        except AttributeError:
            # No database session available - proceed normally
            logger.warning("No database session available for idempotency check")
            return await call_next(request)

        # Check for existing idempotency record
        existing = await self._get_idempotency_record(
            db_session, idempotency_key, user_id
        )

        if existing:
            # Check if request body matches
            if existing.request_hash != request_hash:
                # Same key, different request - conflict
                return JSONResponse(
                    status_code=409,
                    content={
                        "error": {
                            "code": "IDEMPOTENCY_CONFLICT",
                            "message": "Idempotency key already used with different request",
                        }
                    },
                )

            # Same key, same request - return cached response
            logger.info(
                "Returning cached response for idempotency key",
                extra={
                    "idempotency_key": idempotency_key,
                    "user_id": str(user_id),
                },
            )
            return JSONResponse(
                status_code=existing.response_status,
                content=existing.response_body,
                headers={"X-Idempotent-Replayed": "true"},
            )

        # Process request normally
        response = await call_next(request)

        # Store idempotency record for successful responses
        if 200 <= response.status_code < 500:
            await self._store_idempotency_record(
                db_session=db_session,
                key=idempotency_key,
                user_id=user_id,
                request_path=request.url.path,
                request_method=request.method,
                request_hash=request_hash,
                response=response,
            )

        return response

    def _hash_request(self, body: bytes) -> str:
        """Create hash of request body for comparison."""
        return hashlib.sha256(body).hexdigest()

    async def _get_idempotency_record(
        self, db: AsyncSession, key: str, user_id: UUID
    ) -> IdempotencyKey | None:
        """Get existing idempotency record if not expired."""
        now = datetime.now(UTC)
        result = await db.execute(
            select(IdempotencyKey).where(
                IdempotencyKey.key == key,
                IdempotencyKey.user_id == user_id,
                IdempotencyKey.expires_at > now,
            )
        )
        return result.scalar_one_or_none()

    async def _store_idempotency_record(
        self,
        db: AsyncSession,
        key: str,
        user_id: UUID,
        request_path: str,
        request_method: str,
        request_hash: str,
        response: Response,
    ) -> None:
        """Store idempotency record with response."""
        try:
            # Read response body
            response_body = None
            if hasattr(response, "body"):
                body = response.body
                if body:
                    try:
                        response_body = json.loads(body)
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        # Non-JSON response - store as-is
                        response_body = {"raw": body.decode("utf-8", errors="replace")}

            record = IdempotencyKey(
                key=key,
                user_id=user_id,
                request_path=request_path,
                request_method=request_method,
                request_hash=request_hash,
                response_status=response.status_code,
                response_body=response_body,
                created_at=datetime.now(UTC),
                expires_at=datetime.now(UTC) + timedelta(hours=IDEMPOTENCY_TTL_HOURS),
            )

            db.add(record)
            await db.commit()

            logger.debug(
                "Stored idempotency record",
                extra={
                    "idempotency_key": key,
                    "user_id": str(user_id),
                    "expires_at": record.expires_at.isoformat(),
                },
            )
        except Exception as e:
            logger.error(f"Failed to store idempotency record: {e}")
            # Don't fail the request if idempotency storage fails
            await db.rollback()


async def cleanup_expired_idempotency_keys(db: AsyncSession) -> int:
    """Clean up expired idempotency keys.

    Should be run periodically (e.g., daily via background job).

    Returns:
        Number of deleted records
    """
    from sqlalchemy import delete

    now = datetime.now(UTC)
    result = await db.execute(
        delete(IdempotencyKey).where(IdempotencyKey.expires_at < now)
    )
    await db.commit()
    return result.rowcount


__all__ = ["IdempotencyMiddleware", "cleanup_expired_idempotency_keys"]
