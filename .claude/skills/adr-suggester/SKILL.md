---
name: adr-suggester
description: Detects architecturally significant decisions and suggests ADR creation. Use during planning, architecture discussions, tech stack choices. Never auto-creates ADRs - always requires user consent.
allowed-tools: Read, Grep, Glob
---

# ADR Suggester

## Purpose

Detect architecturally significant decisions and suggest documentation via Architecture Decision Records (ADRs), following CLAUDE.md guidelines.

## ADR Suggestion Rule (from CLAUDE.md)

When significant architectural decisions are made, suggest:
```
📋 Architectural decision detected: <brief>
   Document reasoning and tradeoffs? Run `/sp.adr <decision-title>`
```

**Never auto-create ADRs** - require user consent.

## Three-Part Significance Test

A decision is architecturally significant if ALL three are true:

### 1. Impact
**Question:** Does this have long-term consequences?

**High-impact decisions:** Framework choice, database selection, authentication strategy, deployment platform, state management, API architecture, data migration, security model

**Low-impact decisions:** Variable naming, file organization, component styling, log format

### 2. Alternatives
**Question:** Were multiple viable options considered?

**Requires ADR:** Considered multiple options with tradeoffs (e.g., FastAPI vs Flask vs Django)

**No ADR needed:** Only one obvious option, trivial choice with no tradeoffs

### 3. Scope
**Question:** Is this cross-cutting and influential?

**Cross-cutting:** Affects multiple modules/layers, influences future choices, changes system structure, impacts team workflow

**Isolated:** Contained to single component, no ripple effects, easily reversible

## Instructions

### During Planning / Architecture Work

When analyzing user requests or planning:

1. **Identify decision points**
   - Technology selections
   - Architectural patterns
   - Tradeoff discussions

2. **Apply three-part test**
   - Impact: Long-term consequences?
   - Alternatives: Multiple options considered?
   - Scope: Cross-cutting influence?

3. **If ALL three are true → Suggest ADR**
   - Present brief description
   - Ask for consent
   - Provide suggested title

4. **Group related decisions**
   - Authentication stack (method + library + flow) → one ADR
   - Database choice + ORM selection → one ADR
   - Deployment (platform + orchestration + CI/CD) → one ADR

5. **Wait for user consent**
   - Never auto-create
   - User must run `/sp.adr <title>`

## Response Format

### When Significance Detected

```
📋 ARCHITECTURAL DECISION DETECTED

Decision: [Brief description]
Context: [Why this decision is being made]

Significance Test:
✓ Impact: [Long-term consequences described]
✓ Alternatives: [Options considered]
✓ Scope: [Cross-cutting influence]

This decision meets all three criteria for an ADR.

Suggested ADR:
Title: [proposed-title]
Command: /sp.adr [proposed-title]

Document reasoning and tradeoffs?

Options:
[A] Yes, create ADR now (run /sp.adr)
[B] Defer ADR creation (document later)
[C] No, decision not significant enough
```

### When NOT Significant

```
✓ Decision Analysis

Decision: [Brief description]

Significance Test:
✓ Impact: [Assessment]
✗ Alternatives: Only one viable option
✗ Scope: Isolated to single component

This decision does NOT meet ADR criteria.
No ADR needed - proceeding with implementation.

Rationale: [Why ADR is not required]
```

### When Suggesting Grouped ADR

See: `.claude/skills/adr-suggester/grouped-adr-examples.md` for complete grouped ADR template

## Sub-Modules (Progressive Disclosure)

When you need detailed information, read these files:

- **Detailed Examples**: `.claude/skills/adr-suggester/examples.md`
  - Framework selection (ADR needed)
  - Variable naming (No ADR)
  - Database selection (ADR needed)
  - Component styling (No ADR)

- **Grouped ADR Guide**: `.claude/skills/adr-suggester/grouped-adr-examples.md`
  - Multiple related decisions → single ADR
  - Authentication stack example
  - When to group vs separate

## When to Suggest ADRs

### ✅ Suggest ADR For:
- Framework/library selections (FastAPI, Next.js, Better Auth)
- Database choices (PostgreSQL, MongoDB, Redis)
- Architectural patterns (microservices, monolith, event-driven)
- Deployment strategies (Docker, Kubernetes, serverless)
- Authentication/authorization approaches
- State management solutions (Redux, Context, Zustand)
- API design (REST vs GraphQL)
- Major refactorings that change architecture
- Security model decisions
- Data migration strategies

### ❌ Do NOT Suggest ADR For:
- Code style preferences (naming, formatting)
- Component-level implementation details
- Variable/function names
- File organization within a module
- Specific CSS techniques
- Log message format
- Trivial library choices (date formatting, etc.)
- Bug fixes that don't change architecture
- Obvious choices with no alternatives
- Reversible decisions with low impact

## Timing

Suggest ADRs:
- **During /sp.plan** (planning phase) - Most common
- **During /sp.tasks** (if decisions emerge)
- **Ad-hoc** (when user asks for architecture advice)

Do NOT suggest during:
- **/sp.implement** (too late - decision already made)
- **/sp.specify** (too early - architecture not designed yet)

## Notes

- ADR suggestions are **optional** - user can decline
- Group related decisions into single ADR
- Suggestion ≠ creation (user must consent)
- ADRs document **why**, not **what** (what goes in spec)
- Follow CLAUDE.md: "Wait for consent; never auto-create the ADR"
- **Read sub-modules on-demand** to avoid context bloat
