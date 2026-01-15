---
id: 005
title: Add Testing Requirements with React Testing Library
stage: spec
date: 2026-01-08
surface: agent
model: claude-sonnet-4-5
feature: perpetua-frontend
branch: 002-perpetua-frontend
user: Claude Agent
command: /sp.specify
labels: ["testing", "tdd", "react-testing-library", "spec-update"]
links:
  spec: specs/002-perpetua-frontend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-perpetua-frontend/spec.md
tests:
  - None (specification update only)
---

## Prompt

constitution enforces TDD, add testing with react testing library in 002

## Response snapshot

Updated the perpetua-frontend specification (specs/002-perpetua-frontend/spec.md) to add comprehensive Testing Requirements section that enforces TDD with React Testing Library.

### Key additions:

1. **Testing Philosophy**: Mandates TDD as per constitution Section VIII
2. **Testing Framework & Tools**: React Testing Library, Jest, MSW, @testing-library packages
3. **Test Coverage Requirements**:
   - Unit tests for rendering, interactions, accessibility, and state management
   - Integration tests for critical user flows (task creation, focus mode, AI features, search)
   - Given-When-Then test structure requirement
4. **Critical Test Cases**: Mapped each user story (P1-P3) to specific test requirements
5. **Edge Case Tests**: Explicit tests for all documented edge cases
6. **Test Naming Convention**: `[Component/Feature] - [User Action] - [Expected Outcome]`
7. **MSW Mock Handlers**: All API endpoints documented with expected responses
8. **Test Execution Requirements**: Pre-commit hooks, CI pipeline, 80% coverage threshold, 2-minute max runtime
9. **Testing Best Practices**: Query priority (getByRole first), async testing patterns, user-centric approach, accessibility testing
10. **TDD Workflow**: Red-Green-Refactor cycle with examples
11. **Testing Anti-Patterns**: What NOT to do (implementation details, snapshots, testing libraries, etc.)
12. **Testing Documentation**: File header, setup/teardown, grouping, comments

### Dependencies updated:
- Added React Testing Library, Jest, @testing-library/jest-dom, @testing-library/user-event to dependencies list

### Fixed markdown linting issues:
- Converted bold text to proper headings (h5)
- Added blank lines around lists
- Added language specifier to code blocks

## Outcome

- ✅ Impact: Comprehensive testing requirements added to perpetua-frontend spec, enforcing TDD per constitution mandate
- 🧪 Tests: No tests run (specification-only update)
- 📁 Files: 1 file modified (specs/002-perpetua-frontend/spec.md)
- 🔁 Next prompts: `/sp.plan` to design implementation architecture with TDD workflow integrated, `/sp.tasks` to generate tasks in Red-Green-Refactor order
- 🧠 Reflection: Testing requirements are now explicit and comprehensive, covering all user stories, edge cases, and establishing clear quality bars (80% coverage, pre-commit hooks, CI gates). This creates a strong foundation for TDD implementation.

## Evaluation notes (flywheel)

- Failure modes observed: Initial markdown linting warnings (bold text as headings, missing blank lines) - fixed immediately
- Graders run and results (PASS/FAIL): Markdown linting PASS after fixes
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Validate that plan.md generation incorporates these testing requirements into architecture decisions and component design
