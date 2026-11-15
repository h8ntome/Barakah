# Public Vercel demo

**Live: https://barakah-gamma.vercel.app — select Try Demo.** Production deployment and21 real-browser public checks passed on2026-11-15. The database is Neon `barakah-demo`, free plan `free_v3`, region `iad1`; no paid plan was selected.

The repository now deploys **both** the Vite frontend and the existing FastAPI API on one Vercel domain. `api/index.py` exports the real application, `/api/*` routes to it before the SPA fallback, and Python3.13 installs the existing pinned backend dependencies. **A persistent hosted PostgreSQL database is still required.** There is no localStorage/mock-demo fallback and no shared demo password.

## One-time account setup

1. From the repository root, authenticate with `npx vercel login`, then `npx vercel link` and select the existing **barakah** project in the correct account/team. Do not paste tokens or database passwords into chat or commit them.
2. In Vercel Settings → Build and Deployment, use repository root `.` (not `barakah-ui`), Framework **Other**, and let checked-in `vercel.json` supply the install/build/output settings. Enable the Python runtime selected by `.python-version` (3.13). Use a supported Node LTS (22 or24).
3. Connect hosted PostgreSQL through Vercel Marketplace/Storage (for example Neon). Select a free plan if appropriate and confirm provider limits/billing yourself. Use its **pooled, TLS-enabled** connection string as `DATABASE_URL`. Standard `postgres://` and `postgresql://` URLs are normalized to the installed psycopg3 driver. Never use SQLite or `/tmp` as public persistence.
4. Configure these **server-side** environment variables for Production. Do not prefix any secret with `VITE_`:

| Variable | Value |
|---|---|
| `DATABASE_URL` | Hosted PostgreSQL pooled URL including `sslmode=require` |
| `SECRET_KEY` | Generate privately: `python3 -c 'import secrets; print(secrets.token_hex(32))'` |
| `ALLOWED_ORIGINS` | Exact public HTTPS origin, e.g. `https://barakah-gamma.vercel.app`; comma-separate only other domains you own and need |
| `ENVIRONMENT` | `production` |
| `COOKIE_SECURE` | `true` |
| `AI_MODE` | `unavailable` |
| `RESET_URL` | Actual HTTPS origin followed by `/reset-password` |

The entrypoint enforces production mode, secure cookies and unavailable AI even if configured incorrectly. A missing database/secret/origin **fails closed**, not into an insecure ephemeral demo. Leave `FRONTEND_DIST` and `RESET_OUTBOX` unset. The frontend build forces the same-origin `/api/v1` URL; no API URL secret belongs in the client.

Preview deployments require their own scoped configuration and preferably a separate database. Add only the exact trusted preview origin if testing there. Do not expose production secrets to untrusted pull requests or allow `*.vercel.app` origins.

## Migrate, deploy, then verify

Back up any existing database using the provider's snapshot/export facility first. For a brand-new empty demo database there is no existing user data to migrate. Never run migrations per request/cold start or in concurrent preview builds.

With local Python dependencies installed, pull the chosen environment and apply the existing migrations **once** before publishing:

```sh
npx vercel env pull .env.vercel.local --environment=production
# This generated private file is ignored by Git and Vercel uploads.
# Vercel Secret values pull as [SENSITIVE]; do not source those placeholders.
# Read only the direct DB URL. Test mode applies only to this migration process,
# not the deployed API, which always enforces production security.
backend/.venv/bin/python - <<'PY'
import os, sys
from pathlib import Path
from dotenv import dotenv_values
values = dotenv_values('.env.vercel.local')
os.environ.update(DATABASE_URL=values['DATABASE_URL_UNPOOLED'],
                  ENVIRONMENT='test', AI_MODE='unavailable')
sys.path.insert(0, str(Path('backend').resolve()))
from alembic import command
from alembic.config import Config
config = Config(str(Path('backend/alembic.ini').resolve()))
command.upgrade(config, 'head')
command.check(config)
PY
npx vercel deploy --prod
```

Publish the commit containing the Vercel entrypoint (on `audit/full-application-fix`). For automatic Git deployments, choose that branch as Production Branch or merge it normally into the project's production branch; do not force-push. Confirm the intended public alias points to this deployment. A successful Git push or static build alone is **not** a successful demo deployment.

Ensure the **production** URL is publicly accessible without a Vercel login, according to the project's deployment-protection settings; do not disable authentication inside Barakah. Inspect function logs if API health fails, without sharing credentials. Before sending the link to testers:

1. `GET https://YOUR-DOMAIN/api/v1/health` must return200 JSON with `status: ready` and `database: available` (not HTML).
2. Open the public URL in a fresh browser. Click **Try Demo** and confirm the fictional-data banner and seeded totals.
3. Create/edit a financial record, reload and confirm persistence. After an idle interval verify session refresh still works.
4. Open a second private browser; its demo must not contain the first browser's edits.
5. In Home → Settings, reset the first demo and verify the second demo remains unchanged.
6. Verify logout, registration/login and AI's explicit unavailable response. Test recovery only after configuring real SMTP; no provider is required for Try Demo.

Each demo is a unique non-admin owner with a24-hour expiry. Reset recreates only that demo; there are no shared credentials. No actual money moves.

## Operational limits

Use Vercel's edge/firewall rate limiting for the public auth/demo endpoints as available on your plan. Existing in-process throttling is retained but is not a global quota across serverless instances. Python uses the hosted connection pooler instead of holding a pool per function instance. Database/compute quotas and cold starts depend on the chosen plans. Do not advertise production financial-service readiness based on this demo deployment.

`demo-video/`, benchmark/model files, local environments, databases, dumps and audit screenshots are excluded from uploads. None of those files are deleted locally.

## Verification status for this change

Local full suite: **121 SQLite tests passed** plus one PostgreSQL-only test skipped; **122 PostgreSQL tests passed**, including the actual Vercel ASGI entrypoint with production HTTPS-cookie settings, two isolated demos, persisted edits, refresh and reset. **64 frontend tests and the production build passed.** Test execution caught and fixed an import-path issue in Alembic revisions before commit.

Follow-up: Vercel login and project linking succeeded. Node was changed to24.x, and production secret/origin/cookie/AI/reset configuration was added. The first cloud build exposed Vercel's inability to resolve the nested `-r backend/requirements.txt` include; root requirements now contain the same pinned packages, with a parity regression test. The subsequent **real Vercel cloud build passed**, producing both frontend assets and the Python3.13 function (`dpl_BzFo4rNjcFGZfUGD1LfnJhqR9Lpf`).

The owner subsequently accepted Neon terms. `barakah-demo` was created on `free_v3` in `iad1`, connected only to Production, verified empty and migrated. Production deployment `dpl_GNC9Z3btAS9FBxAYsMSai1JyLVqZ` was explicitly published and aliased to **https://barakah-gamma.vercel.app**. Homepage/API readiness return200. The real public browser smoke passed21 checks, including persistent edits, two-tester isolation, reset, secure cookies and registration/login. Evidence is in `audit/artifacts/logs/public-demo.txt`, `vercel-production-build.txt` and `audit/artifacts/public/`.

Production Git branch tracking remains `main`; the documented project-update API does not expose that field. For future releases use `npx vercel deploy --prod` explicitly, or set the desired Production Branch in the Vercel dashboard. Do not assume a preview deployment or Git push has updated the public alias. External SMTP and broad production-capacity testing remain unconfigured/unverified; neither is required to use Try Demo.
