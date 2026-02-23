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
import math
from datetime import datetime, UTC
from typing import Sequence
from uuid import UUID, uuid4

from fastapi import BackgroundTasks
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.config import Settings
from src.models.note import Note
from src.models.tombstone import DeletionTombstone
from src.models.user import User
from src.schemas.note import NoteCreate, NoteUpdate
from src.schemas.enums import TombstoneEntityType, TranscriptionStatus

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
    """Raised when user has reached their note limit (402)."""

    pass


class VoiceNoteProRequiredError(NoteServiceError):
    """Raised when free user tries to create voice note (403)."""

    pass


class NoteArchivedError(NoteServiceError):
    """Raised when trying to modify an archived note."""

    pass


class VoiceNoteInsufficientCreditsError(NoteServiceError):
    """Raised when user has insufficient AI credits for voice transcription (402)."""

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

    async def create_note(
        self,
        user: User,
        data: NoteCreate,
        background_tasks: BackgroundTasks | None = None,
    ) -> Note:
        """Create a new note with tier-based validation.

        T165: NoteService.create_note with tier limits (FR-022)
        Task 3.7d: Credits deducted at creation; transcription_status=PENDING; bg task enqueued.

        Args:
            user: The note owner
            data: Note creation data
            background_tasks: FastAPI BackgroundTasks for async transcription

        Returns:
            The created Note

        Raises:
            NoteLimitExceededError: If user has reached note limit (FR-022)
            VoiceNoteProRequiredError: If free user tries voice note (FR-024)
            VoiceNoteInsufficientCreditsError: If insufficient credits for transcription (FR-006)
        """
        # Check if this is a voice note
        is_voice_note = data.voice_url is not None

        # FR-024: Voice notes require Pro tier
        if is_voice_note and not user.is_pro:
            raise VoiceNoteProRequiredError(
                "Voice notes require Pro tier subscription"
            )

        # FR-006: Deduct AI credits for voice transcription at creation time
        if is_voice_note and data.voice_duration_seconds:
            from src.services.credit_service import CreditService
            credits_needed = (
                math.ceil(data.voice_duration_seconds / 60)
                * self.settings.ai_credit_transcription_per_min
            )
            try:
                credit_service = CreditService(self.session, self.settings)
                await credit_service.consume_credits(
                    user_id=user.id,
                    amount=credits_needed,
                    operation_ref=f"voice_transcription_{uuid4()}",
                )
            except ValueError as e:
                raise VoiceNoteInsufficientCreditsError(str(e)) from e

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
            transcription_status=TranscriptionStatus.PENDING if is_voice_note else None,
        )

        self.session.add(note)
        await self.session.flush()
        await self.session.refresh(note)

        # Enqueue background transcription for voice notes
        if is_voice_note and data.voice_url and background_tasks is not None:
            note_id_copy = note.id  # capture before potential session expiry
            background_tasks.add_task(
                _transcribe_note_background,
                note_id=note_id_copy,
                audio_url=data.voice_url,
                duration_seconds=data.voice_duration_seconds or 0,
                settings=self.settings,
            )

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

        # Block content edits on archived notes; allow toggling archived flag itself
        if note.archived and data.content is not None:
            raise NoteArchivedError("Cannot modify content of an archived note")

        # Apply content update
        if data.content is not None:
            note.content = data.content.strip()

        # Apply archive toggle (spec v1.2: PATCH supports archived=true/false)
        if data.archived is not None:
            note.archived = data.archived

        self.session.add(note)
        await self.session.flush()
        await self.session.refresh(note)

        return note

    async def delete_note(self, user: User, note_id: UUID) -> DeletionTombstone:
        """Delete a note and create a tombstone for recovery (FR-013).

        T169: NoteService.delete_note

        Args:
            user: The requesting user
            note_id: The note ID to delete

        Returns:
            The created DeletionTombstone (tombstone_id usable for recovery)

        Raises:
            NoteNotFoundError: If note not found
        """
        note = await self.get_note(user=user, note_id=note_id, include_archived=True)

        # Serialize note snapshot for tombstone (spec v1.2 — no task_id)
        entity_data = {
            "id": str(note.id),
            "user_id": str(note.user_id),
            "content": note.content,
            "archived": note.archived,
            "voice_url": note.voice_url,
            "voice_duration_seconds": note.voice_duration_seconds,
            "transcription_status": (
                note.transcription_status.value
                if note.transcription_status
                else None
            ),
            "created_at": note.created_at.isoformat(),
            "updated_at": note.updated_at.isoformat(),
        }

        # Enforce FIFO tombstone limit (max 3 per user, FR-013)
        await self._enforce_tombstone_limit(user.id)

        # Create tombstone
        tombstone = DeletionTombstone(
            id=uuid4(),
            user_id=user.id,
            entity_type=TombstoneEntityType.NOTE,
            entity_id=note.id,
            entity_data=entity_data,
            deleted_at=datetime.now(UTC),
        )
        self.session.add(tombstone)

        await self.session.delete(note)
        await self.session.flush()

        return tombstone

    async def _enforce_tombstone_limit(self, user_id: UUID) -> None:
        """Enforce max 3 tombstones per user (FIFO), shared across entity types.

        Deletes oldest tombstones to stay within the limit (FR-013).
        """
        from src.services.recovery_service import MAX_TOMBSTONES_PER_USER

        count_query = select(func.count()).where(
            DeletionTombstone.user_id == user_id
        )
        result = await self.session.execute(count_query)
        count = result.scalar() or 0

        if count >= MAX_TOMBSTONES_PER_USER:
            excess = count - MAX_TOMBSTONES_PER_USER + 1
            oldest_query = (
                select(DeletionTombstone)
                .where(DeletionTombstone.user_id == user_id)
                .order_by(DeletionTombstone.deleted_at.asc())
                .limit(excess)
            )
            result = await self.session.execute(oldest_query)
            for tombstone in result.scalars().all():
                await self.session.delete(tombstone)

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
# BACKGROUND TASK
# =============================================================================


