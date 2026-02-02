# Observability Setup

This document describes the observability infrastructure for the Perpetua Flow Backend API, covering logging, metrics, health checks, and activity auditing.

## Overview

The backend implements comprehensive observability following FR-065, FR-066, and FR-067:

- **Structured Logging (FR-065)**: JSON-formatted logs with request correlation
- **Prometheus Metrics (FR-066)**: Application metrics exposed for monitoring
- **Health Checks (FR-067)**: Liveness and readiness probes for orchestration
- **Activity Auditing (FR-052)**: Immutable audit trail of all user actions

## Health Checks

### Liveness Probe

**Endpoint**: `GET /health/live`

Returns 200 OK if the service process is running. Used by orchestrators to determine if the service should be restarted.

```json
{
  "status": "ok"
}
```

### Readiness Probe

**Endpoint**: `GET /health/ready`

Verifies the service can handle requests by checking:
- Database connectivity
- Essential configuration loading

Returns 200 OK when ready, 503 Service Unavailable when not ready.

```json
{
  "status": "ok",
  "checks": {
    "database": { "status": "ok" },
    "configuration": { "status": "ok" }
  }
}
```

## Metrics

### Prometheus Endpoint

**Endpoint**: `GET /metrics`

Exposes all application metrics in Prometheus text format for scraping.

### Available Metrics

#### HTTP Request Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `http_request_latency_seconds` | Histogram | method, path, status | Request duration |
| `http_request_count_total` | Counter | method, path, status | Total requests |
| `http_error_count_total` | Counter | method, path, status | Error responses (4xx/5xx) |
| `http_active_requests` | Gauge | method, path | Currently active requests |

#### Task Operation Metrics (T130)

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `task_operations_total` | Counter | operation, tier | Task operations by type |
| `task_completions_total` | Counter | completed_by | Task completions by method |
| `task_deletions_total` | Counter | deletion_type | Task deletions (soft/hard) |
| `task_version_conflicts_total` | Counter | - | Optimistic locking conflicts |
| `task_limit_reached_total` | Counter | tier | Task limit violations |
| `task_due_date_exceeded_total` | Counter | - | Due date validation failures |

#### Subtask Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `subtask_operations_total` | Counter | operation, tier | Subtask operations |
| `subtask_limit_reached_total` | Counter | tier | Subtask limit violations |
| `task_auto_completed_total` | Counter | - | Auto-completions triggered |
| `subtasks_per_task` | Histogram | - | Subtask count distribution |

#### Note Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `note_operations_total` | Counter | operation, tier | Note operations |
| `note_limit_reached_total` | Counter | tier | Note limit violations |
| `voice_note_operations_total` | Counter | operation | Voice note operations |
| `voice_note_duration_seconds` | Histogram | - | Voice note durations |
| `note_to_task_conversions_total` | Counter | - | Note-to-task conversions |

#### Reminder Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `reminder_operations_total` | Counter | operation | Reminder CRUD operations |
| `reminder_fired_total` | Counter | method | Reminders triggered |
| `reminder_latency_seconds` | Histogram | - | Fire delay from scheduled time |
| `reminder_skipped_total` | Counter | - | Skipped (recovered task) |

#### AI Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `ai_credits_consumed_total` | Counter | operation | AI credit consumption |
| `ai_subtask_generation_requests_total` | Counter | - | Generation requests |
| `ai_subtask_generation_latency_seconds` | Histogram | - | Generation duration |
| `ai_subtasks_generated` | Histogram | - | Subtasks per generation |
| `ai_subtask_generation_failures_total` | Counter | - | Generation failures |

#### Credit System Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `credit_grants_total` | Counter | credit_type | Credits granted |
| `credit_consumption_total` | Counter | operation, credit_type | Credits consumed |
| `credit_expirations_total` | Counter | credit_type | Credits expired |
| `credit_carryover_total` | Counter | - | Credits carried over |
| `insufficient_credits_total` | Counter | operation | Insufficient balance errors |
| `credit_balance` | Gauge | user_id, credit_type | Current balances |

#### Subscription/Webhook Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `webhook_events_processed_total` | Counter | event_type, status | Webhook processing |
| `webhook_processing_latency_seconds` | Histogram | - | Webhook latency |
| `subscription_status_changes_total` | Counter | from_status, to_status | Status transitions |
| `payment_failures_total` | Counter | retry_count | Payment failures |
| `credit_purchases_total` | Counter | status | Credit purchases |

