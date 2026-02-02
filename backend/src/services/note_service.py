"""Note service for note CRUD operations.

Phase 7: User Story 5 - Notes with Voice Recording (Priority: P2)
Implements FR-022 to FR-024.

T165: NoteService.create_note with tier limits
T166: NoteService.get_note with ownership check
T167: NoteService.list_notes with pagination
T168: NoteService.update_note
T169: NoteService.delete_note
T170: effective_note_limit with achievement perks
"""

import logging
from datetime import datetime, UTC
from typing import Sequence
from uuid import UUID, uuid4

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.config import Settings
from src.models.note import Note
from src.models.user import User
from src.schemas.note import NoteCreate, NoteUpdate
from src.schemas.enums import TranscriptionStatus

# Import centralized limit utilities (T170)
from src.lib.limits import get_effective_note_limit

# Import metrics (T176)
from src.middleware.metrics import (
    record_note_operation,
    record_note_limit_reached,
    record_voice_note_operation,
    record_voice_note_duration,
)


logger = logging.getLogger(__name__)


# =============================================================================
# EXCEPTIONS
# =============================================================================


class NoteServiceError(Exception):
    """Base exception for note service errors."""

    pass


class NoteNotFoundError(NoteServiceError):
    """Raised when note is not found or user doesn't have access."""

    pass


class NoteLimitExceededError(NoteServiceError):
    """Raised when user has reached their note limit (409)."""

    pass


class VoiceNoteProRequiredError(NoteServiceError):
    """Raised when free user tries to create voice note (403)."""

    pass


class NoteArchivedError(NoteServiceError):
    """Raised when trying to modify an archived note."""

    pass


# =============================================================================
# NOTE SERVICE
# =============================================================================


