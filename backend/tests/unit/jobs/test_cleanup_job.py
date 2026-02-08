"""Unit tests for activity log cleanup job.

T360: 30-day retention cleanup job (FR-053)
"""

from datetime import datetime, timedelta, UTC
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.jobs.tasks.cleanup_job import handle_activity_cleanup, RETENTION_DAYS


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def mock_settings():
    return MagicMock()


class TestHandleActivityCleanup:
    """Test activity log cleanup handler."""

    @pytest.mark.asyncio
    async def test_returns_success_when_no_entries(self, mock_session, mock_settings):
        """Should return success with 0 deleted when nothing to clean."""
        count_result = MagicMock()
        count_result.scalar.return_value = 0
        mock_session.execute.return_value = count_result

        result = await handle_activity_cleanup({}, mock_session, mock_settings)

        assert result["status"] == "success"
        assert result["entries_deleted"] == 0

    @pytest.mark.asyncio
    async def test_deletes_old_entries(self, mock_session, mock_settings):
        """Should delete entries older than retention period."""
        # First call: count query returns 5
        count_result = MagicMock()
        count_result.scalar.return_value = 5

        # Second call: batch query returns IDs
        batch_result = MagicMock()
        batch_result.all.return_value = [
            (uuid4(),) for _ in range(5)
        ]

        # Third call: delete operation
        delete_result = MagicMock()

        # Fourth call: next batch returns empty (done)
        empty_result = MagicMock()
        empty_result.all.return_value = []

        mock_session.execute = AsyncMock(
            side_effect=[count_result, batch_result, delete_result, empty_result]
        )

        result = await handle_activity_cleanup({}, mock_session, mock_settings)

        assert result["status"] == "success"
        assert result["entries_deleted"] == 5

    @pytest.mark.asyncio
    async def test_uses_custom_retention_days(self, mock_session, mock_settings):
        """Should use custom retention_days from payload."""
        count_result = MagicMock()
        count_result.scalar.return_value = 0
        mock_session.execute.return_value = count_result

        result = await handle_activity_cleanup(
            {"retention_days": 60}, mock_session, mock_settings
        )

        assert result["retention_days"] == 60

    @pytest.mark.asyncio
    async def test_uses_default_retention_days(self, mock_session, mock_settings):
        """Should use default 30-day retention when not specified."""
        count_result = MagicMock()
        count_result.scalar.return_value = 0
        mock_session.execute.return_value = count_result

        result = await handle_activity_cleanup({}, mock_session, mock_settings)

        assert result["retention_days"] == RETENTION_DAYS

    @pytest.mark.asyncio
    async def test_handles_db_error(self, mock_session, mock_settings):
        """Should return error status on database failure."""
        mock_session.execute = AsyncMock(side_effect=Exception("DB connection failed"))

        result = await handle_activity_cleanup({}, mock_session, mock_settings)

        assert result["status"] == "error"
        assert "DB connection failed" in result["error"]

    @pytest.mark.asyncio
    async def test_cutoff_date_in_result(self, mock_session, mock_settings):
        """Result should include the cutoff date."""
        count_result = MagicMock()
        count_result.scalar.return_value = 0
        mock_session.execute.return_value = count_result

        result = await handle_activity_cleanup({}, mock_session, mock_settings)

        assert "cutoff_date" in result
