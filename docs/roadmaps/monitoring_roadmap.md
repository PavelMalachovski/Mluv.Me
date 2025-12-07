# Monitoring & Observability Roadmap

**Project:** Mluv.Me
**Last Updated:** December 7, 2025
**Status:** Ready for Implementation
**Expected Timeline:** 3-4 weeks
**Priority:** HIGH

---

## 📊 Executive Summary

Goal: Full visibility into reliability, performance, and cost. Implement APM, metrics, logs, and alerts with actionable dashboards. Cover app, OpenAI usage, database, and background tasks.

---

## 🎯 Objectives & KPIs
- Error detection coverage: 100% of unhandled exceptions reported
- p95 API latency < 300ms (voice flows excluded from strict SLA)
- MTTR < 30 minutes for P1 incidents
- Cost dashboards for OpenAI and infra

---

## 🚀 Phase 1: APM & Error Tracking (1 week)
- Integrate Sentry (FastAPI + SQLAlchemy integrations). Set sampling: traces 0.1 prod, 1.0 dev; profiles 0.1.
- Tag events with user_id (anonymized), endpoint, feature flag, subscription tier.
- Release tracking + environment tagging.

**Acceptance:** Errors visible in Sentry with breadcrumbs and user/tier context.

---

## 📈 Phase 2: Metrics (1 week)
- Prometheus client metrics:
  - HTTP: request_count, request_duration histogram (method, endpoint).
  - Business: DAU, messages_processed, conversion_free_to_paid, churn, stars_awarded.
  - OpenAI: requests_total, tokens_total by model/type, failures, rate-limit hits.
  - DB: query_duration, pool_in_use, slow_queries count.
  - Celery: task_runtime, task_failures, queue_length.
- Expose `/metrics`; protect with token/IP allowlist.

**Acceptance:** Dashboards show latency, errors, DAU, OpenAI spend proxy; alerts wired.

---

## 📜 Phase 3: Logging (0.5-1 week)
- Structlog with contextvars: bind user_id, request_id, session_id, tier.
- Redact PII/secrets in processors.
- Ship logs to central store (ELK/Datadog/Railway logs) with 7-30d retention.

**Acceptance:** Correlatable logs with trace/request IDs; no secrets present.

---

## ⏱️ Phase 4: Alerts & Runbooks (0.5 week)
- Prometheus/Sentry alerts:
  - High error rate, p95 latency, 5xx surge, DB pool exhaustion, Celery queue backlog, OpenAI failures.
  - Business: drop in DAU >20%, spike in token usage, conversion dip.
- On-call rotation and escalation matrix; Slack/Telegram notifications.
- Runbooks for common incidents (OpenAI outage, DB overload, Redis down, webhook failures).

**Acceptance:** Alerts actionable with clear owners; false-positive rate low.

---

## 🧪 Validation & SLOs
- SLOs: uptime 99.9%, p95 API latency < 300ms, lesson processing success > 99%.
- Quarterly chaos drills: kill Redis, slow DB, OpenAI 429 storm; verify alerting and recovery.

---

## 📚 References
- Sentry: https://docs.sentry.io/
- Prometheus client for Python: https://github.com/prometheus/client_python
- Structlog: https://www.structlog.org/en/stable/

---

**Next Steps:** Add Sentry/Prometheus middleware, create dashboards, set alerts, and schedule chaos drills.
