# ADR Suggester Examples

## Example 1: Framework Selection (ADR Needed)

### User Question
"Should we use FastAPI or Flask for the backend?"

### After Discussion and Decision

```
📋 ARCHITECTURAL DECISION DETECTED

Decision: Use FastAPI for backend API framework
Context: Building REST API for TODO app, need performance and async support

Significance Test:
✓ Impact: Long-term consequences
  - Defines API development patterns for entire project
  - Affects performance characteristics
  - Determines available ecosystem (Pydantic, SQLModel, etc.)
  - Hard to change later (would require rewriting all endpoints)

✓ Alternatives: Multiple viable options considered
  - FastAPI: Modern, async, auto-docs, type hints, Pydantic integration
  - Flask: Mature, simple, large ecosystem, synchronous
  - Django: Full-featured, ORM included, but heavier than needed

✓ Scope: Cross-cutting influence
  - Affects all API endpoints
  - Influences frontend API client design
  - Determines deployment strategy (ASGI vs WSGI)
  - Sets precedent for async patterns throughout codebase

This decision meets all three criteria for an ADR.

Suggested ADR:
Title: backend-api-framework-selection
Command: /sp.adr backend-api-framework-selection

Recommended Content:
- Context: Need for REST API with async support
- Decision: FastAPI chosen
- Rationale:
  * Native async/await support
  * Automatic OpenAPI documentation
  * Pydantic integration (type safety)
  * Better performance than Flask
- Alternatives Considered:
  * Flask: Rejected due to lack of async and auto-docs
  * Django: Rejected as too heavyweight for API-only service
- Consequences:
  * Positive: Fast development, type safety, auto-docs
  * Negative: Smaller ecosystem than Flask, team learning curve
- Tradeoffs:
  * Speed vs maturity: Chose speed
  * Features vs simplicity: Chose features

Document reasoning and tradeoffs? Run /sp.adr backend-api-framework-selection
```

## Example 2: Variable Naming (No ADR)

### User Question
"Should we use camelCase or snake_case for Python variables?"

### Response

```
✓ Decision Analysis

Decision: Use snake_case for Python variables (following PEP 8)
Context: Code style consistency

Significance Test:
✓ Impact: Low - easily changed with automated refactoring
✗ Alternatives: No real alternatives (PEP 8 is standard)
✗ Scope: Not cross-cutting (doesn't influence architecture)

This decision does NOT meet ADR criteria.
No ADR needed - this is a code style guideline.

Rationale:
- Standard Python convention (PEP 8)
- No architectural implications
- Easily enforced with linter (black, ruff)
- No tradeoffs to document

Recommendation:
Add to code style guide or .editorconfig instead of ADR.
```

## Example 3: Database Selection (ADR Needed)

### User Statement
"We'll use PostgreSQL for the database"

### Response

```
📋 ARCHITECTURAL DECISION DETECTED

Decision: Use PostgreSQL as primary database
Context: Need persistent storage for TODO app data

Significance Test:
✓ Impact: Long-term consequences
  - Defines data storage layer for entire application
  - Affects query patterns, indexing strategies
  - Determines migration approach
  - Extremely expensive to change later

✓ Alternatives: Multiple viable options considered
  - PostgreSQL: Relational, ACID, mature, JSON support
  - MongoDB: Document-based, flexible schema
  - SQLite: Lightweight, file-based, simpler
  - MySQL: Relational, widely used

✓ Scope: Cross-cutting influence
  - Affects backend models (SQLModel/SQLAlchemy)
  - Influences API design (relationships, joins)
  - Determines deployment requirements (managed Postgres needed)
  - Sets precedent for data modeling approach

This decision meets all three criteria for an ADR.

Suggested ADR:
Title: primary-database-selection
Command: /sp.adr primary-database-selection

Recommended Content:
- Context: Need for reliable, scalable data persistence
- Decision: PostgreSQL (via Neon DB managed service)
- Rationale:
  * ACID compliance for data integrity
  * JSON/JSONB support for flexible fields
  * Strong ecosystem (SQLAlchemy, Alembic)
  * Managed hosting available (Neon DB)
  * Better for relational data than MongoDB
- Alternatives Considered:
  * MongoDB: Rejected due to lack of ACID guarantees, overkill for simple schema
  * SQLite: Rejected due to single-file limitations, not suitable for cloud
  * MySQL: Viable but Postgres has better JSON support
- Consequences:
  * Positive: Data integrity, mature tooling, JSON flexibility
  * Negative: Requires managed hosting ($), more complex than SQLite
- Tradeoffs:
  * Complexity vs reliability: Chose reliability
  * Cost vs features: Chose features

Document reasoning and tradeoffs? Run /sp.adr primary-database-selection
```

