"""Unit tests for Template API endpoints.

Tests all recurring task template CRUD endpoints with mocked dependencies.
"""

import pytest
from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from fastapi import HTTPException

from src.api.templates import (
    list_templates,
    get_template,
    create_template,
    generate_instance,
    update_template,
    delete_template,
)
from src.services.recurring_service import (
    InvalidRRuleError,
    TemplateNotFoundError,
)


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = uuid4()
    user.tier = "free"
    user.is_pro = False
    return user


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def mock_settings():
    return MagicMock()


# =============================================================================
# LIST TEMPLATES
# =============================================================================


class TestListTemplates:
    @pytest.mark.asyncio
    @patch("src.api.templates.PaginatedResponse")
    @patch("src.api.templates.TemplateResponse")
    @patch("src.api.templates.get_recurring_service")
    async def test_success(
        self, mock_get_service, mock_resp_cls, mock_paginated,
        mock_user, mock_session, mock_settings,
    ):
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        template = MagicMock()
        mock_service.list_templates.return_value = [template]
        mock_resp_cls.from_model.return_value = MagicMock()
        mock_paginated.return_value = MagicMock()

        result = await list_templates(
            offset=0, limit=25, include_inactive=False,
            user=mock_user, session=mock_session, settings=mock_settings,
        )

        mock_service.list_templates.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("src.api.templates.PaginatedResponse")
    @patch("src.api.templates.TemplateResponse")
    @patch("src.api.templates.get_recurring_service")
    async def test_empty(
        self, mock_get_service, mock_resp_cls, mock_paginated,
        mock_user, mock_session, mock_settings,
    ):
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        mock_service.list_templates.return_value = []
        mock_paginated.return_value = MagicMock()

        result = await list_templates(
            offset=0, limit=25, include_inactive=False,
            user=mock_user, session=mock_session, settings=mock_settings,
        )

        assert mock_service.list_templates.await_count == 1


# =============================================================================
# GET TEMPLATE
# =============================================================================


class TestGetTemplate:
    @pytest.mark.asyncio
    @patch("src.api.templates.TemplateResponse")
    @patch("src.api.templates.get_recurring_service")
    async def test_success(
        self, mock_get_service, mock_resp_cls,
        mock_user, mock_session, mock_settings,
    ):
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        template = MagicMock()
        mock_service.get_template.return_value = template
        mock_resp_cls.from_model.return_value = MagicMock()

        tid = uuid4()
        result = await get_template(
            template_id=tid, user=mock_user,
            session=mock_session, settings=mock_settings,
        )

        mock_service.get_template.assert_awaited_once_with(user=mock_user, template_id=tid)

    @pytest.mark.asyncio
    @patch("src.api.templates.get_recurring_service")
    async def test_not_found(
        self, mock_get_service,
        mock_user, mock_session, mock_settings,
    ):
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        mock_service.get_template.side_effect = TemplateNotFoundError("Not found")

        with pytest.raises(HTTPException) as exc_info:
            await get_template(
                template_id=uuid4(), user=mock_user,
                session=mock_session, settings=mock_settings,
            )

        assert exc_info.value.status_code == 404


# =============================================================================
# CREATE TEMPLATE
# =============================================================================


class TestCreateTemplate:
    @pytest.mark.asyncio
    @patch("src.api.templates.TemplateResponse")
    @patch("src.api.templates.get_recurring_service")
    async def test_success(
        self, mock_get_service, mock_resp_cls,
        mock_user, mock_session, mock_settings,
    ):
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        template = MagicMock()
        mock_service.create_template.return_value = template
        mock_resp_cls.from_model.return_value = MagicMock()

        data = MagicMock()
        data.title = "Daily Standup"
        data.description = "Standup meeting"
        data.priority = "medium"
        data.rrule = "FREQ=DAILY"
        data.estimated_duration = 15

        result = await create_template(
            data=data, user=mock_user,
            session=mock_session, settings=mock_settings,
        )

        mock_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("src.api.templates.get_recurring_service")
    async def test_invalid_rrule(
        self, mock_get_service,
        mock_user, mock_session, mock_settings,
    ):
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        error = InvalidRRuleError.__new__(InvalidRRuleError)
        error.message = "Bad RRULE format"
        mock_service.create_template.side_effect = error

        data = MagicMock()
        data.title = "Bad"
        data.description = None
        data.priority = "low"
        data.rrule = "INVALID"
        data.estimated_duration = None

        with pytest.raises(HTTPException) as exc_info:
            await create_template(
                data=data, user=mock_user,
                session=mock_session, settings=mock_settings,
            )

        assert exc_info.value.status_code == 400


# =============================================================================
# GENERATE INSTANCE
# =============================================================================


