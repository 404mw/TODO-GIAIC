"""API endpoints for recurring task templates.

Phase 6: User Story 3 - Recurring Task Templates (FR-015 to FR-018)

T153-T156: Template CRUD endpoints.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings, get_settings
from src.dependencies import get_current_user, get_db_session
from src.models.user import User
from src.schemas.common import (
    DataResponse,
    DeleteResponse,
    ErrorResponse,
    PaginatedResponse,
    PaginationMeta,
)
from src.schemas.template import (
    GenerateInstanceResponse,
    TemplateCreate,
    TemplateListResponse,
    TemplateResponse,
    TemplateUpdate,
)
from src.services.recurring_service import (
    InvalidRRuleError,
    RecurringTaskService,
    TemplateNotFoundError,
    get_recurring_service,
)


router = APIRouter(prefix="/templates", tags=["templates"])


# =============================================================================
# GET ENDPOINTS (T153)
# =============================================================================


@router.get(
    "",
    response_model=PaginatedResponse[TemplateResponse],
    summary="List recurring task templates",
    description="List all recurring task templates for the authenticated user.",
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
    },
)
async def list_templates(
    offset: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(25, ge=1, le=100, description="Items per page"),
    include_inactive: bool = Query(False, description="Include inactive templates"),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> PaginatedResponse[TemplateResponse]:
    """T153: GET /api/v1/templates - List templates."""
    service = get_recurring_service(session, settings)

    templates = await service.list_templates(
        user=user,
        include_inactive=include_inactive,
        offset=offset,
        limit=limit,
    )

    items = [TemplateResponse.from_model(t) for t in templates]

    return PaginatedResponse(
        data=items,
        meta=PaginationMeta(
            offset=offset,
            limit=limit,
            total=len(items),  # Note: This should be actual total from DB
            has_more=len(items) == limit,
        ),
    )


@router.get(
    "/{template_id}",
    response_model=DataResponse[TemplateResponse],
    summary="Get a recurring task template",
    description="Get details of a specific recurring task template.",
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Template not found"},
    },
)
async def get_template(
    template_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> DataResponse[TemplateResponse]:
    """T153: GET /api/v1/templates/:id - Get single template."""
    service = get_recurring_service(session, settings)

    try:
        template = await service.get_template(user=user, template_id=template_id)
    except TemplateNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template {template_id} not found",
        )

    return DataResponse(data=TemplateResponse.from_model(template))


# =============================================================================
# POST ENDPOINTS (T154)
# =============================================================================


@router.post(
    "",
    response_model=DataResponse[TemplateResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a recurring task template",
    description="Create a new recurring task template with an RRULE.",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid RRULE format"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
    },
)
async def create_template(
    data: TemplateCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> DataResponse[TemplateResponse]:
    """T154: POST /api/v1/templates - Create template."""
    service = get_recurring_service(session, settings)

    try:
        template = await service.create_template(
            user=user,
            title=data.title,
            description=data.description,
            priority=data.priority,
            rrule=data.rrule,
            estimated_duration=data.estimated_duration,
        )
    except InvalidRRuleError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid RRULE: {e.message}",
        )

    await session.commit()

    return DataResponse(data=TemplateResponse.from_model(template))


@router.post(
    "/{template_id}/generate",
    response_model=DataResponse[GenerateInstanceResponse],
    summary="Manually generate next instance",
    description="Manually trigger generation of the next task instance from a template.",
    responses={
        400: {"model": ErrorResponse, "description": "Template inactive or exhausted"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Template not found"},
    },
)
async def generate_instance(
    template_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> DataResponse[GenerateInstanceResponse]:
    """Manually generate the next instance from a template."""
    service = get_recurring_service(session, settings)

    try:
        template = await service.get_template(user=user, template_id=template_id)
    except TemplateNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template {template_id} not found",
        )

    instance = await service.generate_next_instance(template)

    if instance is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Template is inactive or has no more occurrences",
        )

    await session.commit()

    return DataResponse(
        data=GenerateInstanceResponse(
            template_id=template_id,
            instance_id=instance.id,
            title=instance.title,
            due_date=instance.due_date,
            message="Instance generated successfully",
        )
    )


# =============================================================================
# PATCH ENDPOINTS (T155)
# =============================================================================


@router.patch(
    "/{template_id}",
    response_model=DataResponse[TemplateResponse],
    summary="Update a recurring task template",
    description="Update a recurring task template. Changes only affect future instances by default (FR-018).",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid RRULE format"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Template not found"},
    },
)
async def update_template(
    template_id: UUID,
    data: TemplateUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> DataResponse[TemplateResponse]:
    """T155: PATCH /api/v1/templates/:id - Update template."""
    service = get_recurring_service(session, settings)

    try:
        template = await service.update_template(
            user=user,
            template_id=template_id,
            title=data.title,
            description=data.description,
            priority=data.priority,
            estimated_duration=data.estimated_duration,
            rrule=data.rrule,
            active=data.active,
            apply_to_future_only=data.apply_to_future_only,
        )
    except TemplateNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template {template_id} not found",
        )
    except InvalidRRuleError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid RRULE: {e.message}",
        )

    await session.commit()

    return DataResponse(data=TemplateResponse.from_model(template))


# =============================================================================
# DELETE ENDPOINTS (T156)
# =============================================================================


@router.delete(
    "/{template_id}",
    response_model=DeleteResponse,
    summary="Delete a recurring task template",
    description="Delete a recurring task template. Existing instances are preserved as standalone tasks.",
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Template not found"},
    },
)
async def delete_template(
    template_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> DeleteResponse:
    """T156: DELETE /api/v1/templates/:id - Delete template."""
    service = get_recurring_service(session, settings)

    try:
        await service.delete_template(user=user, template_id=template_id)
    except TemplateNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template {template_id} not found",
        )

    await session.commit()

    return DeleteResponse(
        message=f"Template {template_id} deleted successfully",
        deleted_id=template_id,
    )
