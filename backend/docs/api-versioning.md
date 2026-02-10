# API Versioning and Deprecation Policy

**Feature**: 003-perpetua-backend
**Reference**: FR-069, FR-069a, FR-069b, plan.md AD-006

## Versioning Strategy

All API endpoints use URL path versioning under `/api/v1/`.

### Current Version

- **v1**: Active, fully supported
- Base path: `/api/v1/`
- OpenAPI spec: `/openapi.json` (development only)

### Version Lifecycle

| Stage | Duration | Description |
|-------|----------|-------------|
| Active | Indefinite | Current version, receives features and fixes |
| Deprecated | 6 months minimum | Sunset header added, no new features |
| Sunset | After deprecation period | Endpoints return 410 Gone |

## Deprecation Process

When an endpoint is deprecated (FR-069a, FR-069b):

### 1. Response Headers

All deprecated endpoints include:

```
Deprecation: true
Sunset: Sat, 01 Aug 2026 00:00:00 GMT
Link: </api/v2/resource>; rel="successor-version"
```

### 2. Implementation

Deprecation headers are applied via the `@deprecated_endpoint` decorator:

```python
from src.middleware.deprecation import deprecated_endpoint

@router.get("/old-endpoint")
@deprecated_endpoint(sunset_date="2026-08-01", successor="/api/v2/new-endpoint")
async def old_endpoint():
    ...
```

### 3. Communication Timeline

1. **Announcement**: Deprecation notice in API changelog and response headers
2. **Warning period**: 3 months with `Deprecation: true` header
3. **Sunset date**: Published in `Sunset` header (minimum 6 months from deprecation)
4. **Removal**: Endpoint returns `410 Gone` after sunset date

## Backward Compatibility Rules

### No Breaking Changes Within a Version

The following are **not allowed** within a version:

- Removing fields from response bodies
- Changing field types (e.g., `string` to `number`)
- Renaming fields
- Changing required/optional status of request fields
- Removing endpoints
- Changing authentication requirements
- Modifying error response codes for existing scenarios

### Allowed Additive Changes

The following **are allowed** without a version bump:

- Adding new optional fields to request bodies
- Adding new fields to response bodies
- Adding new endpoints
- Adding new query parameters (optional)
- Adding new enum values (if clients handle unknown values)
- Adding new error codes for new scenarios

## Migration Guide Template

When introducing a new version:

1. Document all breaking changes
2. Provide request/response mapping between versions
3. Include code examples for both versions
4. Set deprecation and sunset headers on old version
5. Allow at least 6 months overlap

## Testing

API versioning is validated by:

- `tests/integration/test_api_versioning.py`: Verifies backward compatibility (T402b)
- `tests/integration/test_api_versioning.py`: Verifies deprecation headers (T402c)

### Contract Tests

```bash
# Run versioning tests
pytest tests/integration/test_api_versioning.py -v
```

## Current Deprecations

None. All endpoints are at v1 and active.
