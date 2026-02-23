# ADR-001: Notes Standalone First-Class Entities

> **Scope**: Notes ownership model, API surface, tier limits, and archiving behavior — all
> components of the Note redesign (v1.1 → v1.2) that change together.

- **Status:** Accepted
- **Date:** 2026-02-21
- **Feature:** 003-perpetua-backend
- **Context:** In spec v1.1, Notes were nested resources scoped to a `TaskInstance`
  (`POST /tasks/{id}/notes`, `GET /tasks/{id}/notes`, `Note.task_id` FK). Analysis
  (`ANALYSIS_REVAMP_003.md`) and the `API_REVAMP.md` proposal identified this as
  architecturally limiting: users want a general-purpose capture surface independent of
  tasks, voice input (Pro), and the ability to promote a note to a task rather than
  starting every note within a task. The v1.1 design also had inconsistent tier limits
  (10 free / 25 pro) misaligned with the broader perk system (20/50). The decision to
  redesign was triggered by a proposed API revamp that could not be safely implemented
  without first updating the spec (Constitution II.2 gate), prompting a formal ADR.

---

## Decision

**Notes are redesigned as standalone, user-owned entities (not task-scoped).** The following
components change together as one architectural cluster:

### 1. Data Model: Remove `task_id` FK from Note

```python
# BEFORE (v1.1):
class Note(BaseModel, table=True):
    task_id: UUID = Field(foreign_key="task_instances.id")  # scoped to task
    task: "TaskInstance" = Relationship(back_populates="notes")

# AFTER (v1.2):
class Note(BaseModel, table=True):
    user_id: UUID = Field(foreign_key="users.id", index=True)  # standalone
    user: "User" = Relationship(back_populates="notes")
    # No task_id — notes are owned by the user, not a task
```

`TaskInstance` drops its `notes: list[Note]` relationship. `User` gains
`notes: list[Note] = Relationship(back_populates="user")`.

### 2. API Surface: Standalone Endpoints

| Change | v1.1 | v1.2 |
|--------|------|------|
| List notes | `GET /tasks/{id}/notes` | `GET /api/v1/notes` (user-scoped) |
| Create note | `POST /tasks/{id}/notes` | `POST /api/v1/notes` |
| Update note | `PATCH /notes/{id}` | `PATCH /api/v1/notes/{id}` (+ `archived` field) |
| Delete note | `DELETE /notes/{id}` | `DELETE /api/v1/notes/{id}` |
| Convert to task | `POST /notes/{id}/convert` | `POST /api/v1/notes/{id}/convert` |
| Deprecated routes | — | `POST/GET /tasks/{id}/notes` → 410 Gone |

`GET /api/v1/notes` supports `?archived=bool` filter. List ordered `created_at DESC`,
max 50/page.

### 3. Tier Limits: Corrected to Match Perk System

| Tier | v1.1 | v1.2 | Achievement bonus |
|------|------|------|------------------|
| Free | 10 | 20 | +10 (`notes_10`) |
| Pro | 25 | 50 | +10 (`notes_10`) |

Limit enforcement: `NoteLimitExceededError` → **HTTP 402 LIMIT_EXCEEDED**
(not 409 NOTE_LIMIT_EXCEEDED — aligns with credit/quota pattern in FR-007).

### 4. Archiving: User-Driven via PATCH

Notes are explicitly archived by the user (`PATCH /notes/{id}` with `{"archived": true}`).
The convert endpoint returns an AI suggestion; the user creates the task and archives the note
in separate, explicit steps. Auto-archiving by the convert endpoint is intentionally rejected
(see Alternatives, and Constitution IV.2: AI actions require explicit user confirmation).

`NoteUpdate` schema extended:
```python
class NoteUpdate(BaseModel):
    content: str | None = None
    archived: bool | None = None   # ← v1.2 addition
```

Guard: content updates on an already-archived note are blocked (`NoteArchivedError`).
Setting `archived=false` (unarchiving) is allowed.

### 5. Recovery (Tombstone) Backward Compatibility

Note tombstone snapshots created before v1.2 may contain a `task_id` field. The
`RecoveryService` must silently ignore `task_id` when deserializing pre-v1.2 tombstones.
New tombstones (v1.2+) omit `task_id` entirely.

### 6. Database Index Strategy

```sql
-- v1.2: single-column index (all queries user-scoped)
CREATE INDEX ix_note_user_id ON notes(user_id);

-- Removed:
-- DROP INDEX ix_note_task_id;  (task_id column gone)
-- No composite (user_id, task_id) index needed
```

---

## Consequences

### Positive

- **User flexibility**: Notes can capture ideas before a task context exists; users are
  not forced to create or choose a task before capturing a thought.
