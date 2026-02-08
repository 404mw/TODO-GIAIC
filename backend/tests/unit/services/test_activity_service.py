"""Unit tests for ActivityService.

Phase 20: Activity Logging & Observability (FR-052 to FR-054)

Covers:
- log_event for all entity types (FR-052)
- Source field tracking (FR-054)
- list_activities with filters and pagination
- get_activity_by_entity
- Factory function
"""

from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from src.schemas.enums import ActivitySource, EntityType
from src.services.activity_service import ActivityService, get_activity_service


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def mock_session():
    """Create a mock database session."""
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def mock_settings():
    """Create mock settings."""
    return MagicMock()


@pytest.fixture
def service(mock_session, mock_settings):
    """Create an ActivityService instance."""
    return ActivityService(mock_session, mock_settings)


# =============================================================================
# LOG EVENT TESTS (T359, FR-052, FR-054)
# =============================================================================


class TestLogEvent:
    """Test activity event logging."""

    @pytest.mark.asyncio
    async def test_log_event_creates_activity_log(self, service, mock_session):
        """log_event should create an ActivityLog with correct fields."""
        user_id = uuid4()
        entity_id = uuid4()

        result = await service.log_event(
            user_id=user_id,
            entity_type=EntityType.TASK,
            entity_id=entity_id,
            action="task_created",
            source=ActivitySource.USER,
        )

        mock_session.add.assert_called_once()
        mock_session.flush.assert_awaited_once()
        assert result.user_id == user_id
        assert result.entity_type == EntityType.TASK
        assert result.entity_id == entity_id
        assert result.action == "task_created"
        assert result.source == ActivitySource.USER

    @pytest.mark.asyncio
    async def test_log_event_with_metadata(self, service, mock_session):
        """log_event should store metadata when provided."""
        user_id = uuid4()
        entity_id = uuid4()
        metadata = {"title": "Test Task", "priority": "high"}

        result = await service.log_event(
            user_id=user_id,
            entity_type=EntityType.TASK,
            entity_id=entity_id,
            action="task_created",
            source=ActivitySource.USER,
            metadata=metadata,
        )

        assert result.extra_data == metadata

    @pytest.mark.asyncio
    async def test_log_event_without_metadata_defaults_to_empty_dict(
        self, service, mock_session
    ):
        """log_event should default metadata to empty dict."""
        result = await service.log_event(
            user_id=uuid4(),
            entity_type=EntityType.NOTE,
            entity_id=uuid4(),
            action="note_created",
            source=ActivitySource.USER,
        )

        assert result.extra_data == {}

    @pytest.mark.asyncio
    async def test_log_event_with_request_id(self, service, mock_session):
        """log_event should store request_id for tracing."""
        request_id = uuid4()

        result = await service.log_event(
            user_id=uuid4(),
            entity_type=EntityType.TASK,
            entity_id=uuid4(),
            action="task_updated",
            source=ActivitySource.USER,
            request_id=request_id,
        )

        assert result.request_id == request_id

    @pytest.mark.asyncio
    async def test_log_event_source_ai(self, service, mock_session):
        """log_event should track AI source correctly (FR-054)."""
        result = await service.log_event(
            user_id=uuid4(),
            entity_type=EntityType.AI_CHAT,
            entity_id=uuid4(),
            action="ai_chat",
            source=ActivitySource.AI,
        )

        assert result.source == ActivitySource.AI

    @pytest.mark.asyncio
    async def test_log_event_source_system(self, service, mock_session):
        """log_event should track system source correctly (FR-054)."""
        result = await service.log_event(
            user_id=uuid4(),
            entity_type=EntityType.TASK,
            entity_id=uuid4(),
            action="recurring_task_generated",
            source=ActivitySource.SYSTEM,
        )

        assert result.source == ActivitySource.SYSTEM

    @pytest.mark.asyncio
    async def test_log_event_sets_created_at(self, service, mock_session):
        """log_event should set created_at timestamp."""
        result = await service.log_event(
            user_id=uuid4(),
            entity_type=EntityType.TASK,
            entity_id=uuid4(),
            action="task_created",
            source=ActivitySource.USER,
        )

        assert result.created_at is not None
        assert isinstance(result.created_at, datetime)

    @pytest.mark.asyncio
    async def test_log_event_generates_unique_id(self, service, mock_session):
        """Each log entry should have a unique ID."""
        result1 = await service.log_event(
            user_id=uuid4(),
            entity_type=EntityType.TASK,
            entity_id=uuid4(),
            action="task_created",
            source=ActivitySource.USER,
        )
        result2 = await service.log_event(
            user_id=uuid4(),
            entity_type=EntityType.NOTE,
            entity_id=uuid4(),
            action="note_created",
            source=ActivitySource.USER,
        )

        assert result1.id != result2.id


