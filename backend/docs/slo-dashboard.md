# SLO Dashboard & Uptime Monitoring Strategy

**T397: Document uptime monitoring strategy (SC-009)**

## Service Level Objectives (SLOs)

| SLO ID  | Metric                           | Target   | Window  | Budget   |
|---------|----------------------------------|----------|---------|----------|
| SC-001  | OAuth sign-in latency            | < 10s    | Rolling | N/A      |
| SC-002  | Concurrent user capacity         | 1000 VUs | Peak    | N/A      |
| SC-003  | API p95 latency                  | < 500ms  | 5m      | 5%       |
| SC-004  | Task CRUD success rate           | 99.9%    | 5m      | 0.1%     |
| SC-005  | AI chat p95 latency              | < 5s     | 5m      | 5%       |
| SC-006  | Data integrity (zero corruption) | 100%     | Always  | 0%       |
| SC-007  | Streak calculation accuracy      | 100%     | Always  | 0%       |
| SC-008  | Webhook processing time          | < 30s    | 5m      | 5%       |
| SC-009  | Monthly uptime                   | 99.5%    | 30d     | 0.5%     |
| SC-010  | Task recovery time               | < 30s    | 5m      | 5%       |
| SC-011  | Credit balance consistency       | < 5s     | Always  | 0%       |
| SC-012  | Push notification delivery       | 95%<60s  | 5m      | 5%       |

## Uptime Monitoring Architecture

### 1. Health Check Endpoints

```text
GET /api/v1/health/live     → Liveness probe (is process running?)
GET /api/v1/health/ready    → Readiness probe (can serve traffic?)
GET /metrics                → Prometheus metrics endpoint
```

### 2. External Uptime Monitoring

**Recommended Tools**: UptimeRobot, Better Uptime, or Checkly

**Configuration**:

| Monitor            | URL                          | Interval | Alert After |
|--------------------|------------------------------|----------|-------------|
| API Liveness       | `{BASE}/api/v1/health/live`  | 60s      | 2 failures  |
| API Readiness      | `{BASE}/api/v1/health/ready` | 120s     | 3 failures  |
| Worker Liveness    | `{WORKER}/health`            | 120s     | 3 failures  |
| OAuth Flow         | Synthetic: login flow        | 300s     | 2 failures  |

### 3. Internal Monitoring Stack

```text
Application → Prometheus Metrics → Prometheus Server → Grafana Dashboard
     ↓
Structured Logs → Log Aggregation (Railway Logs / Datadog)
     ↓
Alerting Rules → PagerDuty / Slack / Email
```

### 4. Key Dashboards

#### 4.1 Overview Dashboard
- Request rate (req/s) by endpoint
- Error rate (%) by status code
- p50/p95/p99 latency by endpoint category
- Active database connections
- Worker job queue depth

#### 4.2 SLO Dashboard
- SC-003: API latency heatmap with p95 line at 500ms
- SC-004: Task CRUD success rate gauge (target: 99.9%)
- SC-005: AI chat latency distribution
- SC-009: Monthly uptime percentage
- Error budget remaining for each SLO

#### 4.3 Business Metrics Dashboard
- Active users (daily/weekly/monthly)
- Task operations per hour
- AI credit consumption rate
- Subscription conversion/churn
- Achievement unlock rate

## Uptime Calculation

### Formula

```
Monthly Uptime % = (total_minutes - downtime_minutes) / total_minutes × 100
```

### Error Budget

| Uptime Target | Monthly Downtime Budget | Weekly Budget |
|---------------|------------------------|---------------|
| 99.5%         | 3h 36m                 | 50m           |
| 99.9%         | 43m                    | 10m           |
| 99.95%        | 21m                    | 5m            |

**SC-009 Target: 99.5% monthly uptime = 3h 36m downtime budget**

### Downtime Detection

1. **Synthetic Monitoring**: External probes every 60s
2. **Real User Monitoring**: Client-side error tracking
3. **Internal Health**: Readiness probe failures

A downtime incident starts when:
- Readiness probe fails for ≥2 consecutive checks (120s)
- OR error rate exceeds 50% for ≥60s
- OR p95 latency exceeds 10x target for ≥120s

## Alerting Escalation

### Severity Levels

| Level    | Response Time | Channel           | Examples                          |
|----------|---------------|-------------------|-----------------------------------|
| Info     | Next business | Slack #monitoring | p95 approaching threshold         |
| Warning  | 4 hours       | Slack + Email     | SLO budget 50% consumed           |
| Critical | 30 minutes    | PagerDuty + Slack | Service down, data integrity risk |

### Escalation Path

```
1. Alert fires → Slack #perpetua-alerts
2. After 15m unack → Email to on-call
3. After 30m unack → PagerDuty page
4. After 60m unack → Escalate to team lead
```

## Incident Response

### Runbook Templates

Located at `docs/runbooks/`:
- `high-latency.md` - API latency exceeds thresholds
- `ai-latency.md` - AI service degradation
- `webhook-processing.md` - Payment webhook failures
- `task-recovery.md` - Recovery operation failures
- `notification-delivery.md` - Push notification delays
- `database-connection.md` - Database connectivity issues

### Post-Incident

1. Create incident report within 24 hours
2. Update SLO dashboard with incident timeline
3. Identify corrective actions
4. Update runbooks with lessons learned

## Deployment Strategy for Uptime

### Zero-Downtime Deployments

1. **Rolling Updates**: Railway's default deployment strategy
2. **Health Check Gates**: New instance must pass readiness before routing
3. **Database Migrations**: Run before code deploy (backwards compatible)
4. **Feature Flags**: Toggle new features without deploy

### Rollback Plan

1. **Automated**: If readiness probe fails within 5m of deploy → auto-rollback
2. **Manual**: `railway rollback` to previous deployment
3. **Database**: Alembic `downgrade -1` for schema rollback

---

**Last Updated**: 2026-02-01
**Owner**: Platform Team
**Review Cadence**: Monthly SLO review meeting
