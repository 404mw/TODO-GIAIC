# Grouped ADR Examples

## When to Group Decisions

Group related decisions into a single ADR when:

1. **They form a cohesive system** (e.g., authentication stack)
2. **They were decided together** (e.g., deployment choices)
3. **They have interdependencies** (e.g., database + ORM)
4. **They serve the same purpose** (e.g., monitoring/observability)

## When to Separate Decisions

Create separate ADRs when:

1. **Decisions are independent** (can be changed separately)
2. **Different teams/concerns** (frontend vs backend)
3. **Different timelines** (decided months apart)
4. **Unrelated domains** (auth vs caching)

## Grouped ADR Template

```
📋 MULTIPLE RELATED DECISIONS DETECTED

Decisions:
1. [Decision 1]
2. [Decision 2]
3. [Decision 3]
...

Grouping Recommendation:
[Explain why these should be documented together]

Significance Test (for group):
✓ Impact: [Collective long-term consequences]
✓ Alternatives: [Options considered for the system]
✓ Scope: [Cross-cutting influence of the group]

This decision group meets all three criteria for an ADR.

Suggested ADR:
Title: [system-name-architecture]
Command: /sp.adr [system-name-architecture]

Recommended Content:
- Context: [Overall need/problem]
- Decisions: [List all related decisions]
- Rationale: [Why this combination was chosen]
- Alternatives Considered: [Other approaches/stacks]
- Consequences: [Positive and negative]
- Tradeoffs: [Key tradeoffs made]

Document complete [system] architecture?

[A] Yes, create grouped ADR
[B] Defer for later
[C] Create separate ADRs for each decision
```

## Example 1: Authentication Stack (Group)

**Related Decisions:**
- JWT vs session-based auth
- Better Auth vs custom implementation
- httpOnly cookies vs localStorage
- Token lifetime and refresh strategy

**Why Group:** These form a cohesive authentication architecture that was designed as a system, not individual choices.

**Suggested ADR Title:** `authentication-architecture`

## Example 2: Deployment Stack (Group)

**Related Decisions:**
- DigitalOcean vs AWS vs Vercel
- Docker containers vs serverless
- Kubernetes vs Docker Compose
- CI/CD with GitHub Actions

**Why Group:** Deployment choices are interdependent and form a complete deployment strategy.

**Suggested ADR Title:** `deployment-infrastructure`

## Example 3: Monitoring & Observability (Group)

**Related Decisions:**
- Logging library (structlog)
- Metrics collection (Prometheus)
- Tracing (OpenTelemetry)
- Alerting (PagerDuty)

**Why Group:** These form a complete observability stack that works together.

**Suggested ADR Title:** `observability-stack`

## Example 4: Frontend State Management (Separate)

**Decision 1:** Next.js App Router vs Pages Router
**Decision 2:** Zustand for client state

**Why Separate:** These are independent choices. App Router was chosen for routing architecture, Zustand for client state. They don't depend on each other.

**Suggested ADR Titles:**
- `nextjs-app-router-adoption`
- `client-state-management`

## Example 5: Database + ORM (Group or Separate?)

**Decisions:**
- PostgreSQL for database
- SQLModel for ORM

**Analysis:**
- **Group if:** Chosen together as a package deal (SQLModel chosen because of Postgres)
- **Separate if:** Database chosen first, then ORM evaluated independently later

**Recommendation:** Usually GROUP - ORMs are tightly coupled to database choice.

**Suggested ADR Title:** `database-and-orm-selection`

## Grouped ADR Content Structure

```markdown
# ADR-XXX: [System Name] Architecture

## Status
Accepted

## Context
[Overall problem/need that required this system of decisions]

## Decisions

### 1. [Decision 1 Title]
**Chosen:** [Option selected]
**Rationale:** [Why this specific choice]

### 2. [Decision 2 Title]
**Chosen:** [Option selected]
**Rationale:** [Why this specific choice]

### 3. [Decision 3 Title]
**Chosen:** [Option selected]
**Rationale:** [Why this specific choice]

## Alternatives Considered

### Stack Option A
- Decision 1: [Alternative A1]
- Decision 2: [Alternative A2]
- Decision 3: [Alternative A3]
**Rejected because:** [Reason]

### Stack Option B
- Decision 1: [Alternative B1]
- Decision 2: [Alternative B2]
- Decision 3: [Alternative B3]
**Rejected because:** [Reason]

## Consequences

### Positive
- [Benefit 1]
- [Benefit 2]
- [Benefit 3]

### Negative
- [Drawback 1]
- [Drawback 2]
- [Drawback 3]

## Tradeoffs
- [Tradeoff 1]: Chose [A] over [B] because [reason]
- [Tradeoff 2]: Chose [X] over [Y] because [reason]

## Implementation Notes
[Any specific guidance for implementing this architecture]
```
