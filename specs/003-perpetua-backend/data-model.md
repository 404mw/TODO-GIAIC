# Data Model: 003 — Perpetua Flow Backend

**Version**: 1.2 (Notes Standalone Redesign)
**Date**: 2026-02-21
**Source**: Reverse engineered from codebase + spec.md v1.2

---

## Entity Overview

| # | Entity | Table | Description |
|---|--------|-------|-------------|
| 1 | User | `users` | Auth identity + tier + achievement state |
| 2 | TaskInstance | `task_instances` | Core task entity with optimistic locking |
| 3 | Subtask | `subtasks` | Child tasks, ordered by `order_index` |
| 4 | **Note** | **`notes`** | **Standalone user-owned note (v1.2 — no task_id)** |
| 5 | Credit | `credits` | Credit ledger (multi-type, append-only) |
| 6 | UserAchievementState | `user_achievement_states` | Aggregated achievement stats + unlocked set |
| 7 | FocusSession | `focus_sessions` | Pomodoro timer sessions |
| 8 | Reminder | `reminders` | Absolute + relative task reminders |
| 9 | TaskTemplate | `task_templates` | Reusable task blueprints |
| 10 | DeletionTombstone | `deletion_tombstones` | 7-day soft delete snapshots |
| 11 | ActivityLog | `activity_logs` | Immutable audit trail |
| 12 | IdempotencyKey | `idempotency_keys` | 24h idempotency cache |
| 13 | RefreshToken | `refresh_tokens` | Opaque rotation tokens |

> **Scope note**: This document focuses on the v1.2 migration changes (Notes standalone
> redesign). Entities not listed below retain their schemas as defined in the codebase
> and are documented in `backend/src/models/`. A full column-level schema for all 13
> entities is tracked as a Phase 8 documentation improvement.

---

## Entity 4: Note (v1.2 — Standalone User-Owned)

> **v1.1 → v1.2 change**: `task_id` FK removed. Notes are owned directly by `user_id`
> only. Notes support text content, voice recording metadata (Pro), and explicit archiving.

### Fields

| Field | Type | Nullable | Default | Constraints | Description |
|-------|------|----------|---------|-------------|-------------|
| `id` | UUID | No | gen_random_uuid() | PK | Unique identifier |
| `user_id` | UUID | No | — | FK → users.id, INDEX | Owner (standalone, not task-scoped) |
| `content` | TEXT | No | — | 0–2000 chars; min 1 unless `voice_url` set at creation | Note text (Markdown supported). May be empty string `""` for voice notes (label optional). |
| `archived` | BOOLEAN | No | false | — | Archived flag (set via PATCH or after convert) |
| `voice_url` | TEXT | Yes | null | — | Audio file URL (S3/R2), Pro only |
| `voice_duration_seconds` | INTEGER | Yes | null | 1–300 | Recording duration, Pro only |
| `transcription_status` | ENUM | Yes | null | pending\|completed\|failed | Voice transcription state |
| `created_at` | TIMESTAMPTZ | No | now() | — | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | No | now() | — | Last update timestamp |

### Removed (v1.1 → v1.2)

| Field | Reason |
|-------|--------|
| `task_id` UUID FK | Notes redesigned as standalone user entities (FR-012 v1.2) |

### Indexes

| Index Name | Columns | Type | Reason |
|-----------|---------|------|--------|
| `ix_note_user_id` | `user_id` | BTree | All note queries are user-scoped |
| ~~`ix_note_task_id`~~ | ~~`task_id`~~ | Removed | task_id no longer exists |

### Relationships

| Relationship | Direction | Back-populates |
|-------------|-----------|---------------|
| `user` | Note → User | `User.notes` |

### Constraints

| Constraint | Rule |
|-----------|------|
| Note limit | Free tier: max 20 (base) + achievement perks; Pro tier: max 50 + perks |
| Voice note tier | `voice_url` and `voice_duration_seconds` require Pro tier |
| Voice fields together | Both `voice_url` + `voice_duration_seconds` required together |
| Content limit | 0–2000 chars; **min 0** when `voice_url` is set (voice note label); **min 1** otherwise. Uniform max 2000 for all tiers (v1.2). |
| Archived update | Can set `archived=true` via PATCH; cannot update content of already-archived note |

---

## Entity 1: User

### Fields (relevant to Notes)

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | PK |
| `tier` | ENUM(free, pro) | Determines note limits |
| `notes` | Relationship | `list[Note]` (back_populates="user") |

---

## Entity 2: TaskInstance

### Removed Relationship (v1.1 → v1.2)

| Relationship | Status |
|-------------|--------|
| `notes: list[Note]` | **Removed** — notes no longer task-scoped |

---

## Entity 10: DeletionTombstone (Note snapshot format)

### Note Snapshot (v1.2)

```json
{
  "note": {
    "id": "uuid",
    "user_id": "uuid",
    "content": "Note text content",
    "archived": false,
    "voice_url": null,
    "voice_duration_seconds": null,
    "transcription_status": null,
    "created_at": "2026-02-21T12:00:00Z",
    "updated_at": "2026-02-21T12:00:00Z"
  }
}
```

**Backward compatibility**: Tombstones created before v1.2 may contain `"task_id"` in
the snapshot. The recovery service MUST silently ignore `task_id` when recreating the
note (the field no longer exists on the model).

---

## Note Limits Summary

| Tier | Base | Achievement Bonus | Max Total |
|------|------|------------------|-----------|
| Free | 20 | +10 (`notes_10`) | 30 |
| Pro | 50 | +10 (`notes_10`) | 60 |

**`notes_10` achievement**: Unlocked when `notes_converted` stat ≥ 10.
Perk: `MAX_NOTES +10`.

---

## State Transitions: Note

```
[created]
    │
    ├── PATCH content → [updated]
    │
    ├── PATCH archived=true → [archived]
    │       │
    │       └── PATCH archived=false → [created]  ← unarchive allowed
    │
    ├── POST .../convert → AI suggestion returned (no auto-archive)
    │       └── User reviews → PATCH archived=true → [archived]
    │
    └── DELETE → [tombstone] → (7-day recovery window) → [expired]
```

---

## Migration Checklist (v1.1 → v1.2)

> These are **code-level** changes only. No database ALTER TABLE is required
> because the `task_id` column was not in the deployed DB baseline.

- [x] `src/lib/limits.py`: `FREE_TIER_NOTE_LIMIT = 10` → `20` ✅ applied
- [x] `src/lib/limits.py`: `PRO_TIER_NOTE_LIMIT = 25` → `50` ✅ applied
- [x] `src/schemas/note.py`: Add `archived: bool | None` to `NoteUpdate` ✅ applied
- [x] `src/services/note_service.py`: Handle `archived` field in `update_note()` ✅ applied
- [x] `src/api/notes.py`: `NoteLimitExceededError` → 402 (not 409) ✅ confirmed
- [x] `src/api/tasks.py`: 410 Gone for `POST/GET /tasks/{id}/notes` ✅ confirmed: api/tasks.py (added 2026-02-22); raises HTTP_410_GONE with ENDPOINT_GONE error code
- [ ] Tests: Update note limit fixtures from 10/25 to 20/50 — tracked in Task 7.1
- [ ] Tests: Add PATCH `archived=true` test case — tracked in Task 7.1
- [ ] Tests: Add 410 Gone test for deprecated endpoints — tracked in Task 7.1

---

*Generated by Claude Sonnet 4.6 | 2026-02-21 | Feature 003 — data-model.md v1.2*