async def _transcribe_note_background(
    note_id: UUID,
    audio_url: str,
    duration_seconds: float,
    settings: Settings,
) -> None:
    """Background task: transcribe voice note via Deepgram and update note content.

    Task 3.7d: Called after response for voice note creation. Opens its own
    DB session (independent of request session). Sets COMPLETED + appends
    transcript to content on success; sets FAILED on any Deepgram error.
    Never raises — failures are logged only.
    """
    from src.dependencies import get_session_maker
    from src.integrations.deepgram_client import DeepgramClient, DeepgramError

    session_maker = get_session_maker(settings)
    async with session_maker() as session:
        # Load note in background session
        result = await session.execute(select(Note).where(Note.id == note_id))
        note = result.scalar_one_or_none()
        if note is None:
            logger.warning("Background transcription: note %s not found", note_id)
            return

        client = DeepgramClient(settings)
        try:
            transcription = await client.transcribe(
                audio_url=audio_url,
                duration_seconds=int(duration_seconds),
            )
            transcript = transcription.text

            # Append transcript to existing content (if any), else replace
            # Per spec v1.2: original_content + "\n\n---\n\n" + transcript
            if note.content and note.content.strip():
                note.content = note.content.strip() + "\n\n---\n\n" + transcript
            else:
                note.content = transcript

            note.transcription_status = TranscriptionStatus.COMPLETED
            session.add(note)
            await session.commit()
            record_voice_note_operation("transcribe")

        except DeepgramError as e:
            logger.error("Transcription failed for note %s: %s", note_id, e)
            try:
                await session.rollback()
                result = await session.execute(select(Note).where(Note.id == note_id))
                note = result.scalar_one_or_none()
                if note:
                    note.transcription_status = TranscriptionStatus.FAILED
                    session.add(note)
                    await session.commit()
            except Exception:
                logger.error("Failed to set transcription_failed for note %s", note_id)

        except Exception as e:
            logger.error(
                "Unexpected error in background transcription for note %s: %s",
                note_id,
                e,
            )

        finally:
            await client.close()


# =============================================================================
# FACTORY FUNCTION
# =============================================================================


def get_note_service(session: AsyncSession, settings: Settings) -> NoteService:
    """Get a NoteService instance."""
    return NoteService(session, settings)
