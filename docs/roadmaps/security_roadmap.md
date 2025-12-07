# Security Roadmap

**Project:** Mluv.Me
**Last Updated:** December 7, 2025
**Status:** Ready for Implementation
**Expected Timeline:** 6-8 weeks
**Priority:** HIGH

---

## 📊 Executive Summary

Goal: Harden Mluv.Me across authentication, data protection, API security, and infrastructure. Emphasis on Telegram + Web auth, secrets management, rate limiting, input validation, encryption at rest/in transit, and compliance readiness.

**Expected Outcomes:**
- Reduced account takeover risk
- Safer storage of audio/content data
- Lower API abuse via per-user rate limits
- Clear observability of security events

---

## 🎯 Objectives & KPIs
- 0 critical/high findings in security review
- 100% endpoints behind auth and rate limits
- 100% secrets managed outside codebase
- <0.5% 4xx/5xx due to auth errors after rollout

---

## 🚀 Phase 1: Authentication & Sessions (2 weeks)

### 1.1 Session Management
- Implement `UserSession` model: device_type, device_info, last_activity, expires_at, is_active.
- Add revoke-all and per-device revocation endpoints.
- Sliding expiration (30d) with inactivity timeout; refresh on activity.

### 1.2 Telegram & Web Auth
- Telegram Login Widget verification (HMAC check) server-side.
- Issue httpOnly, secure, samesite=strict cookies for web.
- Add session introspection endpoint for frontend.

### 1.3 2FA (Web, premium/enterprise)
- TOTP secrets per user; backup codes encrypted.
- Require 2FA for payment methods and enterprise admins.

**Acceptance Criteria:**
- Sessions stored and revocable; device list visible to user.
- 2FA flow passes UI/UX tests; recovery codes downloadable once.

---

## 🔒 Phase 2: Data Protection (2 weeks)

### 2.1 Audio & Content Encryption
- Use Fernet/AES-GCM for transient audio storage (`EncryptionService`).
- Encrypt at write; decrypt only for processing; auto-clean temp files.
- Ensure keys rotated via KMS/secrets manager.

### 2.2 Secrets Management
- Move secrets from `.env` to platform secrets (Railway/Cloud KMS).
- No secrets in git; enforce via pre-commit detect-private-key.

### 2.3 PII Minimization & Retention
- Add `deleted_at` soft deletes for major tables.
- Data retention policy: archive or purge per GDPR.

**Acceptance Criteria:**
- No unencrypted audio on disk; temp files removed.
- Secrets retrievable only from manager; no plaintext in logs.

---

## 🛡️ Phase 3: API Security & Rate Limiting (1.5 weeks)

### 3.1 Per-User Rate Limits
- Use SlowAPI/Redis: global + per-endpoint limits (e.g., 30/hr for lessons for free users).
- Tier-aware limits aligned with monetization.

### 3.2 Input Validation & Sanitization
- Pydantic validators for audio MIME/size (<=10MB), text length (<=5000 chars).
- Reject unexpected fields; use JSON schemas for JSONB columns with CHECK constraints.

### 3.3 CORS & Headers
- Prod origins only (`app.mluv.me`, `mluv.me`); allow_credentials true.
- Security headers middleware: HSTS, X-Content-Type-Options, X-Frame-Options, CSP (report-only initially).

**Acceptance Criteria:**
- 100% endpoints protected by rate limits.
- Validation errors return structured 400 with codes.

---

## 🧱 Phase 4: Infrastructure & Dependency Security (1 week)

### 4.1 Dependency Hygiene
- Enable Dependabot/Snyk; weekly updates.
- Pin versions; run `pip-audit` in CI.

### 4.2 Images & Supply Chain
- Use minimal base images; run as non-root; set `readOnlyRootFilesystem` if possible.
- SBOM generation (syft) and image scanning in CI.

### 4.3 Logging & Secrets Redaction
- Structlog processors to redact tokens, API keys, PII fields.
- Prevent request/response bodies with secrets from being logged.

---

## 👁️ Phase 5: Monitoring & Incident Response (1 week)

### 5.1 Security Logging
- Centralize auth events (login, logout, 2FA, session revoke, password/secret updates).
- Alert on anomalies: repeated failures, new device/location, rate-limit bursts.

### 5.2 Playbooks
- Incident runbooks: credential leak, key rotation, data request/deletion, DDoS/API abuse.
- RTO/RPO targets defined; paging via on-call channel.

---

## ✅ Testing & Validation
- Unit tests for auth flows, session expiry, 2FA, rate limits (mock Redis).
- Integration tests: CORS, headers, webhook auth, encryption round-trip.
- Security scans: bandit, pip-audit, container scan; OWASP ZAP baseline against staging.

---

## 🗺️ Rollout Plan
- Week 1: Sessions + rate limits (shadow mode). Monitor 429s.
- Week 2: Encryption + secrets manager cutover. Dry-run key rotation.
- Week 3: 2FA beta for staff/power users. Enable headers/CSP report-only.
- Week 4: Turn on CSP enforce; finalize playbooks; run ZAP and fix findings.

---

## 📈 KPIs to Track
- 401/403 rate (should drop/stabilize)
- 429 rate per tier (no false positives for paid users)
- Time-to-revoke session (<1 min)
- Secrets in repo: 0
- Vulnerability SLA: critical <24h, high <72h

---

## 📚 References
- FastAPI Security: /fastapi/fastapi
- Redis Rate Limiting: /long2ice/fastapi-cache (for cache); slowapi docs
- OWASP ASVS & Top 10
- Stripe Webhook Security

---

**Next Steps:** Approve scope, create tickets per phase, start Phase 1.
