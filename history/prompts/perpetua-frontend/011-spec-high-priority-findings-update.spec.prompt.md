---
id: 011
title: Spec High Priority Findings Update
stage: spec
date: 2026-01-08
surface: agent
model: claude-sonnet-4-5
feature: perpetua-frontend
branch: 002-perpetua-frontend
user: system
command: /sp.specify
labels: ["spec-update", "analysis-findings", "requirements", "edge-cases", "terminology"]
links:
  spec: specs/002-perpetua-frontend/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/002-perpetua-frontend/spec.md
tests:
 - null
---

## Prompt

Update spec.md to address all HIGH priority analysis findings:

## 1. Add FR-072a (Notification Fallback)
After FR-072, add:
**FR-072a**: If browser notification permission is denied, system MUST fall back to in-app toast notifications only; Service Worker continues polling MSW but only sends postMessage to clients (no Notification API calls); users are shown a one-time prompt explaining reduced notification functionality with link to browser settings to enable permissions

## 2. Add FR-073a (Recurrence Validation)
After FR-073, add:
**FR-073a**: Custom recurrence intervals MUST:
- Be limited to maximum 365 days (1 year)
- Be validated via RRule RFC 5545 parsing before storage
- Reject invalid patterns (e.g., "every Feb 30", "every 0 days") with specific error messages
- Support common patterns: "every N days" (1-365), "every N weeks on [weekdays]" (1-52), "every month on day X" (1-28 to avoid month-end issues)
- Display validation errors inline in RecurrenceEditor component
- Provide human-readable pattern description preview using RRule.toText()

## 3. Terminology Standardization
- Replace all "dopamine engine" / "Dopamine Engine" with "Achievements System"
- Add terminology note in Key Entities section after Achievement entity definition

## 4. Edge Cases Additions
Add these edge cases:
- "What happens if user denies browser notification permission?" → System falls back to in-app toasts only; Service Worker still polls and sends messages to all open tabs; no error shown, degraded experience is silent except for one-time informational prompt
- "What happens if user creates invalid recurrence pattern like Feb 30?" → System validates via RRule parsing, shows error "Invalid date pattern: February 30 does not exist", suggests valid alternatives (e.g., "last day of February")
- "What happens if user sets recurrence interval beyond 365 days?" → System shows error "Maximum interval is 365 days", suggests using manual task creation for longer cycles

Regenerate spec.md with all these changes.

## Response snapshot

Successfully updated [specs/002-perpetua-frontend/spec.md](specs/002-perpetua-frontend/spec.md) with all high-priority analysis findings:

1. **FR-072a Added** ([line 276](specs/002-perpetua-frontend/spec.md#L276)): Browser notification fallback requirement with Service Worker behavior and user prompt specifications
2. **FR-073a Added** ([line 278](specs/002-perpetua-frontend/spec.md#L278)): Comprehensive recurrence validation requirements including RRule parsing, interval limits (365 days), supported patterns, inline validation, and human-readable preview
3. **Terminology Standardized**: Replaced "dopamine engine" with "Achievements System" throughout the spec ([line 6](specs/002-perpetua-frontend/spec.md#L6))
4. **Terminology Note Added** ([line 313](specs/002-perpetua-frontend/spec.md#L313)): Clarification in Key Entities section explaining the terminology evolution
5. **Edge Cases Added** ([lines 161-163](specs/002-perpetua-frontend/spec.md#L161-L163)): Three new edge cases covering notification permission denial, invalid recurrence patterns, and interval limit violations

All changes maintain spec format, follow existing requirement numbering convention, and integrate seamlessly with current content.

## Outcome

- ✅ Impact: Specification completeness improved with critical fallback behavior, validation rules, and edge case handling; terminology standardized for clarity
- 🧪 Tests: No tests run (spec-only update)
- 📁 Files: 1 modified (specs/002-perpetua-frontend/spec.md)
- 🔁 Next prompts: Ready for `/sp.plan` or continue with spec refinements as needed
- 🧠 Reflection: High-priority analysis findings successfully integrated; spec now has clearer requirements for notification fallback, recurrence validation, and user-facing error messages

## Evaluation notes (flywheel)

- Failure modes observed: None; all changes applied successfully
- Graders run and results (PASS/FAIL): N/A (spec update)
- Prompt variant (if applicable): Standard spec update prompt
- Next experiment (smallest change to try): Proceed with planning phase to design implementation approach for new requirements