class NoteService:
    """Service for note operations.

    Handles:
    - Note CRUD with tier-based validation
    - Note limits (10 free / 25 pro)
    - Voice note Pro-only enforcement
    - Archive status management
    """

    def __init__(self, session: AsyncSession, settings: Settings):
        self.session = session
        self.settings = settings

    # =========================================================================
    # NOTE CRUD (T165-T169)
    # =========================================================================

    async def create_note(self, user: User, data: NoteCreate) -> Note:
        """Create a new note with tier-based validation.

        T165: NoteService.create_note with tier limits (FR-022)

        Args:
            user: The note owner
            data: Note creation data

        Returns:
            The created Note

        Raises:
            NoteLimitExceededError: If user has reached note limit (FR-022)
            VoiceNoteProRequiredError: If free user tries voice note (FR-024)
        """
        # Check if this is a voice note
        is_voice_note = data.voice_url is not None

        # FR-024: Voice notes require Pro tier
        if is_voice_note and not user.is_pro:
            raise VoiceNoteProRequiredError(
                "Voice notes require Pro tier subscription"
            )

        # FR-022: Check note limit based on tier
        # T170: Uses get_effective_note_limit which includes achievement perks
        current_count = await self._get_user_note_count(user.id)
        max_notes = get_effective_note_limit(user.tier)

        if current_count >= max_notes:
            # T176: Record limit reached metric
            record_note_limit_reached(user.tier.value)
            raise NoteLimitExceededError(
                f"Note limit of {max_notes} reached for "
                f"{'Pro' if user.is_pro else 'Free'} tier"
            )

        # Create the note
        note = Note(
            id=uuid4(),
            user_id=user.id,
            content=data.content.strip(),
            archived=False,
            voice_url=data.voice_url,
            voice_duration_seconds=data.voice_duration_seconds,
            # transcription_status will be set by voice transcription flow
            transcription_status=None,
        )

        self.session.add(note)
        await self.session.flush()
        await self.session.refresh(note)

        # T176: Record metrics
        note_type = "voice" if is_voice_note else "text"
        record_note_operation("create", user.tier.value, note_type)

        if is_voice_note and data.voice_duration_seconds:
            record_voice_note_operation("create")
            record_voice_note_duration(data.voice_duration_seconds)

        return note

    async def get_note(
        self,
        user: User,
        note_id: UUID,
        include_archived: bool = False,
    ) -> Note:
        """Get a note by ID with ownership check.

        T166: NoteService.get_note with ownership check

        Args:
            user: The requesting user
            note_id: The note ID to retrieve
            include_archived: Include archived notes

        Returns:
            The Note

        Raises:
            NoteNotFoundError: If note not found or user doesn't own it
        """
        query = select(Note).where(
            Note.id == note_id,
            Note.user_id == user.id,
        )

        if not include_archived:
            query = query.where(Note.archived == False)

        result = await self.session.execute(query)
        note = result.scalar_one_or_none()

        if note is None:
            raise NoteNotFoundError(f"Note {note_id} not found")

        return note

    async def list_notes(
        self,
        user: User,
        offset: int = 0,
        limit: int = 25,
        archived: bool = False,
    ) -> tuple[Sequence[Note], int]:
        """List notes with pagination and filters.

        T167: NoteService.list_notes with pagination

        Args:
            user: The requesting user
            offset: Pagination offset
            limit: Items per page (max 100)
            archived: Include archived notes

        Returns:
            Tuple of (notes, total_count)
        """
        # Build base query
        query = select(Note).where(Note.user_id == user.id)

        # Apply archived filter
        if not archived:
            query = query.where(Note.archived == False)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        # Apply pagination and ordering (newest first)
        query = (
            query.order_by(Note.created_at.desc())
            .offset(offset)
            .limit(min(limit, 100))
        )

        result = await self.session.execute(query)
        notes = result.scalars().all()

        return notes, total

    async def update_note(
        self,
        user: User,
        note_id: UUID,
        data: NoteUpdate,
    ) -> Note:
        """Update a note.

        T168: NoteService.update_note

        Args:
            user: The requesting user
            note_id: The note ID to update
            data: Update data

        Returns:
            The updated Note

        Raises:
            NoteNotFoundError: If note not found
            NoteArchivedError: If note is archived
        """
        note = await self.get_note(user=user, note_id=note_id, include_archived=True)

        # Cannot update archived notes
        if note.archived:
            raise NoteArchivedError("Cannot modify archived note")

        # Apply updates
        if data.content is not None:
            note.content = data.content.strip()

        self.session.add(note)
        await self.session.flush()
        await self.session.refresh(note)

        return note

    async def delete_note(self, user: User, note_id: UUID) -> None:
        """Delete a note.

        T169: NoteService.delete_note

        Args:
            user: The requesting user
            note_id: The note ID to delete

        Raises:
            NoteNotFoundError: If note not found
        """
        note = await self.get_note(user=user, note_id=note_id, include_archived=True)

        await self.session.delete(note)
        await self.session.flush()

    async def archive_note(self, user: User, note_id: UUID) -> Note:
        """Archive a note (typically after task conversion).

        Args:
            user: The requesting user
            note_id: The note ID to archive

        Returns:
            The archived Note
        """
        note = await self.get_note(user=user, note_id=note_id)

        note.archived = True

        self.session.add(note)
        await self.session.flush()
        await self.session.refresh(note)

        return note

    # =========================================================================
    # TRANSCRIPTION STATUS TRACKING (T269)
    # =========================================================================

    async def set_transcription_pending(
        self,
        user: User,
        note_id: UUID,
    ) -> Note:
        """Set note transcription status to pending.

        T269: Implement transcription status tracking

        Args:
            user: The requesting user
            note_id: The note ID

        Returns:
            The updated Note
        """
        return await self._update_transcription_status(
            user=user,
            note_id=note_id,
            status=TranscriptionStatus.PENDING,
        )

    async def set_transcription_completed(
        self,
        user: User,
        note_id: UUID,
        transcription_text: str,
    ) -> Note:
        """Set note transcription status to completed and update content.

        T269: Implement transcription status tracking

        Args:
            user: The requesting user
            note_id: The note ID
            transcription_text: The transcribed text to set as content

        Returns:
            The updated Note
        """
        note = await self.get_note(user=user, note_id=note_id, include_archived=True)

        note.transcription_status = TranscriptionStatus.COMPLETED
        # Update content with transcription text
        if transcription_text:
            note.content = transcription_text

        self.session.add(note)
        await self.session.flush()
        await self.session.refresh(note)

        # Record metric
        record_voice_note_operation("transcribe")

        return note

    async def set_transcription_failed(
        self,
        user: User,
        note_id: UUID,
    ) -> Note:
        """Set note transcription status to failed.

        T269: Implement transcription status tracking

        Args:
            user: The requesting user
            note_id: The note ID

        Returns:
            The updated Note
        """
        return await self._update_transcription_status(
            user=user,
            note_id=note_id,
            status=TranscriptionStatus.FAILED,
        )

    async def _update_transcription_status(
        self,
        user: User,
        note_id: UUID,
        status: TranscriptionStatus,
    ) -> Note:
        """Update transcription status for a note.

        Args:
            user: The requesting user
            note_id: The note ID
            status: New transcription status

        Returns:
            The updated Note
        """
        note = await self.get_note(user=user, note_id=note_id, include_archived=True)

        note.transcription_status = status

        self.session.add(note)
        await self.session.flush()
        await self.session.refresh(note)

        return note

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    async def _get_user_note_count(self, user_id: UUID) -> int:
        """Get count of user's active (non-archived) notes."""
        query = select(func.count()).where(
            Note.user_id == user_id,
            Note.archived == False,
        )
        result = await self.session.execute(query)
        return result.scalar() or 0


# =============================================================================
# FACTORY FUNCTION
# =============================================================================


def get_note_service(session: AsyncSession, settings: Settings) -> NoteService:
    """Get a NoteService instance."""
    return NoteService(session, settings)