- **Natural promote flow**: Convert note → task is a deliberate promotion action, matching
  real-world workflows (scratch-pad → committed task).
- **Achievment perk alignment**: Limits 20/50 fit within the perk system design (notes_10
  achievement grants +10 to both tiers). The v1.1 limits 10/25 had no such alignment.
- **Cleaner data model**: One FK less on Note; simpler queries (no JOIN with task_instances
  needed for note ownership checks).
- **Simpler tests**: No need to create a task fixture just to test note CRUD.
- **Graceful deprecation**: 410 Gone routes give clients a clear migration message rather
  than silent 404s.

### Negative

- **Loss of task-note co-location**: Users who want notes visually associated with a task
  must rely on the convert flow or manually track the relationship. Task detail views cannot
  directly list "notes for this task" without a separate query.
- **Migration complexity**: Any pre-v1.2 tombstones containing `task_id` require tolerance
  logic in RecoveryService. Pre-v1.2 client code using `POST /tasks/{id}/notes` will receive
  410 and must update.
- **Limit increase risk**: Raising free tier from 10 → 20 doubles storage potential per free
  user. Acceptable at current scale (~10k users) but worth monitoring at 100k+.
- **Test churn**: All existing note limit tests using 10/25 must be updated to 20/50.

---

## Alternatives Considered

### Alternative A: Keep Task-Scoped Notes (v1.1 Status Quo)

**What**: Retain `task_id` FK on Note; list notes via `GET /tasks/{id}/notes`; notes are
a nested resource of tasks.

**Why rejected**:
- Users cannot capture a note without first selecting/creating a task — friction that
  reduces note capture rate.
- Voice input flow (Pro) implies quick capture, not task-first workflow.
- 10/25 limits misaligned with achievement perk values; would require a separate perk
  table for notes vs. tasks.
- Noted as CRITICAL inconsistency (C2) in ANALYSIS_REVAMP_003.md.

### Alternative B: Dual Ownership (Both task_id and user_id on Note)

**What**: Note has both `user_id` (always set) and `task_id` (optional FK, nullable).
Task-scoped endpoints coexist with user-scoped endpoints.

**Why rejected**:
- Nullable FK adds query complexity (WHERE task_id IS NOT NULL for task-scoped; WHERE
  task_id IS NULL for standalone).
- Ambiguous limit semantics: does the free-user limit of 20 apply to standalone notes
  only, or all notes regardless of task scope?
- Two routing conventions for the same resource creates API surface confusion.
- Constitution VI.1 (single-responsibility endpoints) violated by overlapping routes.

### Alternative C: Automatic Archive on Convert (Atomic Convert-and-Create)

**What**: `POST /notes/{id}/convert` atomically creates the task AND archives the note,
returning `{task: {...}, note: {...}}` in a single response.

**Why rejected**:
- Constitution IV.2: AI suggested actions must require explicit user confirmation before
  execution. Auto-creating a task without user review violates this guarantee.
- The AI suggestion may have incorrect priority, due date, or title — the user must
  review before committing.
- Idempotency is harder to guarantee for a two-entity atomic operation across task and
  note tables.
- Chosen approach (suggestion → user review → explicit PATCH to archive) preserves the
  undo guarantee (Constitution III.4).

### Alternative D: Event-Sourced Notes (Append-Only Log)

**What**: Notes stored as an event log rather than a mutable entity; "updating" a note
appends a new event.

**Why rejected**:
- Over-engineered for a simple capture surface at current scale.
- No requirement for note history or audit log beyond the activity log (FR-014).
- Adds infrastructure complexity (event stream, snapshot reconstruction).
- Constitution X.1: simplicity over scale — chose the simplest viable design.

---

## References

- Feature Spec: [specs/003-perpetua-backend/spec.md — FR-012](../../specs/003-perpetua-backend/spec.md)
- Implementation Plan: [specs/003-perpetua-backend/plan.md](../../specs/003-perpetua-backend/plan.md)
- Data Model: [specs/003-perpetua-backend/data-model.md](../../specs/003-perpetua-backend/data-model.md)
- Analysis: [ANALYSIS_REVAMP_003.md — Section B](../../ANALYSIS_REVAMP_003.md)
- API Revamp Proposal: [API_REVAMP.md](../../API_REVAMP.md)
- PHR: [history/prompts/003-perpetua-backend/044-revise-plan-notes-v12-standalone.plan.prompt.md](../prompts/003-perpetua-backend/044-revise-plan-notes-v12-standalone.plan.prompt.md)
- Related ADRs: None (first ADR)
- Evaluator Evidence: ANALYSIS_REVAMP_003.md — findings C2, C3, C4, H1, H2, H3