class TestGenerateInstance:
    @pytest.mark.asyncio
    @patch("src.api.templates.get_recurring_service")
    async def test_success(
        self, mock_get_service,
        mock_user, mock_session, mock_settings,
    ):
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        template = MagicMock()
        mock_service.get_template.return_value = template

        instance = MagicMock()
        instance.id = uuid4()
        instance.title = "Generated Task"
        instance.due_date = datetime.now(UTC)
        mock_service.generate_next_instance.return_value = instance

        tid = uuid4()
        result = await generate_instance(
            template_id=tid, user=mock_user,
            session=mock_session, settings=mock_settings,
        )

        assert result.data.instance_id == instance.id
        mock_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("src.api.templates.get_recurring_service")
    async def test_template_not_found(
        self, mock_get_service,
        mock_user, mock_session, mock_settings,
    ):
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        mock_service.get_template.side_effect = TemplateNotFoundError("Not found")

        with pytest.raises(HTTPException) as exc_info:
            await generate_instance(
                template_id=uuid4(), user=mock_user,
                session=mock_session, settings=mock_settings,
            )

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    @patch("src.api.templates.get_recurring_service")
    async def test_no_instance(
        self, mock_get_service,
        mock_user, mock_session, mock_settings,
    ):
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        mock_service.get_template.return_value = MagicMock()
        mock_service.generate_next_instance.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await generate_instance(
                template_id=uuid4(), user=mock_user,
                session=mock_session, settings=mock_settings,
            )

        assert exc_info.value.status_code == 400


# =============================================================================
# UPDATE TEMPLATE
# =============================================================================


class TestUpdateTemplate:
    @pytest.mark.asyncio
    @patch("src.api.templates.TemplateResponse")
    @patch("src.api.templates.get_recurring_service")
    async def test_success(
        self, mock_get_service, mock_resp_cls,
        mock_user, mock_session, mock_settings,
    ):
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        template = MagicMock()
        mock_service.update_template.return_value = template
        mock_resp_cls.from_model.return_value = MagicMock()

        data = MagicMock()
        data.title = "Updated"
        data.description = None
        data.priority = None
        data.estimated_duration = None
        data.rrule = None
        data.active = None
        data.apply_to_future_only = True

        result = await update_template(
            template_id=uuid4(), data=data, user=mock_user,
            session=mock_session, settings=mock_settings,
        )

        mock_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("src.api.templates.get_recurring_service")
    async def test_not_found(
        self, mock_get_service,
        mock_user, mock_session, mock_settings,
    ):
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        mock_service.update_template.side_effect = TemplateNotFoundError("Not found")

        data = MagicMock()
        data.title = None
        data.description = None
        data.priority = None
        data.estimated_duration = None
        data.rrule = None
        data.active = None
        data.apply_to_future_only = True

        with pytest.raises(HTTPException) as exc_info:
            await update_template(
                template_id=uuid4(), data=data, user=mock_user,
                session=mock_session, settings=mock_settings,
            )

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    @patch("src.api.templates.get_recurring_service")
    async def test_invalid_rrule(
        self, mock_get_service,
        mock_user, mock_session, mock_settings,
    ):
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        error = InvalidRRuleError.__new__(InvalidRRuleError)
        error.message = "Bad RRULE"
        mock_service.update_template.side_effect = error

        data = MagicMock()
        data.title = None
        data.description = None
        data.priority = None
        data.estimated_duration = None
        data.rrule = "INVALID"
        data.active = None
        data.apply_to_future_only = True

        with pytest.raises(HTTPException) as exc_info:
            await update_template(
                template_id=uuid4(), data=data, user=mock_user,
                session=mock_session, settings=mock_settings,
            )

        assert exc_info.value.status_code == 400


# =============================================================================
# DELETE TEMPLATE
# =============================================================================


class TestDeleteTemplate:
    @pytest.mark.asyncio
    @patch("src.api.templates.MessageResponse")
    @patch("src.api.templates.get_recurring_service")
    async def test_success(
        self, mock_get_service, mock_msg_resp,
        mock_user, mock_session, mock_settings,
    ):
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        mock_service.delete_template.return_value = None
        mock_msg_resp.return_value = MagicMock()

        tid = uuid4()
        result = await delete_template(
            template_id=tid, user=mock_user,
            session=mock_session, settings=mock_settings,
        )

        mock_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("src.api.templates.get_recurring_service")
    async def test_not_found(
        self, mock_get_service,
        mock_user, mock_session, mock_settings,
    ):
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        mock_service.delete_template.side_effect = TemplateNotFoundError("Not found")

        with pytest.raises(HTTPException) as exc_info:
            await delete_template(
                template_id=uuid4(), user=mock_user,
                session=mock_session, settings=mock_settings,
            )

        assert exc_info.value.status_code == 404
