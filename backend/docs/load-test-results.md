# Load Test Results

**T387: Run load test and document results (SC-002)**

## Test Configuration

| Parameter         | Value                                  |
|-------------------|----------------------------------------|
| Tool              | k6 v0.50+                              |
| Script            | `tests/load/k6_script.js`             |
| Target VUs        | 1000 concurrent virtual users          |
| Ramp-up Strategy  | 10 → 100 → 500 → 1000 → 0             |
| Total Duration    | 5 minutes                              |
| Target URL        | `http://localhost:8000` (staging)       |

## How to Run

```bash
# Install k6 (if not installed)
# Windows: choco install k6
# macOS:   brew install k6
# Linux:   snap install k6

# Run with default settings
k6 run tests/load/k6_script.js

# Run with custom settings
k6 run --vus 1000 --duration 5m tests/load/k6_script.js

# Run against staging
BASE_URL=https://staging-api.perpetuaflow.app AUTH_TOKEN=<token> k6 run tests/load/k6_script.js
```

## Success Criteria Validated

### SC-002: 1000 Concurrent Users

| Metric              | Target    | Result  | Status  |
|---------------------|-----------|---------|---------|
| Max concurrent VUs  | 1000      | PENDING | PENDING |
| HTTP error rate     | < 0.1%    | PENDING | PENDING |
| Connection failures | 0         | PENDING | PENDING |

### SC-003: API Response Latency (p95 < 500ms)

| Endpoint           | p50 (ms)  | p95 (ms)  | p99 (ms)  | Status  |
|--------------------|-----------|-----------|-----------|---------|
| GET /tasks         | PENDING   | PENDING   | PENDING   | PENDING |
| POST /tasks        | PENDING   | PENDING   | PENDING   | PENDING |
| PATCH /tasks/:id   | PENDING   | PENDING   | PENDING   | PENDING |
| DELETE /tasks/:id   | PENDING   | PENDING   | PENDING   | PENDING |
| GET /health/live   | PENDING   | PENDING   | PENDING   | PENDING |

### SC-004: Task CRUD 99.9% Success Rate

| Operation | Success Rate | Target   | Status  |
|-----------|-------------|----------|---------|
| Create    | PENDING     | > 99.9%  | PENDING |
| Read      | PENDING     | > 99.9%  | PENDING |
| Update    | PENDING     | > 99.9%  | PENDING |
| Delete    | PENDING     | > 99.9%  | PENDING |
| Overall   | PENDING     | > 99.9%  | PENDING |

## Resource Utilization During Test

| Resource    | Idle  | Peak Load | Status  |
|-------------|-------|-----------|---------|
| CPU         | ~5%   | PENDING   | PENDING |
| Memory      | ~200MB| PENDING   | PENDING |
| DB Conns    | 5     | PENDING   | PENDING |
| Response/s  | N/A   | PENDING   | PENDING |

## Notes

- Results marked PENDING until load test is executed against a running instance
- Load tests require a deployed backend with database (not in-memory SQLite)
- k6 outputs detailed JSON results to `docs/load-test-results.json`
- Run load tests in a staging environment, never against production

## Recommendations

1. **Database Connection Pooling**: Ensure pool_size (5) and max_overflow (10) handle 1000 VUs
2. **Rate Limiting**: Verify slowapi limits don't interfere with load test (may need test bypass)
3. **Database**: Use PostgreSQL (Neon) for realistic results, not SQLite
4. **Baseline**: Establish baseline metrics before optimization efforts

---

**Last Updated**: PENDING (run k6 to populate)
**Test Environment**: PENDING
