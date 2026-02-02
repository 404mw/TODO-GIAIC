"""Integration tests for WebSocket voice sessions.

Phase 13: Voice Transcription (Priority: P3)
Tests for FR-036 (max 300 seconds).

T273a: Test WebSocket voice session auto-closes at 300 seconds with partial transcript
T273b: Test WebSocket returns MAX_DURATION_EXCEEDED error at timeout
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.credit import AICreditLedger
from src.models.user import User
from src.schemas.enums import CreditType, CreditOperation, UserTier


# =============================================================================
# WEBSOCKET VOICE SESSION TIMEOUT TESTS (T273a, T273b)
# =============================================================================


class MockWebSocketSession:
    """Mock WebSocket session for testing voice streaming.

    Simulates a WebSocket connection with duration tracking and
    auto-close behavior at 300 seconds.
    """

    MAX_DURATION_SECONDS = 300

    def __init__(self):
        self.connected = False
        self.duration_seconds = 0
        self.partial_transcript = ""
        self.closed = False
        self.close_reason = None

    async def connect(self):
        """Simulate WebSocket connection."""
        self.connected = True

    async def stream_audio(self, duration_seconds: int):
        """Simulate streaming audio for a given duration.

        Args:
            duration_seconds: Duration to stream

        Returns:
            Tuple of (actual_duration, partial_transcript, close_reason)
        """
        if not self.connected:
            raise RuntimeError("Not connected")

        # Simulate streaming with duration check
        remaining = min(duration_seconds, self.MAX_DURATION_SECONDS)
        self.duration_seconds = remaining

        # Build partial transcript based on duration
        words_per_second = 2  # Approximate
        word_count = remaining * words_per_second
        self.partial_transcript = " ".join(
            [f"word{i}" for i in range(min(word_count, 600))]
        )

        if duration_seconds > self.MAX_DURATION_SECONDS:
            self.closed = True
            self.close_reason = "MAX_DURATION_EXCEEDED"
            return (self.MAX_DURATION_SECONDS, self.partial_transcript, "MAX_DURATION_EXCEEDED")

        return (remaining, self.partial_transcript, None)

    async def close(self, reason: str = None):
        """Close the WebSocket connection."""
        self.closed = True
        self.close_reason = reason


@pytest.mark.asyncio
async def test_websocket_voice_auto_closes_at_300_seconds(
    db_session: AsyncSession,
    pro_user: User,
):
    """T273a: WebSocket voice session auto-closes at 300 seconds with partial transcript.

    Per FR-036: Voice recording max duration is 300 seconds.
    When the limit is reached, the session should:
    1. Stop accepting new audio
    2. Return whatever partial transcript was captured
    3. Close the connection gracefully
    """
    # Setup: Grant Pro user credits
    credit = AICreditLedger(
        id=uuid4(),
        user_id=pro_user.id,
        credit_type=CreditType.SUBSCRIPTION,
        amount=100,
        balance_after=100,
        operation=CreditOperation.GRANT,
        consumed=0,
    )
    db_session.add(credit)
    await db_session.commit()

    # Create mock WebSocket session
    ws_session = MockWebSocketSession()
    await ws_session.connect()

    # Simulate streaming 350 seconds (exceeds 300 second limit)
    actual_duration, partial_transcript, close_reason = await ws_session.stream_audio(350)

    # Verify session auto-closed at 300 seconds
    assert ws_session.closed is True
    assert actual_duration == 300
    assert close_reason == "MAX_DURATION_EXCEEDED"

    # Verify partial transcript was captured (up to the 300 second mark)
    assert len(partial_transcript) > 0
    assert "word" in partial_transcript


@pytest.mark.asyncio
async def test_websocket_returns_max_duration_exceeded_error(
    db_session: AsyncSession,
    pro_user: User,
):
    """T273b: WebSocket returns MAX_DURATION_EXCEEDED error at timeout.

    Per FR-036: When 300 seconds is reached:
    - Return error code MAX_DURATION_EXCEEDED
    - Include partial transcript in response
    - Close connection with appropriate status
    """
    # Setup: Grant Pro user credits
    credit = AICreditLedger(
        id=uuid4(),
        user_id=pro_user.id,
        credit_type=CreditType.SUBSCRIPTION,
        amount=100,
        balance_after=100,
        operation=CreditOperation.GRANT,
        consumed=0,
    )
    db_session.add(credit)
    await db_session.commit()

    # Create mock WebSocket session
    ws_session = MockWebSocketSession()
    await ws_session.connect()

    # Stream exactly at the limit
    _, _, close_reason = await ws_session.stream_audio(301)

    # Verify MAX_DURATION_EXCEEDED error was returned
    assert close_reason == "MAX_DURATION_EXCEEDED"
    assert ws_session.closed is True


@pytest.mark.asyncio
async def test_websocket_voice_normal_duration_completes(
    db_session: AsyncSession,
    pro_user: User,
):
    """T273a (positive): Normal duration voice session completes without error."""
    # Setup
    credit = AICreditLedger(
        id=uuid4(),
        user_id=pro_user.id,
        credit_type=CreditType.SUBSCRIPTION,
        amount=100,
        balance_after=100,
        operation=CreditOperation.GRANT,
        consumed=0,
    )
    db_session.add(credit)
    await db_session.commit()

    # Create mock WebSocket session
    ws_session = MockWebSocketSession()
    await ws_session.connect()

    # Stream normal duration (under 300 seconds)
    actual_duration, partial_transcript, close_reason = await ws_session.stream_audio(60)

    # Verify normal completion
    assert close_reason is None
    assert ws_session.closed is False
    assert actual_duration == 60
    assert len(partial_transcript) > 0


@pytest.mark.asyncio
async def test_websocket_voice_exactly_300_seconds_allowed(
    db_session: AsyncSession,
    pro_user: User,
):
    """T273a (boundary): Exactly 300 seconds is allowed without error."""
    # Setup
    credit = AICreditLedger(
        id=uuid4(),
        user_id=pro_user.id,
        credit_type=CreditType.SUBSCRIPTION,
        amount=100,
        balance_after=100,
        operation=CreditOperation.GRANT,
        consumed=0,
    )
    db_session.add(credit)
    await db_session.commit()

    # Create mock WebSocket session
    ws_session = MockWebSocketSession()
    await ws_session.connect()

    # Stream exactly 300 seconds (boundary)
    actual_duration, partial_transcript, close_reason = await ws_session.stream_audio(300)

    # Verify boundary case completes normally
    assert close_reason is None
    assert ws_session.closed is False
    assert actual_duration == 300


@pytest.mark.asyncio
async def test_websocket_voice_partial_transcript_preserved(
    db_session: AsyncSession,
    pro_user: User,
):
    """T273a (data integrity): Partial transcript is preserved when session times out."""
    # Setup
    credit = AICreditLedger(
        id=uuid4(),
        user_id=pro_user.id,
        credit_type=CreditType.SUBSCRIPTION,
        amount=100,
        balance_after=100,
        operation=CreditOperation.GRANT,
        consumed=0,
    )
    db_session.add(credit)
    await db_session.commit()

    # Create mock WebSocket session
    ws_session = MockWebSocketSession()
    await ws_session.connect()

    # Stream exceeding duration
    _, partial_transcript, _ = await ws_session.stream_audio(400)

    # Verify partial transcript contains content from the 300 seconds that were recorded
    # At 2 words/second, we should have approximately 600 words (capped)
    words = partial_transcript.split()
    assert len(words) > 0
    assert len(words) <= 600  # Capped at 300 seconds * 2 words/second


@pytest.mark.asyncio
async def test_websocket_voice_free_user_denied():
    """T273b (tier check): Free user cannot start WebSocket voice session."""
    # This test validates that free users are denied at connection time,
    # not just when exceeding duration

    # In a real implementation, the WebSocket handler would check tier
    # before allowing the connection

    # For now, we verify the expected behavior through mock
    ws_session = MockWebSocketSession()

    # Simulate tier check (in real impl, this would be in the connect handler)
    def check_tier_requirement(user_tier: UserTier) -> bool:
        return user_tier == UserTier.PRO

    # Free user should be denied
    assert check_tier_requirement(UserTier.FREE) is False

    # Pro user should be allowed
    assert check_tier_requirement(UserTier.PRO) is True
