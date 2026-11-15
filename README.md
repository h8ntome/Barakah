# Barakah

An authenticated Islamic personal-finance tracker: transactions, budgets, savings goals, zakat records, sadaqah and manually valued investments. React/Vite + FastAPI/SQLAlchemy/Alembic; SQLite locally, PostgreSQL supported.

**Tracking, not money movement.** No bank sync, payment processing, brokerage execution, live prices or religious certification. **AI is unavailable by default and on the public demo.** An explicit [private local AI setup](docs/local-ai.md) connects the pinned Barakah checkpoint after saved consent. Real browser → backend → model → browser inference and follow-ups were observed; advice quality failed important checks. No fake answers or automatic financial-record sharing. Offline model evaluation is separate; no weights were changed during this release.

**Current release:** [audit, evidence and limitations](docs/RELEASE_AUDIT.md) · [credits](docs/CREDITS.md). This is not a production financial adviser or a claim of hackathon eligibility.

**Evaluation and submission:** [Fine-Tuning Evaluation and Personal Finance Domain Adaptation](benchmark/rescue/REPORT.md) · [submission checklist](benchmark/rescue/SUBMISSION_CHECKLIST.md). The original numerical comparison is **36/40 LFM3 vs 32/40 Barakah**, with conceptual answers unreviewed. The separate exploratory personal-finance benchmark completed 50 questions/model: **5/23 LFM3 vs 9/23 Barakah** on strict numeric fields, with substantial formatting failures and no reviewed advice-quality scores. It does not replace the original benchmark. **This project is a prototype and is not financial advice.**

## Start the complete app

The locked release setup uses Python **3.13** and Node **20.19+ / 22.13+ / 24+**. First install dependencies:

```sh
python3.13 -m venv backend/.venv
backend/.venv/bin/python -m pip install --require-hashes -r backend/requirements.lock
npm ci --prefix barakah-ui
```

If using `uv`: `uv venv --python 3.13 backend/.venv`, then `uv pip install --python backend/.venv/bin/python --require-hashes -r backend/requirements.lock`. `requirements.txt` remains the pinned direct-dependency input for cloud deployment; `requirements.lock` includes transitive versions and hashes for the release setup. Do not recreate an existing environment while its server is running.

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
- **AI Chat:** default/public mode truthfully reports unavailable and saves no failed sends. Opt-in local mode sends your question and bounded owned conversation history to the exact pinned checkpoint after consent; successful pairs persist atomically. Model text is not Sharia-screened and can give wrong or contradictory advice. Verify calculations independently; it never changes your financial records.
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

Browser tests use installed `agent-browser`/Chromium and **actual backend/database requests**, not production mock APIs. [Current commands, executed evidence and unresolved failures](docs/RELEASE_AUDIT.md) · [feature matrix](audit/FEATURE_MATRIX.md) · [fixes](audit/FIXES.md) · [remaining issues](audit/REMAINING_ISSUES.md).

## Deployment boundary

The checked-in **Vercel configuration now includes the Python API** alongside the frontend. Connect persistent hosted PostgreSQL, configure server-side secrets/origins, apply migrations, then deploy and verify the public demo. Follow [the Vercel setup guide](docs/VERCEL.md). **Public demo: https://barakah-gamma.vercel.app — choose Try Demo.** The production frontend/API and free Neon PostgreSQL database are deployed; 21 real-browser public checks passed, including persistence, isolation, reset and registration/login. No Vercel account is needed to test it. Docker/Nginx deployment files are also supplied but Docker runtime was not tested.

[Deployment/backups](docs/DEPLOYMENT.md) · [API contract](docs/backend-api.md) · [opt-in pinned model boundary](docs/local-ai.md). Older `docs/testing/` and `audit/` reports are historical snapshots; [the release audit](docs/RELEASE_AUDIT.md) distinguishes local AI tests, public deployed behavior and offline benchmarks.