## Example 4: Component Styling (No ADR)

### User Statement
"I'll use flexbox for this component layout"

### Response

```
✓ Decision Analysis

Decision: Use flexbox for component layout
Context: Styling a specific UI component

Significance Test:
✓ Impact: Low - affects only this component, easily changed
✗ Alternatives: Grid is alternative, but flexbox is appropriate here
✗ Scope: Isolated to single component

This decision does NOT meet ADR criteria.
No ADR needed - this is an implementation detail.

Rationale:
- Component-level styling choice
- No project-wide implications
- Standard CSS technique
- Easily reversible

No documentation required - proceed with implementation.
```

## Example 5: Grouped ADR (Auth Stack)

### User Statement
"We'll use JWT tokens with Better Auth, stored in httpOnly cookies"

### Response

```
📋 MULTIPLE RELATED DECISIONS DETECTED

Decisions:
1. Authentication method: JWT-based tokens
2. Auth library: Better Auth
3. Token storage: httpOnly cookies (not localStorage)
4. Token lifetime: 7 days with refresh
5. Session management: Stateless (JWT claims only)

Grouping Recommendation:
These decisions form a cohesive authentication architecture
and should be documented together in a single ADR.

Significance Test (for group):
✓ Impact: Long-term consequences
  - Defines security model for entire application
  - Affects user experience (login flow, sessions)
  - Determines scalability (stateless vs stateful)
  - Hard to change without breaking existing users

✓ Alternatives: Multiple approaches considered
  - JWT (stateless): Chosen
  - Session-based (stateful): Rejected for scalability
  - OAuth 2.0: Deferred for future (social login)
  - Passwordless: Deferred for future (magic links)

✓ Scope: Cross-cutting influence
  - Affects frontend (login UI, API calls)
  - Affects backend (middleware, validation)
  - Affects database (user table, token tracking if needed)
  - Influences deployment (no session store needed)

This decision group meets all three criteria for an ADR.

Suggested ADR:
Title: authentication-architecture
Command: /sp.adr authentication-architecture

Recommended Content:
- Context: Need secure user authentication for TODO app
- Decisions:
  1. JWT tokens for stateless auth
  2. Better Auth library for implementation
  3. httpOnly cookies for XSS protection
  4. 7-day expiry with refresh token
  5. Stateless validation (no session DB)
- Rationale:
  * Stateless scales better than sessions
  * Better Auth provides modern patterns
  * httpOnly cookies prevent XSS attacks
  * Refresh tokens balance security and UX
- Alternatives Considered:
  * Session-based auth: Rejected (requires session store, doesn't scale)
  * localStorage for tokens: Rejected (vulnerable to XSS)
  * OAuth only: Deferred (will add later for social login)
- Consequences:
  * Positive: Scalable, secure, modern patterns
  * Negative: Cannot revoke tokens immediately, slightly complex
- Tradeoffs:
  * Stateless vs revocability: Chose stateless (use short expiry)
  * Security vs UX: Chose security (httpOnly cookies)

Document complete authentication architecture? Run /sp.adr authentication-architecture

[A] Yes, create grouped ADR
[B] Defer for later
```
