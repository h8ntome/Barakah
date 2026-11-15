# Barakah backend

FastAPI + SQLAlchemy 2 + Alembic, Python **3.11–3.13**. PostgreSQL recommended; SQLite supported for development with exact decimal storage and serialized writes. No weights, banking, payment processor, live prices or certified religious authority bundled.

## Run locally

```sh
cd backend
python3.11 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log
```

The app **never calls create_all**. Apply migrations before serving. `GET /health` is liveness; `/api/v1/health` checks the database and migration table; Swagger at `/docs`, JSON schema `/openapi.json`. Full client contract: [`../docs/backend-api.md`](../docs/backend-api.md). All application routes `/api/v1`.

For PostgreSQL set `DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/barakah`. SQLite default is `sqlite:///./barakah.db`. Alembic reads the same settings as the API. Initial migration supports upgrade/downgrade; `alembic check` verifies model parity. **Downgrade destroys data**; back up before migration.

## Deployment

```sh
# Docker unavailable in the implementation environment; Dockerfile provided, not runtime-tested.
docker build -t barakah-api backend
# Supply DATABASE_URL and strong SECRET_KEY through environment/secrets, not build args.
docker run --rm -p 8000:8000 --env-file backend/.env barakah-api
```

Container runs non-root, port 8000, migration then uvicorn. For multiple replicas, run migrations once as a separate job and override command to `uvicorn app.main:app --host 0.0.0.0 --port 8000 --no-access-log`. The SQLite container file is ephemeral unless a correctly owned persistent volume is supplied; production should use PostgreSQL.

Required production configuration:

- `ENVIRONMENT=production`, `SECRET_KEY` at least 32 random characters (generate `python -c 'import secrets; print(secrets.token_urlsafe(48))'`). Default development secret rejected.
- `COOKIE_SECURE=true`, `ALLOWED_ORIGINS=https://your-app.example` (comma separated exact origins, never `*`). SameSite=Lax cookies require a **same-site** frontend/API deployment, ideally reverse proxy `/api` on the frontend origin. HTTPS termination must be trusted; never expose database credentials to browser configuration.
- `DATABASE_URL` private PostgreSQL with least-privilege role, encrypted transport as appropriate. Backups, rotation, monitoring, production edge rate limits, proxy body limits and request timeouts are deployment responsibilities.
- `AUTH_RATE_LIMIT=20` and `ADVISOR_RATE_LIMIT=30` per minute are bounded **per-process** defenses, not distributed/global limits. Ad events limited 120/minute per user. Do not trust client-supplied forwarding headers. Use a trusted reverse proxy for client IP enforcement. Disable access logs or redact reset-token query strings at **all** proxy/frontend layers.
- Server does not log credentials, financial records, prompts, tokens or raw SQL exceptions. API errors sanitized; no-store for private responses. Keep production debug off. SMTP failures log only a generic provider failure.

## Auth and reset delivery

Register/login return access token + public user and set refresh/CSRF cookies. Access token expires in 15 minutes, refresh in 30 days. Refresh rotates session and invalidates previous access token. Store bearer token only in memory. Browser fetch uses credentials; refresh/logout require trusted Origin + `X-CSRF-Token` copied from readable `csrf_token` cookie. Password change/reset/logout invalidate appropriate server sessions. Password hashes Argon2id; refresh/reset tokens only hashed in DB. Deleting user requires password and cascades owned database records, including chats and ad events.

Password reset does not expose whether email exists. With neither provider configured, `/auth/reset/request` returns explicit 503. Choose:

- Development only: `RESET_OUTBOX=./outbox`, private directory/files (0700/0600). Files contain email/token for local testing; **never serve, commit, back up publicly or retain these**. Account deletion erases owned DB rows, not already-delivered mail/outbox files. Delete development outbox manually after use.
- SMTP: `SMTP_HOST`, `SMTP_PORT=587`, optional `SMTP_USERNAME`/`SMTP_PASSWORD`, `SMTP_SENDER`, `RESET_URL=https://your-app.example/reset-password`. STARTTLS certificate verification mandatory. Link passes the token in a URL fragment, which is not sent to HTTP servers. Frontend consumes it once into memory and removes it from the URL; legacy query-token links are accepted and scrubbed too. Token one-use, 30-minute lifetime. Public response generic even if SMTP delivery fails (avoids enumeration); monitor generic provider-failure logs. Real mail delivery requires your provider credentials; transport tested with mocked SMTP, not a real external provider.

Provision existing registered user as admin using trusted server access only:

```sh
python -m app.admin admin@example.com
python -m app.admin admin@example.com --revoke
```

Clients cannot set admin status. Admin manually vets causes/ad destinations. Ad delivery filters approval, active flag, date range and explicit page context only; no financial/chat targeting. Event counts are not billing-grade analytics (client repeat events possible under throttle).

## Financial methodology

