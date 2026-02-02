/**
 * k6 Load Test Script for Perpetua Flow Backend API
 *
 * T386: k6 load test for 1000 concurrent users (SC-002)
 * T390: Task CRUD 99.9% success rate under load (SC-004)
 *
 * Usage:
 *   k6 run tests/load/k6_script.js
 *   k6 run --vus 1000 --duration 5m tests/load/k6_script.js
 *
 * Environment Variables:
 *   BASE_URL:    Target server URL (default: http://localhost:8000)
 *   AUTH_TOKEN:  Bearer token for authenticated requests
 */

import http from "k6/http";
import { check, sleep, group } from "k6";
import { Rate, Trend, Counter } from "k6/metrics";

// =============================================================================
// CUSTOM METRICS
// =============================================================================

const taskCreateSuccess = new Rate("task_create_success");
const taskReadSuccess = new Rate("task_read_success");
const taskUpdateSuccess = new Rate("task_update_success");
const taskDeleteSuccess = new Rate("task_delete_success");
const overallSuccess = new Rate("overall_success_rate");
const apiLatency = new Trend("api_latency_ms", true);
const taskCRUDLatency = new Trend("task_crud_latency_ms", true);
const errorCount = new Counter("error_count");

// =============================================================================
// CONFIGURATION
// =============================================================================

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";
const AUTH_TOKEN = __ENV.AUTH_TOKEN || "";

const headers = {
  "Content-Type": "application/json",
  ...(AUTH_TOKEN ? { Authorization: `Bearer ${AUTH_TOKEN}` } : {}),
};

// SC-002: Load test for 1000 concurrent users
export const options = {
  scenarios: {
    // Ramp-up scenario for gradual load increase
    ramp_up: {
      executor: "ramping-vus",
      startVUs: 10,
      stages: [
        { duration: "30s", target: 100 },   // Warm up
        { duration: "1m", target: 500 },     // Medium load
        { duration: "2m", target: 1000 },    // Peak load (SC-002)
        { duration: "1m", target: 1000 },    // Sustain peak
        { duration: "30s", target: 0 },      // Ramp down
      ],
      gracefulRampDown: "10s",
    },
  },
  thresholds: {
    // SC-003: 95% of API responses < 500ms
    api_latency_ms: ["p(95)<500", "p(99)<1000"],
    // SC-004: 99.9% success rate for task CRUD
    overall_success_rate: ["rate>0.999"],
    task_create_success: ["rate>0.999"],
    task_read_success: ["rate>0.999"],
    task_update_success: ["rate>0.999"],
    task_delete_success: ["rate>0.999"],
    // Task CRUD latency
    task_crud_latency_ms: ["p(95)<500"],
    // HTTP errors
    http_req_failed: ["rate<0.001"],
  },
};

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

function randomPriority() {
  const priorities = ["low", "medium", "high", "urgent"];
  return priorities[Math.floor(Math.random() * priorities.length)];
}

function randomTaskTitle() {
  const prefixes = [
    "Review", "Implement", "Test", "Debug", "Deploy",
    "Document", "Refactor", "Optimize", "Configure", "Monitor",
  ];
  const suffixes = [
    "authentication module", "database queries", "API endpoints",
    "frontend components", "CI/CD pipeline", "unit tests",
    "performance metrics", "error handling", "logging system",
    "security headers",
  ];
  const prefix = prefixes[Math.floor(Math.random() * prefixes.length)];
  const suffix = suffixes[Math.floor(Math.random() * suffixes.length)];
  return `${prefix} ${suffix} - VU${__VU}`;
}

// =============================================================================
// TEST SCENARIOS
// =============================================================================

