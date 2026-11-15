# Demonstration guide

## Public demo — ready for remote testers

Open **https://barakah-gamma.vercel.app** and choose **Try Demo**. No Vercel account or shared password is required. Each tester gets a private editable fictional workspace, persisted in hosted PostgreSQL. Reset through **Home → Settings → Reset demo data**; demos expire after24 hours. Public browser verification passed21 checks. AI is intentionally unavailable; no actual money moves.

## Start locally

Requirements: Python 3.11–3.13, Node 20.19+, dependencies installed. No API key/model is required.

```sh
python3.13 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
npm ci --prefix barakah-ui
bash scripts/start-local.sh
```

If using `uv` (also clean-install tested): `uv venv --python 3.13 backend/.venv`, then `uv pip install --python backend/.venv/bin/python -r backend/requirements.txt`. Do not recreate an existing environment while its server is running.

Open **http://127.0.0.1:8080**. The launcher builds the frontend, migrates the selected database and serves UI/API on one origin. Stop with Ctrl+C. To use another port: `PORT=8081 bash scripts/start-local.sh`. If supplying `ALLOWED_ORIGINS`, include the exact origin/port; never use a wildcard or disable checks.

Default database: `backend/barakah.db`. For a separate demo database:

```sh
DATABASE_URL=sqlite:////absolute/private/path/demo.db PORT=8081 bash scripts/start-local.sh
```

Use a writable private directory. Do not place databases/outboxes inside the frontend assets directory. This loopback HTTP configuration is for a laptop demonstration; public deployment requires HTTPS, secure cookies, a strong secret, persistent backend/database and same-origin proxy. Static Vercel hosting alone is not enough. The API deployment entrypoint is now included; follow `docs/VERCEL.md` for the public hosted demo setup.

## Judge experience

1. Click **Try Demo** on the login screen. No email/password is needed.
2. Home shows fictional income $4,500, expense $2,850, surplus $1,650, account balances $15,000 (checking $3,000 + savings $12,000), and manually valued portfolio $8,500. Tracked assets total $23,500; zakat classification is independent and not added twice.
3. Home → Transactions: select Demo checking, add income/expense, edit/delete from history. Filter by description/category/date. Home and budgets recalculate from stored records.
4. Home → Budgets: create a monthly category limit; edit/delete it. Category names are user-defined labels and must match transaction categories.
5. Home → Savings goals → Savings & giving goals: Hajj target $5,000, contributions $1,250, progress25%, remaining $3,750. Add/correct/delete contributions or edit/delete a goal. Progress does not create additional assets or move cash.
6. Zakat: inspect the $375 estimate. The example explicitly assumes $15,000 eligible cash/savings, a fictional $5,000 threshold and satisfied lunar-year haul. Edit only eligible assets, rate, manual/gold/silver method and dated source; record jewelry/investment/debt assumptions. Save a snapshot, then record/edit/delete payments made elsewhere. No real payment is sent.
7. Give: record/edit/delete sadaqah and see monthly/yearly totals. Voluntary sadaqah is never automatically counted as zakat. The approved-cause directory may be empty; recording a recipient manually works independently.
8. Invest: three fictional examples have dated manual valuations and unverified screening. Add a holding, then record a buy (10×$50=$500); correct the latest trade to12 shares ($600). Add manual quotes/screening evidence, inspect allocation, or confirm deletion of a tracked holding/history. Nothing trades on a brokerage or moves account cash.
9. Settings: change display name/preferences. Currency preference does not convert/relabel records. Demo password/account-deletion controls are hidden because there is no judge password.
10. AI Chat: type or choose an example question and Send. The service honestly reports unavailable, retains the draft and produces no advice or saved message.
11. Refresh: financial records remain. Sign out: protected pages become inaccessible.

## Isolation, expiry and reset

Every Try Demo creates a unique ordinary, non-admin user with a random unexposed password and its own records. No shared public credentials exist. Two unrelated browser sessions cannot see or mutate each other's records; the usual backend ownership checks apply.

**Home → Settings → Reset demo data** atomically deletes only that authenticated demo owner and creates a fresh seeded owner/session. Old tokens become invalid. Regular accounts cannot call this reset. Reset also works after access-token expiry via normal refresh/retry. If the seed fails, the entire transaction rolls back.

A demo expires after24 hours; expired users cannot use existing access/refresh sessions. New demo starts delete up to100 expired demo owners per request. Physical deletion is opportunistic, not a timer: without new starts, expired records remain inaccessible until cleanup. Start a new demo after expiry. Never enter real financial data in demo mode.

Multiple tabs in one browser share authentication cookies, as with normal accounts. Use separate browser profiles/incognito contexts to demonstrate independent judges; ordinary separate demo accounts never share records.

## Migration and backup

Added migrations:
- `b17d8e0a1f42`: demo flag/expiry, default regular-user status for existing users.
- `c28e9f1b2a53`: nullable trade sequence and exact pre-trade snapshots. Legacy trades/balances remain unchanged and are explicitly non-correctable individually.

No existing application database was destructively migrated during this audit. Testing used `/tmp/barakah-audit/app.db`, disposable SQLite databases and random schemas in dedicated local PostgreSQL databases. Read-only inspection of the pre-existing integration database verified the initial synthetic registration only.

Before upgrading any existing database, stop writers and create a private backup outside Git. SQLite example:

```sh
backend/.venv/bin/python - <<'PY'
import sqlite3
with sqlite3.connect('backend/barakah.db') as source, sqlite3.connect('/private/backup/barakah-before-audit.db') as backup:
    source.backup(backup)
PY
```

Create that backup directory first and restrict permissions. PostgreSQL: `pg_dump -Fc DATABASE > /private/backup/barakah.dump`; restore-test into a **different empty database**, never over live data. Then run `cd backend && .venv/bin/alembic upgrade head`. Do not downgrade/drop a database to reset a judge demo.

## Password recovery

For local reset tests, launch with `RESET_OUTBOX=/absolute/private/outbox`. Files are private notifications, **not email delivery**. Use the token through the reset UI/link and delete the private test notification afterward. Public onboarding requires an SMTP provider; none was provisioned or externally tested here.
