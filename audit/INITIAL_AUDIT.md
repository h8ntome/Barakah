# Initial audit — 2026-11-15

Baseline: `6dca92f`, clean `feat/barakah-frontend`; work branch `audit/full-application-fix`. Existing React/Vite frontend, FastAPI/SQLAlchemy backend, Alembic migrations, SQLite/PostgreSQL, and unit/integration/browser suites. `benchmark/` is out of scope.

## Confirmed findings

- **P0 deployment:** `vercel.json` builds static assets and rewrites every path to HTML; it does not deploy or proxy the Python API. Known public alias returned HTTP 404. The user's exact failing URL was not supplied; do not equate this evidence with a proven diagnosis of their particular attempt.
- **P0 configuration reproduction:** real Chromium registration via preview port 5182 returned 403 `origin_forbidden` / `Untrusted request origin`. That origin is absent from backend allowlist. Do not disable Origin/CSRF checks; launch with an explicitly configured matching origin.
- **Authentication baseline:** Chromium at configured origin 127.0.0.1:5173 registered a synthetic account (201), logged out/in and refreshed successfully. Read-only SQL in existing local integration DB confirmed one user and an Argon2id hash. Existing service log contained startup/shutdown messages, no registration exception. Existing user data was not altered. The single synthetic account created for this baseline reproduction was later deleted through the normal authenticated account-deletion endpoint (204); unrelated records were untouched.
- **P1 demo:** only a CLI seed script exists; no Try Demo button, automatic expiry, or browser reset. Script also requests a fabricated AI response.
- **P1 investments:** holdings have create/trade/quote/screening endpoints but no holding edit/remove endpoints or UI.
- **P1 AI requirement mismatch:** default provider generates deterministic financial advice and optional local inference exists. Current request requires an unavailable placeholder only; no inference should be invoked.
- **P2 error handling:** non-JSON successful API responses become null and authentication dereferences null; validation errors say only 'consult API schema'; duplicate email message does not clearly identify duplicate registration.
- **P2 goals:** existing goals are presented as charitable giving only, not general savings/Hajj goals.

Further finance/security findings and execution results will be recorded as verified, not inferred from component existence. Existing architecture and visual identity are retained. Expected load: single-process hackathon demonstration, not large-scale multi-worker production.