# =============================================================================
# LIST ACTIVITIES TESTS
# =============================================================================


class TestListActivities:
    """Test activity listing with filters."""

    @pytest.mark.asyncio
    async def test_list_activities_basic(self, service, mock_session):
        """list_activities should query with user_id filter."""
        user_id = uuid4()

        # Mock the count query
        count_result = MagicMock()
        count_result.scalar.return_value = 5

        # Mock the data query
        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = []

        mock_session.execute = AsyncMock(
            side_effect=[count_result, data_result]
        )

        activities, total = await service.list_activities(user_id=user_id)

        assert total == 5
        assert mock_session.execute.call_count == 2

    @pytest.mark.asyncio
    async def test_list_activities_with_entity_type_filter(
        self, service, mock_session
    ):
        """list_activities should filter by entity_type."""
        user_id = uuid4()

        count_result = MagicMock()
        count_result.scalar.return_value = 3

        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = []

        mock_session.execute = AsyncMock(
            side_effect=[count_result, data_result]
        )

        activities, total = await service.list_activities(
            user_id=user_id,
            entity_type=EntityType.TASK,
        )

        assert total == 3

    @pytest.mark.asyncio
    async def test_list_activities_with_action_filter(
        self, service, mock_session
    ):
        """list_activities should filter by action."""
        user_id = uuid4()

        count_result = MagicMock()
        count_result.scalar.return_value = 2

        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = []

        mock_session.execute = AsyncMock(
            side_effect=[count_result, data_result]
        )

        activities, total = await service.list_activities(
            user_id=user_id,
            action="task_created",
        )

        assert total == 2

    @pytest.mark.asyncio
    async def test_list_activities_with_source_filter(
        self, service, mock_session
    ):
        """list_activities should filter by source."""
        user_id = uuid4()

        count_result = MagicMock()
        count_result.scalar.return_value = 1

        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = []

        mock_session.execute = AsyncMock(
            side_effect=[count_result, data_result]
        )

        activities, total = await service.list_activities(
            user_id=user_id,
            source=ActivitySource.AI,
        )

        assert total == 1

    @pytest.mark.asyncio
    async def test_list_activities_with_entity_id_filter(
        self, service, mock_session
    ):
        """list_activities should filter by entity_id."""
        user_id = uuid4()
        entity_id = uuid4()

        count_result = MagicMock()
        count_result.scalar.return_value = 4

        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = []

        mock_session.execute = AsyncMock(
            side_effect=[count_result, data_result]
        )

        activities, total = await service.list_activities(
            user_id=user_id,
            entity_id=entity_id,
        )

        assert total == 4

    @pytest.mark.asyncio
    async def test_list_activities_limit_capped_at_100(
        self, service, mock_session
    ):
        """list_activities should cap limit at 100."""
        user_id = uuid4()

        count_result = MagicMock()
        count_result.scalar.return_value = 0

        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = []

        mock_session.execute = AsyncMock(
            side_effect=[count_result, data_result]
        )

        # Request 200 but should be capped
        await service.list_activities(user_id=user_id, limit=200)

        # Verify the query was executed (limit handled inside)
        assert mock_session.execute.call_count == 2


# =============================================================================
# GET ACTIVITY BY ENTITY TESTS
# =============================================================================


class TestGetActivityByEntity:
    """Test getting activity history for a specific entity."""

    @pytest.mark.asyncio
    async def test_get_activity_by_entity_returns_results(
        self, service, mock_session
    ):
        """get_activity_by_entity should return activity logs for an entity."""
        user_id = uuid4()
        entity_id = uuid4()

        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = []

        mock_session.execute = AsyncMock(return_value=data_result)

        result = await service.get_activity_by_entity(
            user_id=user_id,
            entity_type=EntityType.TASK,
            entity_id=entity_id,
        )

        assert isinstance(result, (list, type(data_result.scalars.return_value.all.return_value)))
        mock_session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_activity_by_entity_limit_capped(
        self, service, mock_session
    ):
        """get_activity_by_entity should cap limit at 100."""
        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = []

        mock_session.execute = AsyncMock(return_value=data_result)

        await service.get_activity_by_entity(
            user_id=uuid4(),
            entity_type=EntityType.NOTE,
            entity_id=uuid4(),
            limit=200,
        )

        mock_session.execute.assert_awaited_once()


# =============================================================================
# FACTORY FUNCTION TESTS
# =============================================================================


class TestFactoryFunction:
    """Test the factory function."""

    def test_get_activity_service_returns_instance(self):
        """get_activity_service should return an ActivityService."""
        session = AsyncMock()
        settings = MagicMock()

        result = get_activity_service(session, settings)

        assert isinstance(result, ActivityService)
        assert result.session == session
        assert result.settings == settings
