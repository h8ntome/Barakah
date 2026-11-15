# Barakah

An authenticated Islamic personal-finance tracker: transactions, budgets, savings goals, zakat records, sadaqah and manually valued investments. React/Vite + FastAPI/SQLAlchemy/Alembic; SQLite locally, PostgreSQL supported.

**Tracking, not money movement.** No bank sync, payment processing, brokerage execution, live prices or religious certification. **AI is intentionally unavailable**: no model, fake advice, inference API or API key is required. `benchmark/` and model-training work are unchanged.

## Start the complete app

Requires Python **3.11–3.13** and Node **20.19+**. First install dependencies:

```sh
python3.13 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
npm ci --prefix barakah-ui
```

If using `uv` (also clean-install tested): `uv venv --python 3.13 backend/.venv`, then `uv pip install --python backend/.venv/bin/python -r backend/requirements.txt`. Do not recreate an existing environment while its server is running.

From the repository root:

```sh
bash scripts/start-local.sh
# Open http://127.0.0.1:8080
```

This builds the frontend, applies additive migrations, and serves the real frontend and API together. The default database is `backend/barakah.db`; no external service is necessary. **Back up an existing database before upgrading.** See [migration/backup instructions](audit/DEMO_GUIDE.md).

Use `PORT=8081 bash scripts/start-local.sh` for another port. `DATABASE_URL` can select a dedicated SQLite file or PostgreSQL database. The launcher configures exact localhost origins for the selected port; it does not disable CSRF or authentication. It is bound to loopback and is **not** a public-production server recipe.

For frontend development, separately run `alembic upgrade head` and Uvicorn in `backend/`, then `npm run dev --prefix barakah-ui` on port 5173. Configure the actual frontend origin in backend `ALLOWED_ORIGINS`; opening an unconfigured port correctly returns 403. SQLite defaults are infrastructure-free. Do not change databases while a server is running.

## Try Demo

Choose **Try Demo** on the login screen. Each browser receives a unique, non-admin, editable workspace with fictional records:

- Monthly income **$4,500**, expenses **$2,850**; savings balance **$12,000**.
- Three fictional holdings valued manually at **$8,500**, not verified halal/live data.
- Eligible wealth **$15,000**, fictional nisab threshold and attested haul → **$375** zakat.
- Budgets, donations, transaction history and a **$5,000 Hajj goal with $1,250 contributed**.

Reset using **Home → Settings → Reset demo data**. Only that demo is replaced. Changes survive refresh; separate demo browsers never share data. Demos expire after 24 hours and expired owners are cleaned in bounded batches when another demo starts. Never enter real information in demo mode. [Full demo guide](audit/DEMO_GUIDE.md).

## Core workflows

- **Home:** stored totals, category charts, recent transactions, budget/goal/zakat summaries; Accounts, Transactions, Budgets, Savings goals and Settings.
- **Zakat:** manually classify eligible assets and deductible liabilities; document jewelry/investment assumptions, choose manual/gold/silver nisab, dated manual prices, rate and lunar-year attestation. Save immutable calculations; record/correct/remove payments made elsewhere.
- **Give:** record/edit/delete sadaqah and inspect monthly/annual totals. Goals track earmarked progress only, not extra assets or donations.
- **Invest:** portfolios, holding metadata, buys/sells, dated manual valuations including zero, configurable educational screening, allocation and gain/loss. Correct/remove the **latest post-migration trade** using exact snapshots; legacy trades cannot safely be individually reversed. Holding deletion explicitly removes its tracked history, not a real investment.
- **AI Chat:** suggestions, input and history UI work; Send explicitly reports the model is not connected. No new messages or fake responses are persisted.
- **Settings:** display name/preferences, logout/password change/deletion. Preferred currency never relabels or converts existing records.

Passwords use Argon2id. Access tokens stay in memory; rotating refresh tokens use HttpOnly cookies. All financial records are owner-checked server-side. Amounts use Decimal, not binary floating-point accounting.

For local password recovery, set `RESET_OUTBOX=/private/path` when launching; reset tokens are written to private files, **not emailed**. Production needs configured SMTP. Never expose or commit the outbox. [Backend guide](backend/README.md).

## Verify

```sh
(cd backend && .venv/bin/python -m pytest -q)
(cd backend && TEST_DATABASE_URL='postgresql+psycopg:///YOUR_TEST_DB' .venv/bin/python -m pytest -q)
npm test --prefix barakah-ui
npm run build --prefix barakah-ui
# With the single-origin app running against an isolated local database:
BARAKAH_UI_URL=http://127.0.0.1:8080 python3 tests/e2e/journey.py
```

Browser tests use installed `agent-browser`/Chromium and **actual backend/database requests**, not production mock APIs. [All commands and executed results](audit/TEST_RESULTS.md) · [feature matrix](audit/FEATURE_MATRIX.md) · [fixes](audit/FIXES.md) · [remaining issues](audit/REMAINING_ISSUES.md).

## Deployment boundary

The checked-in **Vercel configuration is frontend-only**. It does not provision Python, a database or an API proxy. The known public alias returned 404 during this audit; public deployment is not verified. Use the tested local launcher for a live laptop demonstration, or provision the backend/database and a same-origin HTTPS proxy before inviting remote users. Docker/Nginx deployment files are supplied but Docker runtime was not tested.

[Deployment/backups](docs/DEPLOYMENT.md) · [API contract](docs/backend-api.md) · [future LFM3-1.7B boundary](audit/AI_INTEGRATION.md). Older `docs/testing/` results are historical; `audit/TEST_RESULTS.md` is the current audit evidence.
