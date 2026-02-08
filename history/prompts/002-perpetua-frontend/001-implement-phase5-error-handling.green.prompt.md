---
id: 001
title: Implement Phase 5 Error Handling
stage: green
date: 2026-02-08
surface: agent
model: claude-opus-4-6
feature: 002-perpetua-frontend
branch: 002-perpetua-frontend
user: 404mw
command: continue with phase 5
labels: ["error-handling", "error-boundary", "toast", "providers", "msw-removal"]
links:
  spec: FRONTEND-BACKEND-INTEGRATION.md
  ticket: null
  adr: null
  pr: null
files:
  - frontend/src/components/ErrorBoundary.tsx
  - frontend/src/lib/utils/errorHandler.ts
  - frontend/src/lib/hooks/useToast.ts
  - frontend/src/lib/hooks/index.ts
  - frontend/src/app/providers.tsx
tests:
  - none (Phase 6 covers testing)
---

## Prompt

continue with phase 5

## Response snapshot

Implemented Phase 5: Error Handling from FRONTEND-BACKEND-INTEGRATION.md (lines 835-943):

**Task 5.1 - ErrorBoundary component** (`ErrorBoundary.tsx`): React class component with `getDerivedStateFromError`, supports static fallback or `(error, reset) => ReactNode` render-prop pattern.

**Task 5.2 - Error handler utility** (`errorHandler.ts`): Maps 12 backend error codes (VALIDATION_ERROR, UNAUTHORIZED, TOKEN_EXPIRED, FORBIDDEN, TIER_REQUIRED, NOT_FOUND, INSUFFICIENT_CREDITS, CONFLICT, LIMIT_EXCEEDED, ARCHIVED, RATE_LIMIT_EXCEEDED, AI_SERVICE_UNAVAILABLE) to user-friendly `{ title, message, action }` objects with recovery actions (retry, login, upgrade, none).

**Task 5.3 - Toast integration** (`useToast.ts`): Added `showApiError(error: unknown)` function that converts any error (ApiError or generic Error) to a user-friendly toast notification using the error handler. Exported from `hooks/index.ts`.

**Task 5.4 - Providers rewrite** (`providers.tsx`): Removed all MSW dev mode code (MSWReadyContext, useMSWReady, MSW initialization useEffect). Added ErrorBoundary wrapper, smart retry logic (non-retryable codes skip retries), and global mutation `onError` that auto-shows toast via `showApiError`.

## Outcome

- Impact: Complete Phase 5 error handling layer connecting backend error codes to user-facing feedback
- Tests: Deferred to Phase 6
- Files: 5 files (2 created, 3 modified)
- Next prompts: Phase 6 - Testing & Validation
- Reflection: MSW removal from providers was clean since it was a full rewrite. ErrorBoundary uses class component pattern (required by React for error boundaries).

## Evaluation notes (flywheel)

- Failure modes observed: Write tool requires recent Read before editing - needed to re-read files that were modified by linter between reads
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
