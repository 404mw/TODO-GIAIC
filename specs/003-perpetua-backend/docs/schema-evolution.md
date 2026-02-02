# Schema Evolution Process

**T384: Document schema evolution process**

This document describes the process for evolving API schemas, database models, and contracts in the Perpetua Flow Backend. Following these guidelines ensures backward compatibility, smooth migrations, and aligned frontend/backend development.

## Overview

Schema evolution involves changes to:
- **Pydantic schemas** (backend request/response types)
- **SQLModel models** (database tables)
- **OpenAPI specification** (API contract)
- **TypeScript types** (frontend contract)
- **AI agent output schemas** (structured AI responses)

## Guiding Principles

### 1. Backward Compatibility Within Major Versions (FR-069)

Within a major version (e.g., `/api/v1/`), changes must be backward-compatible:

**Allowed Changes (Non-Breaking):**
- ✅ Adding optional fields (with defaults)
- ✅ Adding new endpoints
- ✅ Adding new enum values (if clients handle unknown values gracefully)
- ✅ Relaxing validation (e.g., increasing max length)
- ✅ Adding new response fields
- ✅ Adding optional query parameters

**Disallowed Changes (Breaking):**
- ❌ Removing fields from responses
- ❌ Renaming fields
- ❌ Changing field types
- ❌ Making optional fields required
- ❌ Removing endpoints
- ❌ Tightening validation on existing fields
- ❌ Changing authentication requirements

### 2. Deprecation Policy (FR-069a, FR-069b)

- **Minimum 90-day notice** before removing any endpoint or field within a major version
- Deprecated endpoints return `Deprecation` header with sunset date per RFC 8594
- Documentation clearly marks deprecated features with migration guidance

### 3. Versioning Strategy (AD-005)

- URL path versioning: `/api/v1/`, `/api/v2/`, etc.
- Major version increment for breaking changes
- New major versions can coexist during migration period

## Schema Change Workflow

### Step 1: Propose the Change

1. **Document the change** in a GitHub issue or PR:
   - What is changing and why
   - Impact analysis (breaking vs non-breaking)
   - Migration path for clients

2. **Check compatibility:**
   ```bash
   # Run contract tests to verify no breaking changes
   pytest tests/contract/ -v
   ```

### Step 2: Update Backend Schemas

1. **Update Pydantic schemas** in `backend/src/schemas/`:
   ```python
   # Example: Adding optional field (non-breaking)
   class TaskResponse(BaseModel):
       id: UUID
       title: str
       # NEW: Optional field with default
       tags: list[str] | None = None
   ```

2. **Update SQLModel models** in `backend/src/models/` if database change needed:
   ```python
   class TaskInstance(BaseSQLModel, table=True):
       # Existing fields...
       # NEW: Add column with default for existing rows
       tags: list[str] = Field(default_factory=list, sa_column=Column(ARRAY(String)))
   ```

3. **Create Alembic migration** for database changes:
   ```bash
   cd backend
   alembic revision --autogenerate -m "add_tags_to_tasks"
   # Review and edit the generated migration
   alembic upgrade head
   ```

### Step 3: Update Contract Artifacts

1. **Regenerate OpenAPI spec:**
   ```bash
   cd backend
   python scripts/generate_openapi.py -o ../specs/003-perpetua-backend/contracts/openapi.yaml
   ```

2. **Update TypeScript types** in `contracts/types.ts`:
   ```typescript
   export interface TaskResponse {
     id: string;
     title: string;
     // NEW: Optional field
     tags?: string[] | null;
   }
   ```

3. **Update snapshot tests** if AI schemas changed:
   ```bash
   # Delete old snapshot to regenerate
   rm backend/tests/contract/snapshots/task_suggestion.json
   pytest backend/tests/contract/test_ai_schemas.py -v
   ```

### Step 4: Validate Changes

1. **Run all contract tests:**
   ```bash
   pytest backend/tests/contract/ -v
   ```

2. **Run schemathesis fuzz tests:**
   ```bash
   pytest backend/tests/contract/test_*_fuzz.py -v
   ```

3. **Validate TypeScript types compile:**
   ```bash
   cd frontend
   npx tsc --noEmit
   ```

### Step 5: Communicate Changes

1. **Update API changelog** (if maintained)
2. **Notify frontend team** of new fields/endpoints
3. **Update SDK documentation** if applicable

## Database Migration Guidelines

### Safe Migrations (Online, No Downtime)

