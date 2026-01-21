---
id: 005
title: Update Plan to Use OpenAI Agents SDK
stage: plan
date: 2026-01-19
surface: agent
model: claude-opus-4-5-20251101
feature: 003-perpetua-backend
branch: 002-perpetua-frontend
user: system
command: /sp.plan
labels: ["openai-agents", "plan-update", "ai-integration"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-perpetua-backend/plan.md
  - specs/003-perpetua-backend/research.md
tests:
  - null
---

## Prompt

update 003 plan to use `openai-agents` instead of `openai`

## Response snapshot

Updated the 003-perpetua-backend plan and research documents to use `openai-agents` (OpenAI Agents SDK) instead of the raw `openai` package. Key changes:

1. **plan.md - Technical Context**: Changed primary dependency from `openai` to `openai-agents`
2. **plan.md - OpenAI Integration Section**: Updated to reflect agent-based architecture with tool definitions, built-in streaming via `Runner.run_streamed()`, and tracing capabilities
3. **plan.md - Project Structure**: Renamed `openai_client.py` to `ai_agent.py` to better reflect the agent-based approach
4. **research.md - OpenAI Integration**: Complete rewrite with Agents SDK patterns including Agent definition, function_tool decorator, structured output via Pydantic models, and streaming implementation

## Outcome

- Impact: Documentation updated to specify openai-agents SDK for AI integration
- Tests: N/A (documentation only)
- Files: 2 files modified (plan.md, research.md)
- Next prompts: Generate tasks.md, implement AI agent integration
- Reflection: The Agents SDK provides cleaner separation of concerns with agent definitions and tool-based interactions vs raw API calls

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
