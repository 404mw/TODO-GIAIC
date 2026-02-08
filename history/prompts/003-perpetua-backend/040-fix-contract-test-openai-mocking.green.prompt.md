---
id: 040
title: Fix Contract Test OpenAI Mocking
stage: green
date: 2026-02-03
surface: agent
model: claude-opus-4-5-20251101
feature: 003-perpetua-backend
branch: 002-perpetua-frontend
user: architect
command: /sp.implement
labels: ["contract-tests", "mocking", "respx", "openai", "test-reliability"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/tests/contract/conftest.py
  - backend/tests/contract/test_ai_contract.py
tests:
  - backend/tests/contract/test_ai_contract.py (10 tests: 9 passed, 1 xfailed)
  - backend/tests/contract/ (154 total: 150 passed, 2 skipped, 2 xfailed)
  - backend/tests/unit/ (693 passed, no regressions)
---

## Prompt

003

Check and fix the non-fuzz contract test failures — The `test_ai_contract.py` failure (503 from `sk-test-key`) indicates contract tests hitting real OpenAI integration instead of mocks. These need `respx` mocking in the contract test conftest.

## Response snapshot

Fixed contract tests hitting real OpenAI API by adding an autouse `mock_external_apis` fixture in `tests/contract/conftest.py` that mocks OpenAI, Deepgram, Checkout.com, and Google JWKS endpoints. Also fixed two tests in `test_ai_contract.py` that had vacuous conditional assertions (`if response.status_code == 200/429`) — they now properly assert expected behavior. All 154 contract tests pass (150 passed, 2 skipped, 2 xfailed). All 693 unit tests pass with no regressions.

## Outcome

- ✅ Impact: Contract tests now reliably mock all external APIs via autouse fixture; no test can accidentally hit real OpenAI/Deepgram/Checkout APIs
- 🧪 Tests: 154 contract tests pass (150 passed, 2 skipped, 2 xfailed); 693 unit tests pass
- 📁 Files: 2 files modified (contract conftest.py, test_ai_contract.py)
- 🔁 Next prompts: Consider fixing the 2 xfailed contract tests (MissingGreenlet and complete_task missing argument)
- 🧠 Reflection: The root cause was tests with conditional assertions that silently passed when OpenAI returned 503 — the autouse mock approach prevents this class of issue for all future contract tests

## Evaluation notes (flywheel)

- Failure modes observed: Tests using conditional assertions (if status == 200) passed vacuously when external API returned errors; sk-test-key hitting real OpenAI API
- Graders run and results (PASS/FAIL): All contract tests PASS, all unit tests PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Fix the 2 xfailed tests (selectinload for subtasks, complete_task completed_by argument)
