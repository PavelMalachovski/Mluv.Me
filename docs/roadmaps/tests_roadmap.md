# Testing Roadmap

**Project:** Mluv.Me
**Last Updated:** December 7, 2025
**Status:** Ready for Implementation
**Expected Timeline:** 5-6 weeks
**Priority:** HIGH

---

## 📊 Executive Summary

Goal: Raise confidence and speed via systematic testing. Target 80%+ coverage, reliable integration/E2E coverage of core flows (voice lessons, stats, payments), and load testing for scale.

---

## 🎯 Objectives & Metrics
- Unit test coverage ≥ 80%
- Integration/E2E coverage for all critical paths
- p95 test runtime < 6 min in CI
- Flaky test rate < 1%

---

## 🚀 Phase 1: Foundations (1 week)
- Standardize pytest config, markers (`unit`, `integration`, `load`, `e2e`).
- Add factory/fixtures for users, sessions, audio samples, OpenAI mocks.
- Introduce `pytest-rerunfailures` for flaky isolation in CI.

**Acceptance:** Base fixtures available; tests runnable locally with `make test`.

---

## 🧪 Phase 2: Unit Tests (2 weeks)

### Priority Areas
- `honzik_personality.py`: prompt building, history formatting, model selection.
- `gamification.py`: streak logic, stars calculation, achievements.
- `correction_engine.py`: parsing GPT responses, scoring, error paths.
- `srs_service.py`: SM-2 scheduling edge cases.
- `openai_client.py`: retry/backoff, model routing.

**Acceptance:** 80%+ unit coverage in services; mocks for external APIs.

---

## 🔗 Phase 3: Integration Tests (1-1.5 weeks)

### Flows
- Voice/text lesson processing `/api/v1/lessons/process`: upload audio, get response, stars, DB writes.
- Stats retrieval `/api/v1/stats/{user}`: cache hits/misses.
- Subscription checks (once payments live): access control by tier.
- Telegram handlers: voice handler end-to-end with mocked Bot API.

**Tooling:** httpx.AsyncClient with test app; test DB; fakeredis for cache; mock OpenAI/Stripe.

**Acceptance:** Green integration suite; covers happy path + common errors (429, validation).

---

## 📈 Phase 4: Load & Performance (0.5-1 week)
- Locust scenarios: 500-1000 concurrent users; main flows (process lesson, stats, vocabulary).
- Track p95, error rate, DB pool usage, Redis hit rate.
- Gate for releases: p95 < 3s, errors <1% under target load.

---

## 🎭 Phase 5: End-to-End & Regression (0.5-1 week)
- Light E2E smoke (post-deploy) hitting health, lesson flow, stats, subscription status.
- Contract tests for APIs (OpenAPI examples as checks).
- Visual regression not needed now (no web UI yet), add when Next.js live.

---

## 🛠️ Tooling & CI
- pytest, pytest-asyncio, httpx, fakeredis, freezegun.
- Coverage with `coverage.py`; fail CI if < threshold.
- Split jobs: unit (fast) vs integration (slower); nightly load test optional.
- Pre-commit hooks: mypy, bandit, black, isort, flake8 run before tests in CI.

---

## ✅ Acceptance Criteria & DoD
- Coverage ≥ 80% overall; critical modules ≥ 90%.
- No skipped tests in critical paths.
- CI time < 10 min for full suite.
- Docs: HOWTO for running tests locally; make targets (`test`, `test-unit`, `test-int`).

---

## 📚 References
- Pytest: /pytest-dev/pytest
- Async testing: /fastapi/fastapi
- Load testing: https://locust.io/

---

**Next Steps:** Add fixtures/mocks, prioritize unit targets, wire CI thresholds, schedule load test baseline.
