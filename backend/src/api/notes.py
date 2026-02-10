"""Note API endpoints.

Phase 7: User Story 5 - Notes with Voice Recording (Priority: P2)
Implements api-specification.md Section 6.

T171: Implement GET /api/v1/notes
T172: Implement POST /api/v1/notes
T173: Implement PATCH /api/v1/notes/:id
T174: Implement DELETE /api/v1/notes/:id

Phase 12: User Story 5 Extended - Note to Task Conversion (Priority: P3)
Implements FR-032.

T259: Implement POST /api/v1/notes/:id/convert
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
from src.dependencies import (
    get_current_user,
    get_db_session,
    get_settings,
)
from src.models.user import User
from src.schemas.common import (
    DataResponse,
    PaginatedResponse,
    PaginationMeta,
)
from src.schemas.note import (
    NoteConvertResponse,
    NoteCreate,
    NoteResponse,
    NoteUpdate,
)
from src.services.ai_service import (
    AIService,
    AIServiceError,
    AIServiceUnavailableError,
    InsufficientCreditsError,
)
from src.services.note_service import (
    NoteArchivedError,
    NoteLimitExceededError,
    NoteNotFoundError,
    NoteService,
    VoiceNoteProRequiredError,
)


router = APIRouter(prefix="/notes", tags=["notes"])


# =============================================================================
# DEPENDENCIES
# =============================================================================


def get_note_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> NoteService:
    """Get NoteService instance."""
    return NoteService(session, settings)


def get_ai_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AIService:
    """Get AIService instance for note conversion."""
    return AIService(session, settings)


# =============================================================================
# T171: GET /api/v1/notes - List Notes
# =============================================================================


@router.get(
    "",
    response_model=PaginatedResponse[NoteResponse],
    summary="List Notes",
    description="Get all notes for the authenticated user with pagination.",
)
async def list_notes(
    current_user: Annotated[User, Depends(get_current_user)],
    note_service: Annotated[NoteService, Depends(get_note_service)],
    archived: bool = Query(default=False, description="Include archived notes"),
    offset: int = Query(default=0, ge=0, description="Pagination offset"),
    limit: int = Query(default=25, ge=1, le=100, description="Items per page"),
) -> PaginatedResponse[NoteResponse]:
    """List all notes for the current user.

    Per api-specification.md Section 6.1.
    """
    notes, total = await note_service.list_notes(
        user=current_user,
        offset=offset,
        limit=limit,
        archived=archived,
    )

    return PaginatedResponse(
        data=[NoteResponse.model_validate(n) for n in notes],
        pagination=PaginationMeta(
            offset=offset,
            limit=limit,
            total=total,
            has_more=offset + len(notes) < total,
        ),
    )


# =============================================================================
# T172: POST /api/v1/notes - Create Note
# =============================================================================


@router.post(
    "",
    response_model=DataResponse[NoteResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Note",
    description="Create a new note. Voice notes require Pro tier.",
)
async def create_note(
    data: NoteCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    note_service: Annotated[NoteService, Depends(get_note_service)],
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key")],
) -> DataResponse[NoteResponse]:
    """Create a new note.

    Per api-specification.md Section 6.2.

    - Free users: Text notes only, max 10 notes
    - Pro users: Text and voice notes, max 25 notes
    - Voice duration: Max 300 seconds
    """
    try:
        note = await note_service.create_note(user=current_user, data=data)
        return DataResponse(data=NoteResponse.model_validate(note))

    except VoiceNoteProRequiredError as e:
        from src.middleware.error_handler import ForbiddenError
        raise ForbiddenError(
            message=str(e),
            required_tier="pro",
            current_tier="free",
        )
    except NoteLimitExceededError as e:
        from src.middleware.error_handler import LimitExceededError
        raise LimitExceededError(message=str(e))


# =============================================================================
# GET /api/v1/notes/:id - Get Note by ID
# =============================================================================


@router.get(
    "/{note_id}",
    response_model=DataResponse[NoteResponse],
    summary="Get Note",
    description="Get a specific note by ID.",
)
async def get_note(
    note_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    note_service: Annotated[NoteService, Depends(get_note_service)],
) -> DataResponse[NoteResponse]:
    """Get a note by ID.

    Returns 404 if note not found or user doesn't own it.
    """
    try:
        note = await note_service.get_note(
            user=current_user,
            note_id=note_id,
            include_archived=True,
        )
        return DataResponse(data=NoteResponse.model_validate(note))

    except NoteNotFoundError as e:
        from src.middleware.error_handler import NotFoundError
        raise NotFoundError(message=str(e))


# =============================================================================
# T173: PATCH /api/v1/notes/:id - Update Note
# =============================================================================


@router.patch(
    "/{note_id}",
    response_model=DataResponse[NoteResponse],
    summary="Update Note",
    description="Update a note's content.",
)
async def update_note(
    note_id: UUID,
    data: NoteUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    note_service: Annotated[NoteService, Depends(get_note_service)],
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key")],
) -> DataResponse[NoteResponse]:
    """Update a note.

    Cannot update archived notes.
    """
    try:
        note = await note_service.update_note(
            user=current_user,
            note_id=note_id,
            data=data,
        )
        return DataResponse(data=NoteResponse.model_validate(note))

    except NoteNotFoundError as e:
        from src.middleware.error_handler import NotFoundError
        raise NotFoundError(message=str(e))
    except NoteArchivedError as e:
        from src.middleware.error_handler import ConflictError
        raise ConflictError(message=str(e), code="ARCHIVED")


# =============================================================================
# T174: DELETE /api/v1/notes/:id - Delete Note
# =============================================================================


@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Note",
    description="Delete a note permanently.",
)
async def delete_note(
    note_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    note_service: Annotated[NoteService, Depends(get_note_service)],
) -> None:
    """Delete a note.

    Returns 404 if note not found or user doesn't own it.
    """
    try:
        await note_service.delete_note(user=current_user, note_id=note_id)

    except NoteNotFoundError as e:
        from src.middleware.error_handler import NotFoundError
        raise NotFoundError(message=str(e))


# =============================================================================
# T259: POST /api/v1/notes/:id/convert - Convert Note to Task
# =============================================================================


@router.post(
    "/{note_id}/convert",
    response_model=DataResponse[NoteConvertResponse],
    summary="Convert Note to Task",
    description="""
    Use AI to convert a note into a task suggestion (FR-032).

    The AI analyzes the note content and suggests:
    - Task title and description
    - Priority level
    - Due date (if extractable from note)
    - Subtasks (if the note mentions multiple steps)

    **Cost:** 1 AI credit per conversion.

    **Note:** This endpoint returns a *suggestion*. The note is NOT automatically
    archived. To complete the conversion flow:
    1. Call this endpoint to get the suggestion
    2. Create the task using POST /api/v1/tasks with the suggested data
    3. Archive the note using PATCH /api/v1/notes/:id to mark it as archived

    **Errors:**
    - 402: Insufficient AI credits
    - 404: Note not found
    - 409: Note is already archived
    - 503: AI service unavailable
    """,
    responses={
        200: {"description": "Task suggestion generated successfully"},
        402: {"description": "Insufficient AI credits"},
        404: {"description": "Note not found"},
        409: {"description": "Note is already archived"},
        503: {"description": "AI service unavailable"},
    },
)
async def convert_note_to_task(
    note_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    ai_service: Annotated[AIService, Depends(get_ai_service)],
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key")],
) -> DataResponse[NoteConvertResponse]:
    """Convert a note to a task suggestion using AI.

    T259: Implement POST /api/v1/notes/:id/convert per api-specification.md Section 5.3.

    Consumes 1 AI credit. Returns a task suggestion that the user can
    review before creating the actual task.
    """
    from src.middleware.error_handler import (
        AIServiceUnavailableError as AIServiceHTTPError,
        ConflictError,
        InsufficientCreditsError as InsufficientCreditsHTTPError,
        NotFoundError,
    )

    try:
        result = await ai_service.convert_note_to_task(
            user=current_user,
            note_id=note_id,
        )
        return DataResponse(data=result)

    except InsufficientCreditsError as e:
        raise InsufficientCreditsHTTPError(message=str(e))
    except AIServiceError as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            raise NotFoundError(message=str(e))
        elif "archived" in error_msg:
            raise ConflictError(message=str(e), code="NOTE_ARCHIVED")
        else:
            raise AIServiceHTTPError(message=str(e))
    except AIServiceUnavailableError as e:
        raise AIServiceHTTPError(
            message="AI service is temporarily unavailable. Please try again later."
        )