export default function () {
  // Health check (lightweight, no auth required)
  group("Health Checks", () => {
    const liveRes = http.get(`${BASE_URL}/api/v1/health/live`);
    apiLatency.add(liveRes.timings.duration);
    check(liveRes, { "liveness OK": (r) => r.status === 200 });
    overallSuccess.add(liveRes.status === 200);
  });

  // Task CRUD lifecycle
  group("Task CRUD", () => {
    // CREATE
    const createPayload = JSON.stringify({
      title: randomTaskTitle(),
      description: `Load test task created by VU ${__VU} iteration ${__ITER}`,
      priority: randomPriority(),
    });

    const createRes = http.post(`${BASE_URL}/api/v1/tasks`, createPayload, {
      headers,
    });
    apiLatency.add(createRes.timings.duration);
    taskCRUDLatency.add(createRes.timings.duration);

    const createOk = createRes.status === 200 || createRes.status === 201;
    taskCreateSuccess.add(createOk);
    overallSuccess.add(createOk);

    if (!createOk) {
      errorCount.add(1);
      return;
    }

    let taskId;
    try {
      taskId = createRes.json().id;
    } catch (e) {
      errorCount.add(1);
      return;
    }

    sleep(0.1); // Brief pause between operations

    // READ
    const readRes = http.get(`${BASE_URL}/api/v1/tasks/${taskId}`, { headers });
    apiLatency.add(readRes.timings.duration);
    taskCRUDLatency.add(readRes.timings.duration);

    const readOk = readRes.status === 200;
    taskReadSuccess.add(readOk);
    overallSuccess.add(readOk);

    if (!readOk) {
      errorCount.add(1);
    }

    sleep(0.1);

    // UPDATE
    const updatePayload = JSON.stringify({
      title: `Updated - ${randomTaskTitle()}`,
      priority: randomPriority(),
    });

    const updateRes = http.patch(
      `${BASE_URL}/api/v1/tasks/${taskId}`,
      updatePayload,
      { headers }
    );
    apiLatency.add(updateRes.timings.duration);
    taskCRUDLatency.add(updateRes.timings.duration);

    const updateOk = updateRes.status === 200;
    taskUpdateSuccess.add(updateOk);
    overallSuccess.add(updateOk);

    if (!updateOk) {
      errorCount.add(1);
    }

    sleep(0.1);

    // DELETE
    const deleteRes = http.del(`${BASE_URL}/api/v1/tasks/${taskId}`, null, {
      headers,
    });
    apiLatency.add(deleteRes.timings.duration);
    taskCRUDLatency.add(deleteRes.timings.duration);

    const deleteOk = deleteRes.status === 200 || deleteRes.status === 204;
    taskDeleteSuccess.add(deleteOk);
    overallSuccess.add(deleteOk);

    if (!deleteOk) {
      errorCount.add(1);
    }
  });

  // List tasks (pagination)
  group("Task Listing", () => {
    const listRes = http.get(
      `${BASE_URL}/api/v1/tasks?page=1&page_size=20`,
      { headers }
    );
    apiLatency.add(listRes.timings.duration);
    const listOk = listRes.status === 200;
    overallSuccess.add(listOk);
  });

  // Brief pause between iterations
  sleep(0.5 + Math.random() * 0.5);
}

// =============================================================================
// SUMMARY HANDLER
// =============================================================================

export function handleSummary(data) {
  const summary = {
    timestamp: new Date().toISOString(),
    test: "Perpetua Flow Backend Load Test",
    scenarios: {
      "SC-002": {
        description: "1000 concurrent users",
        target_vus: 1000,
        actual_max_vus: data.metrics.vus_max ? data.metrics.vus_max.values.max : 0,
      },
      "SC-003": {
        description: "API p95 latency < 500ms",
        p95_ms: data.metrics.api_latency_ms
          ? data.metrics.api_latency_ms.values["p(95)"]
          : null,
        p99_ms: data.metrics.api_latency_ms
          ? data.metrics.api_latency_ms.values["p(99)"]
          : null,
        passed:
          data.metrics.api_latency_ms &&
          data.metrics.api_latency_ms.values["p(95)"] < 500,
      },
      "SC-004": {
        description: "Task CRUD 99.9% success rate",
        success_rate: data.metrics.overall_success_rate
          ? data.metrics.overall_success_rate.values.rate
          : null,
        passed:
          data.metrics.overall_success_rate &&
          data.metrics.overall_success_rate.values.rate > 0.999,
      },
    },
    task_crud: {
      create_success: data.metrics.task_create_success
        ? data.metrics.task_create_success.values.rate
        : null,
      read_success: data.metrics.task_read_success
        ? data.metrics.task_read_success.values.rate
        : null,
      update_success: data.metrics.task_update_success
        ? data.metrics.task_update_success.values.rate
        : null,
      delete_success: data.metrics.task_delete_success
        ? data.metrics.task_delete_success.values.rate
        : null,
    },
    errors: data.metrics.error_count
      ? data.metrics.error_count.values.count
      : 0,
  };

  return {
    "docs/load-test-results.json": JSON.stringify(summary, null, 2),
    stdout: textSummary(data, { indent: "  ", enableColors: true }),
  };
}

function textSummary(data, opts) {
  // k6 will use the default text summary if this function is not available
  return "";
}