#### Recovery Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `recovery_operations_total` | Counter | operation, status | Recovery operations |
| `recovery_latency_seconds` | Histogram | - | Recovery duration |

### Prometheus Configuration

Example `prometheus.yml` configuration:

```yaml
scrape_configs:
  - job_name: 'perpetua-backend'
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

## Structured Logging

### Format

All logs are emitted in JSON format with the following fields:

```json
{
  "timestamp": "2026-01-28T12:34:56.789Z",
  "level": "info",
  "logger": "src.services.task_service",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "Task created",
  "event": "task.created",
  "task_id": "789e0123-e89b-12d3-a456-426614174000"
}
```

### Request Logging

The logging middleware captures:

- **request_started**: Method, path, query params, client IP
- **request_completed**: Status code, duration in milliseconds
- **request_failed**: Exception details with stack trace

### Excluded Paths

The following paths are excluded from request logging to reduce noise:

- `/health/live`
- `/health/ready`
- `/metrics`

### Log Levels

| Level | Usage |
|-------|-------|
| `DEBUG` | Detailed diagnostic information |
| `INFO` | Normal operational events |
| `WARNING` | Unexpected but recoverable situations |
| `ERROR` | Errors that need attention |
| `CRITICAL` | Service-impacting failures |

### Configuration

Set log level via environment variable:

```bash
LOG_LEVEL=INFO  # Default
LOG_LEVEL=DEBUG # For development
```

## Activity Auditing

### Activity Log

All user and system actions are recorded in the `activity_logs` table with:

- `user_id`: User context
- `entity_type`: Target entity (task, subtask, note, reminder, etc.)
- `entity_id`: Affected entity ID
- `action`: Action performed (e.g., `task_created`, `note_converted`)
- `source`: Who initiated (user, ai, system) - FR-054
- `metadata`: Action-specific context
- `request_id`: Request correlation ID
- `created_at`: Timestamp (UTC)

### Retention

Activity logs are retained for 30 days (FR-053). The `cleanup_job` runs daily to purge older entries.

### Activity API

**Endpoint**: `GET /api/v1/activity`

Query user activity logs with filtering:

- `entity_type`: Filter by entity type
- `action`: Filter by action
- `source`: Filter by source (user/ai/system)
- `entity_id`: Filter by specific entity

## Alerting Guidelines

### Recommended Alerts

| Alert | Condition | Severity |
|-------|-----------|----------|
| High Error Rate | `rate(http_error_count_total[5m]) > 0.05` | Warning |
| Slow Responses | `histogram_quantile(0.95, http_request_latency_seconds) > 0.5` | Warning |
| Database Unavailable | `readiness_check{check="database"} != 1` | Critical |
| AI Service Degraded | `rate(ai_subtask_generation_failures_total[5m]) > 0.1` | Warning |
| Webhook Processing Slow | `histogram_quantile(0.95, webhook_processing_latency_seconds) > 30` | Warning |
| Credit System Issues | `rate(insufficient_credits_total[5m]) > 10` | Info |

### SLA Metrics

Per success criteria:

| SC | Metric | Target |
|----|--------|--------|
| SC-003 | p95 API latency | < 500ms |
| SC-005 | p95 AI chat response | < 5s |
| SC-008 | p95 webhook processing | < 30s |
| SC-010 | p95 task recovery | < 30s |
| SC-012 | p95 push notification | < 60s |

## Development Setup

### Local Monitoring Stack

For local development with monitoring:

```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

### Viewing Logs

```bash
# View structured logs in development
python -m uvicorn src.main:app --log-level debug

# Parse JSON logs with jq
python -m uvicorn src.main:app 2>&1 | jq '.'
```

## Production Considerations

1. **Log Aggregation**: Use a log aggregator (e.g., Loki, Elasticsearch) for centralized logging
2. **Metric Storage**: Configure Prometheus with appropriate retention
3. **Alert Routing**: Set up alerting via Alertmanager or equivalent
4. **Dashboard**: Create Grafana dashboards for the key metrics
5. **Trace Correlation**: Use request_id to correlate logs across services

---

**Generated**: 2026-01-28
**Task**: T366 - Document observability setup
