---
id: 003
title: Add Backend Documentation Directory
stage: spec
date: 2026-01-19
surface: agent
model: claude-opus-4-5-20251101
feature: 003-perpetua-backend
branch: 002-perpetua-frontend
user: developer
command: /sp.specify
labels: ["documentation", "backend", "api-spec", "data-model", "authentication"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-perpetua-backend/docs/data-model.md
  - specs/003-perpetua-backend/docs/api-specification.md
  - specs/003-perpetua-backend/docs/authentication.md
  - specs/003-perpetua-backend/spec.md
tests:
  - N/A (documentation only)
---

## Prompt

update 003 to have `/docs` directory containing info about the backend

## Response snapshot

Created a comprehensive `/docs` directory within the 003-perpetua-backend specification folder containing three detailed documentation files:

1. **data-model.md** - Complete database entity definitions including:
   - 13 entity definitions (User, Task Instance, Task Template, Subtask, Note, Reminder, Achievement Definition, User Achievement State, AI Credit Ledger, Subscription, Activity Log, Deletion Tombstone, Notification)
   - Field types, constraints, defaults, and validation rules
   - Entity relationships diagram
   - Tier-based limits table
   - Data integrity rules
   - Pydantic/SQLModel schema patterns

2. **api-specification.md** - Full REST API specification including:
   - Authentication endpoints (OAuth, refresh, logout)
   - Task endpoints (CRUD, force-complete, recover)
   - Subtask endpoints (create, update, reorder, delete)
   - Note endpoints (list, create, convert to task)
   - Reminder endpoints
   - AI endpoints (chat, generate subtasks, transcribe)
   - Achievement and Subscription endpoints
   - Notification endpoints
   - Error handling with standard codes
   - Rate limiting rules
   - Health check endpoints

3. **authentication.md** - Security documentation including:
   - Google OAuth flow diagram
   - JWT token structure and management
   - Token refresh strategy
   - Session management
   - Security measures checklist
   - Key rotation implementation
   - Error response formats
   - Monitoring and audit logging

Updated `spec.md` to add a "Related Documentation" section linking to all three docs files.

## Outcome

- ✅ Impact: Added comprehensive backend documentation structure for 003-perpetua-backend feature
- 🧪 Tests: N/A - documentation only, no code tests applicable
- 📁 Files: 3 new files created, 1 file modified
- 🔁 Next prompts: `/sp.plan` to create implementation plan, or `/sp.tasks` to generate tasks
- 🧠 Reflection: Documentation follows frontend spec pattern (data-model.md, api-specification.md) plus adds authentication.md for backend-specific security concerns

## Evaluation notes (flywheel)

- Failure modes observed: None - straightforward documentation task
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Consider adding additional docs like deployment.md or architecture.md if needed
