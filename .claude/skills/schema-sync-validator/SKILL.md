---
name: schema-sync-validator
description: Ensures Zod (frontend) and Pydantic (backend) schemas stay perfectly aligned. Use when modifying schemas, adding fields, changing types, or updating validation rules across the stack.
allowed-tools: Read, Grep, Glob
---

# Schema Sync Validator

## Purpose

Enforce schema consistency between frontend (Zod) and backend (Pydantic/SQLModel) per Constitution Section VII. Prevent type mismatches that cause runtime errors and API contract violations.

## Tech Stack (from Project_Outline.md)

- **Frontend:** Next.js + TypeScript + Zod validation
- **Backend:** FastAPI + SQLModel (Pydantic) + Neon DB (PostgreSQL)

## Instructions

### When Schema Changes Detected

On any request to modify data types, add fields, or change validation:

1. **Identify both schemas**
   - Frontend: Search for Zod schemas (`.ts` files with `z.object`)
   - Backend: Search for Pydantic/SQLModel models (`.py` files with `BaseModel` or `SQLModel`)

2. **Read both schemas completely**
   - Load current frontend schema
   - Load current backend schema

3. **Compare field-by-field**
   - Run alignment checks (see below)
   - See: `.claude/skills/schema-sync-validator/type-mappings.md` for complete type mapping table

4. **Report mismatches or confirm alignment**

5. **Propose synchronized updates**
   - Present changes for BOTH sides simultaneously

### Alignment Checks

For each field in the schema:

#### ✅ Field Name Alignment
- Frontend and backend field names MUST match exactly
- Python `snake_case` should map to TypeScript `camelCase` (be consistent)
- Check: Do both schemas have the same fields?

#### ✅ Type Alignment
- Zod types must match Pydantic types
- See: `.claude/skills/schema-sync-validator/type-mappings.md` for complete mapping table

**Quick reference:**
- `str` → `z.string()`
- `int` → `z.number().int()`
- `UUID` → `z.string().uuid()`
- `datetime` → `z.string().datetime()`
- `Optional[T]` → `.optional()`
- `Literal["a", "b"]` → `z.enum(["a", "b"])`

#### ✅ Validation Rule Alignment
- String length constraints must match
- Number range constraints must match
- Regex patterns must match
- Email/URL validators must match
- Custom validation logic must be equivalent

#### ✅ Optional/Required Alignment
- Required fields on backend → required in Zod
- Optional fields on backend → `.optional()` in Zod
- Default values should match (or be documented if different)

#### ✅ Enum Alignment
- Enum values must be identical
- Order doesn't matter, but values must match exactly

## Response Format

For detailed response templates, see: `.claude/skills/schema-sync-validator/examples.md`

### When Misalignment Detected
```
🚫 SCHEMA MISALIGNMENT DETECTED
[List mismatches with specific issues]
[Propose synchronized update for both schemas]
```

### When Schemas Aligned
```
✅ SCHEMA ALIGNMENT VERIFIED
[List verified fields]
Proceeding with changes...
```

### When Proposing Updates
```
📋 SYNCHRONIZED SCHEMA UPDATE PROPOSAL
[Show backend + frontend changes together]
[Verify alignment]
Approve synchronized update?
```

## Sub-Modules (Progressive Disclosure)

When you need detailed information, read these files:

- **Type Mappings**: `.claude/skills/schema-sync-validator/type-mappings.md`
  - Complete Pydantic ↔ Zod type mapping table
  - Validation rule equivalents
  - Common patterns (Optional, datetime, enums)

- **Detailed Examples**: `.claude/skills/schema-sync-validator/examples.md`
  - Catching string length mismatch
  - Detecting missing field
  - Enum value mismatch
  - Complete synchronized update examples

## Common Patterns

### Pattern: New Entity Schema

When creating a new entity (e.g., Tag, Category):

1. Define backend SQLModel first (source of truth for DB)
2. Immediately create matching Zod schema
3. Run alignment check before any API code
4. Document the schema in spec.md

### Pattern: Optional vs Required

```python
# Backend
description: Optional[str] = Field(default=None)  # Optional
```

```typescript
// Frontend - CORRECT
description: z.string().optional()

// Frontend - WRONG (makes it required)
description: z.string()
```

### Pattern: Datetime Handling

```python
# Backend
created_at: datetime = Field(default_factory=datetime.utcnow)
```

```typescript
// Frontend - use ISO 8601 string
createdAt: z.string().datetime()  // Validates ISO 8601 format
```

## Notes

- Run this check BEFORE implementing schema changes
- Backend schema is typically source of truth (it's backed by database)
- TypeScript types should be inferred from Zod: `type Task = z.infer<typeof TaskSchema>`
- Schema misalignment is a **blocking defect** - must be fixed immediately
- **Read sub-modules on-demand** to avoid context bloat