- Money: Decimal major units, two-decimal supported currency allowlist USD/EUR/GBP/PKR/SAR/AED, no FX. SQLite text representation avoids binary float loss, PostgreSQL NUMERIC(24,6). Accounts nonnegative; transaction edits/delete atomically reverse changes. Transfers same-currency and atomic; transfer entries cannot be independently modified. PostgreSQL row locks / SQLite BEGIN IMMEDIATE prevent concurrent overdraft. No automatic POST replay/idempotency keys; reconcile by reading state after uncertain response before retrying.
- Dashboard monthly income/expenses/savings, balances current. Assets = account balances + manually quoted holdings, liabilities from zakat profile. Other manually classified profile assets are deliberately excluded to avoid double counting. Missing quotes => incomplete/null valuation, never invented prices or silent FX. Separate currencies always retained.
- Zakat: manually classified cash/investments/gold/silver/business minus declared deductible debt, floor zero. Configurable rate (default 2.5%); positive manual nisab or dated user-entered per-gram gold/silver prices × configurable `gold_nisab_grams` / `silver_nisab_grams` (defaults 85/595g). Separate savings and other eligible assets are supported. Gates on nisab and user-attested haul, rounded once half-up. Snapshot history immutable; linked manual payments track paid/remaining. **Educational estimate**, asset/debt qualification and religious methodology need qualified guidance. No live metals, automatic haul monitoring or automated payment execution.
- Multiple named portfolios; weighted-average basis, buy fees capitalized/sell fees deducted, internal six-decimal basis rounding, no shorts/backdated trades ahead of latest recorded date, no cash-account coupling. Manual quotes retain source/date; no claims of live data. Dividends/splits/corporate actions unsupported.
- Screening: illustrative configurable debt/assets, interest income/revenue, interest-bearing assets/assets thresholds and prohibited-business input. Missing => uncertain, failed => non_compliant, complete passing => compliant_under_selected_methodology. Input/source/date/threshold/methodology version retained in immutable screening history. After `max_age_days` (default 90), current status becomes uncertain and `needs_reevaluation` is true; historical outcomes remain unchanged. **Not platform certification, a named scholarly standard or investment advice**.
- Giving/intents/goal contributions are manual records only. No real payment or charity receipt, account movement or verified campaign total implied.

## Advisor providers and privacy

`AI_MODE=mock` (default) is deterministic educational content. `AI_MODE=local` uses `AI_LOCAL_URL=http://127.0.0.1:8080/chat` (administrator configured loopback only). Protocol:

```http
POST /chat
Content-Type: application/json

{"text":"current user message only","system_prompt":"Barakah educational and safety instructions; optional authorized aggregate totals"}
```

Provider returns `{"text":"answer"}`; its `GET /health` returns 2xx when available. No OpenAI-specific protocol or bundled model/weights. An operator can implement a thin local service around their chosen model. Adapter ignores proxy environment, refuses redirects, has an overall configurable 10-second deadline (`AI_REQUEST_TIMEOUT_SECONDS`, connect 2s), caps response at 32 KiB/8,000 chars and sanitizes failures. `/api/v1/ai/health` reports mock/local health without exposing URL/secrets.

Explicit profile `ai_consent=true` required even in mock; revoking blocks future prompts. Current prompt and system instructions are sent to the local provider, **never individual account/portfolio records or previous chat history**. Per-message `include_financial_context=true` additionally permits only current-owner monthly currency/income/expense/savings totals; defaults off. Conversation length is bounded by `AI_MAX_CONVERSATION_MESSAGES` (default 100). Conversation/messages retained in owned DB until conversation/account deletion. Provider protocol and implementations are in `app/ai.py`; see `docs/AI_MODEL_INTEGRATION.md`. No streaming, retrieval citations or guarantee of model correctness; educational disclaimer appended. Review local-provider content safety separately before public exposure. Synchronous requests hold DB transaction while awaiting local provider; timeout bounded, but throughput needs load testing before scale.

## Validation

```sh
cd backend
.venv/bin/python -m pytest -q
# Optional PostgreSQL parity: creates random isolated schemas and removes them after each test.
TEST_DATABASE_URL='postgresql+psycopg://user:password@localhost:5432/test_database' .venv/bin/python -m pytest -q
.venv/bin/alembic check
```

Initial implementation: 54 tests passed on each database. Additional integration/review regressions were added afterward; authoritative final counts and commands are in `../docs/testing/test-results.md`. Tests migrate actual databases (no create_all), verify migration downgrade/upgrade parity, credentials/mass assignment/token expiry/refresh CSRF and rotation/concurrent refresh/revocation/reset/deletion; foreign ownership, exact decimal boundaries/concurrent overdraft/transfers/reversal; zakat gates/rounding/history/payments; multiple portfolios/cost basis/screening/quotes; consent/history/local HTTP adapter with an actual in-process HTTP server/provider failure rollback; approved campaign/admin behavior; SMTP TLS flow. PostgreSQL tests run against isolated schemas, not application tables. One upstream Starlette TestClient warning about a future httpx2 transition is currently emitted; production HTTP calls and tests still use the supported httpx compatibility path.

Production penetration/load testing, real SMTP delivery, Docker runtime and external AI/provider deployment are **not** claimed validated.
