<!--
SYNC IMPACT REPORT
==================
Version Change: [INITIAL] → 1.0.0
Modified Principles: N/A (initial ratification)
Added Sections:
  - I. Authority & Source of Truth
  - II. Phase Discipline (Hard Gates)
  - III. Data Integrity & Safety
  - IV. AI Agent Governance
  - V. AI Logging & Auditability
  - VI. API Design Rules
  - VII. Validation & Type Safety
  - VIII. Testing Doctrine
  - IX. Secrets & Configuration
  - X. Infrastructure Philosophy
  - XI. Enforcement
Removed Sections: N/A (initial version)
Templates Status:
  ✅ plan-template.md - Verified: Constitution Check section aligns with phase discipline and enforcement
  ✅ spec-template.md - Verified: User scenarios align with testing doctrine and spec-first approach
  ✅ tasks-template.md - Verified: TDD requirements and phase organization align with testing doctrine
  ⚠ CLAUDE.md - Reviewed: Contains compatible guidance on PHR creation and ADR suggestions
Follow-up TODOs: None
-->

# TODO App Constitution

**Project Type:** Production-grade, single-user SaaS
**Methodology:** Spec-Driven Development (SDD)
**Project Status:** Open-ended, living system
**Primary Principle:** Build once, evolve forever — no rewrites

---

## I. Authority & Source of Truth

1. **The specification is the supreme authority.**
   If implementation, tests, or runtime behavior diverge from the specification, they are wrong by default.

2. **Hotfix exception rule (production only):**
   - A hotfix may be applied to protect users or data.
   - The specification MUST be updated immediately afterward.
   - A hotfix is incomplete until the spec reflects the new behavior.

3. **Executable spec doctrine:**
   The specification must define:
   - system states and transitions,
   - invariants and constraints,
   - edge cases and failure modes,
   - AI permissions and limits.
   High-level descriptions are insufficient.

---

## II. Phase Discipline (Hard Gates)

1. **Strict phase sequencing:**
   A new phase MUST NOT begin until the previous phase is:
   - fully implemented,
   - fully tested,
   - fully documented in the specification.

2. **No spec, no code:**
   Any behavioral change requires a spec update BEFORE implementation.

3. **No partial completion:**
   A phase is either complete or not started. Overlap is forbidden.

---

## III. Data Integrity & Safety

1. **User data loss is unacceptable.**
   This is a non-negotiable constraint.

2. **Minimum recovery guarantee:**
   - Automated daily backups are mandatory in production.

3. **Dummy-first rule:**
   - All development and testing must use dummy data by default.
   - Real user data must never be used for testing.

4. **Undo guarantee:**
   - Undo is guaranteed for all updates performed during the current session.
   - Undo is valid until the next mutation occurs.
   - Undo is not best-effort; it is a contractual guarantee.

---

## IV. AI Agent Governance

1. **AI is an autonomous agent, not a trusted authority.**

2. **Default restrictions (hard rules):**
   The AI agent MUST NEVER, by default:
   - change task state,
   - delete tasks.

3. **Opt-in behavior:**
   - Autonomous AI actions are globally opt-in.
   - Opt-in may be revoked at any time.
   - Revocation does not invalidate undo guarantees.

4. **Interaction flow (mandatory):**
   - User sends prompt.
   - AI takes action.
   - AI sends confirmation response.
   - UI updates automatically.
   - A popup is shown with an undo option.

5. **AI loop control:**
   - While an AI task is running, the send button becomes a stop button.
   - Stopping halts the current loop only.
   - Undo remains available for completed actions.

---

## V. AI Logging & Auditability

1. **Every AI interaction is an event.**

2. **Mandatory logged fields:**
   - task ID (used to resolve task data),
   - timestamp,
   - actor identity (user or AI).

3. **Logs are immutable.**
   Logged events must never be modified or deleted.

---

## VI. API Design Rules

1. **Single responsibility endpoints:**
   Each API endpoint must serve exactly one purpose.

2. **Mandatory documentation:**
   Every endpoint must include:
   - clear intent,
   - input/output schema,
   - error behavior.

3. **No hidden side effects:**
   API calls must not trigger undocumented state changes.

---

## VII. Validation & Type Safety

1. **Schema consistency is mandatory:**
   - Zod for frontend validation,
   - Pydantic / SQLModel for backend validation.

2. **Schemas define truth:**
   Any mismatch between schemas is a defect.

---

## VIII. Testing Doctrine

1. **Test-driven development is mandatory.**

2. **Coverage expectation:**
   - Core logic,
   - API behavior,
   - state transitions,
   - AI interaction boundaries.

3. **Tests precede real data.**
   Production behavior must be proven using dummy data first.

---

## IX. Secrets & Configuration

1. **All secrets and keys must live in `.env`.**

2. **Environment validation is mandatory:**
   - A dedicated env validator must block startup if required variables are missing.

3. **No secret leakage:**
   - Secrets must never be exposed to the UI or client-side code.

4. **AI usage limits:**
   - All AI limits must be configurable via `.env`.
   - No hardcoded limits in code.

---

## X. Infrastructure Philosophy

1. **Primary priority:** Simplicity over scale.

2. **Complexity must be justified.**
   If a simpler solution exists, it must be preferred.

---

## XI. Enforcement

1. **Breaking the constitution is a bug.**
2. **Intentional violations require explicit documentation.**
3. **Silently bypassing rules is forbidden.**

---

## Governance

### Amendment Procedure

1. **Proposal requirement:**
   - All amendments must be proposed in writing with explicit rationale.
   - Changes must be reviewed against existing principles for conflicts.

2. **Impact assessment:**
   - Identify all affected templates, documentation, and code.
   - Document migration path if changes require codebase updates.

3. **Version control:**
   - Constitution follows semantic versioning (MAJOR.MINOR.PATCH).
   - MAJOR: Backward-incompatible principle removals or redefinitions.
   - MINOR: New principles added or materially expanded guidance.
   - PATCH: Clarifications, wording, typo fixes, non-semantic refinements.

4. **Propagation requirement:**
   - All dependent artifacts must be updated before amendment is complete.
   - Templates, documentation, and guidance files must reflect new principles.

### Compliance Review

1. **All development work must verify compliance with this constitution.**
2. **Pull requests and code reviews must explicitly check for violations.**
3. **Automated checks should enforce constitutional requirements where possible.**

### Final Clause

This constitution exists to prevent:

- silent data corruption,
- AI overreach,
- architectural drift,
- and future rewrites.

Any change to this constitution must be deliberate, documented, and justified.

---

**Version**: 1.0.0 | **Ratified**: 2026-01-03 | **Last Amended**: 2026-01-03
