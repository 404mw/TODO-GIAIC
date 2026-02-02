---
id: 023
title: Implement Phase 10 AI Chat Widget
stage: green
date: 2026-01-25
surface: agent
model: claude-opus-4-5
feature: 003-perpetua-backend
branch: 002-perpetua-frontend
user: developer
command: /sp.implement 003 phase-10
labels: ["ai", "chat", "credits", "openai", "streaming"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/integrations/ai_agent.py
  - backend/src/services/ai_service.py
  - backend/src/api/ai.py
  - backend/src/main.py
  - backend/tests/unit/services/test_ai_service.py
  - backend/tests/contract/test_ai_contract.py
  - backend/tests/integration/test_ai_features.py
  - backend/tests/conftest.py
tests:
  - tests/unit/services/test_ai_service.py
  - tests/contract/test_ai_contract.py
  - tests/integration/test_ai_features.py
---

## Prompt

003 phase-10

## Response snapshot

Implemented Phase 10: User Story 6 - AI Chat Widget (24 tasks, T221-T242) following TDD workflow:

**RED Phase (T221-T227):**
- Created failing tests in `tests/unit/services/test_ai_service.py` covering:
  - Credit deduction (FR-030)
  - 402 insufficient credits
  - Action suggestion confirmation (FR-034)
  - Per-task request warnings at 5 requests (FR-035)
  - Per-task request blocking at 10 requests (FR-035)
  - 503 service unavailable
- Created contract tests in `tests/contract/test_ai_contract.py`

**GREEN Phase (T228-T234):**
- Implemented `AIAgentClient` in `src/integrations/ai_agent.py`:
  - OpenAI API integration with chat, streaming, subtask generation
  - 30-second timeout handling
  - Service unavailable fallback
- Implemented `AIService` in `src/services/ai_service.py`:
  - Credit check and FIFO consumption
  - Per-task request counters (5 warn, 10 block)
  - Action suggestion validation

**API Endpoints (T235-T238):**
- `POST /api/v1/ai/chat` - Chat with SSE streaming support
- `POST /api/v1/ai/chat/stream` - Streaming variant
- `POST /api/v1/ai/generate-subtasks` - Subtask generation
- `POST /api/v1/ai/confirm-action` - Confirm AI-suggested actions
- `GET /api/v1/ai/credits` - Credit balance query
- Applied 20 req/min rate limit (FR-061)

**REFACTOR Phase (T239-T242):**
- Enhanced OpenAI mocks in `tests/conftest.py`
- Created integration tests in `tests/integration/test_ai_features.py`
- Added AI interaction logging

## Outcome

- ✅ Impact: Phase 10 complete - AI Chat Widget fully implemented with credit management
- 🧪 Tests: Unit tests, contract tests, and integration tests created
- 📁 Files: 8 files created/modified
- 🔁 Next prompts: Phase 11 (Auto Subtask Generation), Phase 12 (Note Conversion)
- 🧠 Reflection: TDD approach ensured all requirements covered; credit FIFO and per-task limits properly tracked

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Not run yet
- Prompt variant (if applicable): Standard /sp.implement
- Next experiment (smallest change to try): Run test suite to verify implementation
