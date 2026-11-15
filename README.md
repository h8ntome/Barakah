# Barakah

A connected personal-finance workspace for budgeting, Zakat, giving, manually tracked investments, and Islamic-finance education. The original React/Vite emerald-and-mint interface is preserved; data now lives in an authenticated FastAPI backend.

**Tracking, not money movement.** No bank sync, payment processing, brokerage execution, live market feed or religious certification is included. AI defaults to an explicitly labelled deterministic mock; the fine-tuned model and `benchmark/` remain separate and unchanged.

## Start locally

Python 3.11–3.13 and Node 20.19+ are required. Two terminals:

```sh
# Terminal 1, repository root
cd backend
python3.11 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log
```

```sh
# Terminal 2, repository root
cd barakah-ui
npm ci
npm run dev -- --port 5173
```

Open **http://127.0.0.1:5173** and create an account (password: 12–128 characters). SQLite is the no-infrastructure local default. For PostgreSQL set `DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/barakah` in `backend/.env`, create that database, then run the same migrations. Never mix databases by changing configuration while the API is running.

Optional Docker Compose: copy root `.env.example` to `.env`, replace both placeholders with distinct random hex values, then `docker compose up --build`; visit **http://localhost:8080**. This configuration is supplied but **Docker execution was not tested here** because Docker is unavailable. Native PostgreSQL startup/migrations and the full browser flow were tested.

## Try the product

1. Home → Accounts: add a cash/bank account; Transactions: enter income and expenses; Budgets: set a monthly category limit.
2. Zakat: enter eligible assets and deductible debt, choose manual/gold/silver Nisab, supply dated manual prices and attest to haul if applicable. Save a dated snapshot, then record payments against it.
3. Give: record Sadaqah given elsewhere; view/filter history; create a giving goal and record contributions. These actions never transfer money.
4. Invest: create portfolios/holdings, record buys/sells and optional dated manual quotes. Evaluate configurable educational screening checks; absent evidence stays uncertain, stale results need re-evaluation.
5. Home → Settings: explicitly enable advisor consent. AI Chat stores conversations; optionally include only your current-month income/expense aggregates. Mock replies are labelled; no paid/external service is required.
6. Reload, sign out, sign back in: records persist. Settings includes profile preferences, password change, and account deletion. For local password resets, uncomment `RESET_OUTBOX=./outbox` in `backend/.env` and restart the API. This private notification directory is not real email delivery; without an outbox or SMTP configuration, reset requests explicitly report unavailable.

**Accounting boundary:** account balances must represent cash/uninvested balances, excluding securities separately entered as portfolio holdings. Portfolio trades do not automatically move cash; keep your manually tracked balances reconciled. Zakat assets are independently classified and are not added again to dashboard assets. No FX conversion is performed. Six two-decimal currencies are supported: USD/EUR/GBP/PKR/SAR/AED.

## Optional fictional demo

Against your local API:

```sh
python3 scripts/demo.py --email judge@example.com
# Prompts for your own private password; never creates a public known-password account.
# Delete that isolated account and all its owned records when done:
python3 scripts/demo.py --email judge@example.com --delete-test-account
```

The script labels its stock/metal values as fictional, creates one user only, refuses non-loopback URLs and refuses to overwrite an existing account. Reset by deleting and re-seeding that test account, not by dropping other users' data.

## Tests

```sh
cd backend
.venv/bin/python -m pytest -q
# Optional PostgreSQL parity, in a dedicated database with schema-creation permission:
TEST_DATABASE_URL='postgresql+psycopg:///barakah_test' .venv/bin/python -m pytest -q
cd ../barakah-ui
npm test
npm run build
cd ..
# With frontend/API running; requires agent-browser CLI and Chromium:
python3 tests/e2e/journey.py
# Optional reset browser flow; point to the private outbox configured on the API:
BARAKAH_RESET_OUTBOX=backend/outbox python3 tests/e2e/reset_flow.py
python3 tests/load_smoke.py
```

See [actual test results](docs/testing/test-results.md), [coverage and limitations](docs/testing/feature-coverage.md), [security checks](docs/testing/security-tests.md), and [integration evidence/screenshots](docs/testing/integration-results.md). Browser tests create unique fictional users in the configured **local** API; use an isolated development database.

## Architecture and API

- React 18/Vite/plain CSS; same five destinations, service boundary and in-memory access tokens.
- FastAPI `/api/v1`, Pydantic validation, SQLAlchemy 2, Alembic migrations, exact Decimal arithmetic. PostgreSQL preferred; SQLite exact-text numeric storage for local parity.
- Argon2id passwords, hashed rotating refresh sessions, HttpOnly cookies, CSRF/Origin checks, per-resource ownership, admin-only campaign APIs.
- Modular finance, giving/Zakat, portfolio/screening, AI providers, advertising, mail and security modules. No microservices required.
- OpenAPI: **http://127.0.0.1:8000/docs**. [API contract](docs/backend-api.md).
- `/health`: process liveness. `/api/v1/health`: database/schema readiness. Authenticated `/api/v1/ai/health`: mock/local provider availability, not a claim of model quality.

[Backend guide](backend/README.md) · [Frontend guide](barakah-ui/README.md) · [AI model integration](docs/AI_MODEL_INTEGRATION.md) · [Deployment/backups](docs/DEPLOYMENT.md)

The existing Vercel configuration builds only static frontend assets. It needs a configured same-site API proxy to run this integrated application; it does not deploy Python/PostgreSQL automatically.
