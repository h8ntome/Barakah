# Public Vercel demo

**Public demo: https://barakah-gamma.vercel.app — select Try Demo.** Production personal-account OpenAI settings and encrypted storage were verified on **15 November 2026 (UTC)**. Demo accounts cannot save keys; AI stays off until a personal user saves a connection and consent. No custom destination is currently approved. **Successful external inference remains unverified.** The database uses Neon's free plan; confirm current provider limits.

## Current verification

Functional release [`e74b4ab`](https://github.com/h8ntome/Barakah/commit/e74b4ab15450cfac2632315e010ffc3a848e4f55) passed [fresh Linux CI](https://github.com/h8ntome/Barakah/actions/runs/43757595736). Independent current tests: SQLite264 +1 PostgreSQL-only skip; PostgreSQL265; frontend75; benchmark86. The frontend has no lint/type script; Vite build passed. Media TypeScript/ESLint/source checks are separate.

Production was built with `--prod --skip-domain` before migrating from `c28e9f1b2a53` to `d39f0a2c3b64`. A private PostgreSQL18.7 custom backup and full archive decode passed; no global database client upgrade or service restart occurred. Promotion was confirmed8.182s after migration completion; canonical health returned200 ready/database available and schema-drift check passed. Existing data was preserved.

Canonical production-command bundle: `index-BnW_DoQQ.js`, SHA256 `e57dff714ff06d6195ea59a59b0db3c8bc581259f0ea85462ea0444371e44381`. Production checks verified owner-bound AES-GCM storage, CSRF, demo refusal, actual invalid-key rejection, saved failure/consent across refresh, removal/no fallback and auth. Independent browser checks also verified signup, key clearing, failure/reload, removal/signout, retained demo data and immediate Zakat-to-Home updates. No successful external inference, quality improvement or financial-service certification is claimed. Historical checks below remain historical, not extra current-run passes.

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
| `AI_MODE` | `unavailable` (private pinned runtime stays off) |
| `USER_AI_ENABLED` | `false` unless deliberately enabling personal-account BYOK after secure setup below |
| `RESET_URL` | Actual HTTPS origin followed by `/reset-password` |

The entrypoint enforces production mode, secure cookies and `AI_MODE=unavailable` (no private pinned runtime). It does **not** override `USER_AI_ENABLED`; leave that false to keep external-provider AI unavailable too. A missing database/secret/origin **fails closed**, not into an insecure ephemeral demo. Leave `FRONTEND_DIST` and `RESET_OUTBOX` unset. The frontend build forces the same-origin `/api/v1` URL; no API URL secret belongs in the client.

Preview deployments require their own scoped configuration and preferably a separate database. Add only the exact trusted preview origin if testing there. Do not expose production secrets to untrusted pull requests or allow `*.vercel.app` origins.

## Personal-account AI setup

Follow [the user-provider guide](user-ai.md) before enabling this feature. Public demo accounts can never save provider keys. Personal accounts can use OpenAI or an exact operator-approved HTTPS OpenAI-compatible destination, not native Anthropic/Gemini APIs.

After backing up and applying the integrated migrations, supply `USER_AI_ENABLED=true` and a **dedicated base64-encoded 32-byte random `AI_CREDENTIAL_KEY`** privately through server-side secret management. It must not be `SECRET_KEY` or a browser-exposed `VITE_` variable. No actual secret is included in this guide. Optional `AI_ALLOWED_BASE_URLS` is a comma-separated exact HTTPS allowlist; keep empty if custom providers are unnecessary. Encryption-key rotation requires a planned migration or users replacing keys; removing a live key does not erase backups or provider data.

Defaults: 6 attempts/minute and 30/day per account, one in-flight request/account and 8 globally through database-backed admission. Tests and failed provider attempts count. Users must save their connection and then consent; testing makes a real potentially billable request. No automatic financial-record sharing, financial writes, silent fallback or provider-key fallback. A provider's reported model identity is not independently proved.

Verify migrations, setup gating, demo refusal, personal-account ownership, encryption, consent resets, removal, quotas and provider failures before announcing availability. Production verification used a deliberately invalid synthetic key and **verified no successful external inference**. A genuine-key test requires separate authorization/budget. On another installation, keep the feature disabled until its release verification is complete.

## Build, back up, migrate, promote, then verify

Back up any existing database using the provider's snapshot/export facility first. For a brand-new empty demo database there is no existing user data to migrate. Never run migrations per request/cold start or in concurrent preview builds.

With local Python dependencies installed, stage a production-context build without moving the alias. Verify that build and a backup made with a compatible PostgreSQL client before applying migrations **once**. The old release checks an exact schema head; minimize the gap between migration and new-deployment health/promotion:

```sh
npx vercel deploy --prod --skip-domain --yes
# Record the immutable staged URL; verify build and private DB backup first.
umask 077
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
PY
# Check /api/v1/health on the staged deployment, then promote immediately.
npx vercel promote https://YOUR-STAGED-DEPLOYMENT.vercel.app --yes
```

After promotion, run Alembic's schema-drift check against the same database and verify the canonical alias. Retain the previous deployment receipt and database archive privately. After a schema upgrade, do not blindly roll back to code expecting the old head: prefer new-schema-compatible code with `USER_AI_ENABLED=false`. Never downgrade or restore a snapshot over newer writes without a write freeze and reconciliation.

Publish the commit containing the Vercel entrypoint (on `audit/full-application-fix`). For automatic Git deployments, choose that branch as Production Branch or merge it normally into the project's production branch; do not force-push. Confirm the intended public alias points to this deployment. A successful Git push or static build alone is **not** a successful demo deployment.

Ensure the **production** URL is publicly accessible without a Vercel login, according to the project's deployment-protection settings; do not disable authentication inside Barakah. Inspect function logs if API health fails, without sharing credentials. Before sending the link to testers:

1. `GET https://YOUR-DOMAIN/api/v1/health` must return200 JSON with `status: ready` and `database: available` (not HTML).
2. Open the public URL in a fresh browser. Click **Try Demo** and confirm the fictional-data banner and seeded totals.
3. Create/edit a financial record, reload and confirm persistence. After an idle interval verify session refresh still works.
4. Open a second private browser; its demo must not contain the first browser's edits.
5. In Home → Settings, reset the first demo and verify the second demo remains unchanged.
6. Verify logout and registration/login. With both AI modes disabled, verify AI's explicit unavailable response. If deliberately enabling personal-account BYOK, verify the optional rollout boundary above and demo refusal separately. Test recovery only after configuring real SMTP; no provider is required for Try Demo.

Each demo is a unique non-admin owner with a24-hour expiry. Reset recreates only that demo; there are no shared credentials. No actual money moves.

## Operational limits

Use Vercel's edge/firewall rate limiting for the public auth/demo endpoints as available on your plan. Existing in-process throttling is retained but is not a global quota across serverless instances. Python uses the hosted connection pooler instead of holding a pool per function instance. Database/compute quotas and cold starts depend on the chosen plans. Do not advertise production financial-service readiness based on this demo deployment.

`demo-video/`, benchmark/model files, local environments, databases, dumps and audit screenshots are excluded from uploads. None of those files are deleted locally.

## Historical verification (older deployment, not new AI rollout)

Local full suite: **121 SQLite tests passed** plus one PostgreSQL-only test skipped; **122 PostgreSQL tests passed**, including the actual Vercel ASGI entrypoint with production HTTPS-cookie settings, two isolated demos, persisted edits, refresh and reset. **64 frontend tests and the production build passed.** Test execution caught and fixed an import-path issue in Alembic revisions before commit.

Follow-up: Vercel login and project linking succeeded. Node was changed to24.x, and production secret/origin/cookie/AI/reset configuration was added. The first cloud build exposed Vercel's inability to resolve the nested `-r backend/requirements.txt` include; root requirements now contain the same pinned packages, with a parity regression test. The subsequent **real Vercel cloud build passed**, producing both frontend assets and the Python3.13 function (`dpl_BzFo4rNjcFGZfUGD1LfnJhqR9Lpf`).

The owner subsequently accepted Neon terms. `barakah-demo` was created on `free_v3` in `iad1`, connected only to Production, verified empty and migrated. Production deployment `dpl_GNC9Z3btAS9FBxAYsMSai1JyLVqZ` was explicitly published and aliased to **https://barakah-gamma.vercel.app**. Homepage/API readiness return200. The real public browser smoke passed21 checks, including persistent edits, two-tester isolation, reset, secure cookies and registration/login. Evidence is in `audit/artifacts/logs/public-demo.txt`, `vercel-production-build.txt` and `audit/artifacts/public/`.

Production Git branch tracking remains `main`; the documented project-update API does not expose that field. For future releases use `npx vercel deploy --prod` explicitly, or set the desired Production Branch in the Vercel dashboard. Do not assume a preview deployment or Git push has updated the public alias. External SMTP and broad production-capacity testing remain unconfigured/unverified; neither is required to use Try Demo.