```python
# Adding nullable column
op.add_column('task_instances', Column('tags', ARRAY(String), nullable=True))

# Adding index concurrently (PostgreSQL)
op.execute('CREATE INDEX CONCURRENTLY idx_tasks_tags ON task_instances USING GIN (tags)')
```

### Migrations Requiring Coordination

```python
# Renaming column (requires application coordination)
# 1. Add new column
op.add_column('task_instances', Column('new_name', String, nullable=True))
# 2. Migrate data
op.execute('UPDATE task_instances SET new_name = old_name')
# 3. Deploy code using both columns
# 4. After deployment, drop old column
```

### Irreversible Migrations

Always include downgrade path when possible:

```python
def upgrade():
    op.add_column('users', Column('preferences', JSONB, default='{}'))

def downgrade():
    op.drop_column('users', 'preferences')
```

## AI Schema Evolution

AI agent output schemas require special care because they affect:
- Frontend parsing of AI responses
- AI agent system prompts
- Contract tests and snapshots

### Updating AI Schemas

1. **Update Pydantic schema** in `backend/src/schemas/ai_agents.py`:
   ```python
   class SubtaskSuggestion(BaseModel):
       title: str = Field(max_length=200)
       # NEW: Optional rationale
       rationale: str | None = Field(default=None, max_length=500)
   ```

2. **Update agent system prompt** if the change affects output format

3. **Update snapshot tests:**
   ```bash
   # Regenerate snapshots
   rm backend/tests/contract/snapshots/*.json
   pytest backend/tests/contract/test_ai_schemas.py -v
   ```

4. **Update TypeScript types** in `contracts/types.ts`

## Deprecation Process

### Marking an Endpoint Deprecated

1. **Add deprecation header middleware:**
   ```python
   @app.get("/api/v1/old-endpoint", deprecated=True)
   async def old_endpoint():
       response.headers["Deprecation"] = "@2026-05-01"
       response.headers["Sunset"] = "Sat, 01 May 2026 00:00:00 GMT"
       response.headers["Link"] = '</api/v1/new-endpoint>; rel="successor-version"'
       return ...
   ```

2. **Document in OpenAPI:**
   ```yaml
   /api/v1/old-endpoint:
     get:
       deprecated: true
       x-sunset-date: "2026-05-01"
       description: |
         **Deprecated**: Use `/api/v1/new-endpoint` instead.
         This endpoint will be removed on 2026-05-01.
   ```

3. **Log usage for monitoring:**
   ```python
   logger.warning(
       "Deprecated endpoint accessed",
       endpoint="/api/v1/old-endpoint",
       user_id=user.id,
   )
   ```

### Timeline

| Day | Action |
|-----|--------|
| 0 | Add deprecation header, update docs |
| 30 | First reminder in release notes |
| 60 | Second reminder, warn in logs |
| 90+ | Remove endpoint in next major release |

## Contract Testing Strategy

### Automated Checks

1. **Schema validation** via schemathesis fuzz tests
2. **Snapshot tests** for AI output schemas
3. **TypeScript compilation** in CI
4. **OpenAPI spec diffing** to detect unintentional changes

### CI Integration

```yaml
# .github/workflows/contract-tests.yml
contract-tests:
  steps:
    - name: Run contract tests
      run: pytest backend/tests/contract/ -v

    - name: Verify TypeScript types
      run: |
        cd frontend
        npx tsc --noEmit

    - name: Check OpenAPI changes
      run: |
        python backend/scripts/generate_openapi.py -o /tmp/openapi-new.yaml
        diff specs/003-perpetua-backend/contracts/openapi.yaml /tmp/openapi-new.yaml
```

## Tools and Resources

### Schema Generation

- **OpenAPI from FastAPI:** `python scripts/generate_openapi.py`
- **TypeScript from OpenAPI:** `openapi-typescript` or manual sync

### Validation

- **Contract testing:** schemathesis, pytest
- **Schema diff:** `oasdiff` for OpenAPI comparison
- **Type checking:** TypeScript compiler, Pydantic validation

### References

- [RFC 8594 - Sunset Header](https://www.rfc-editor.org/rfc/rfc8594)
- [JSON Schema Compatibility](https://json-schema.org/understanding-json-schema/reference/version)
- [Pydantic V2 Migration Guide](https://docs.pydantic.dev/latest/migration/)
- [Alembic Auto-Generation](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)

---

**Last Updated:** 2026-01-28
**Related Documents:**
- [API Specification](api-specification.md)
- [Data Model](data-model.md)
- [OpenAPI Spec](../contracts/openapi.yaml)
- [TypeScript Types](../contracts/types.ts)
