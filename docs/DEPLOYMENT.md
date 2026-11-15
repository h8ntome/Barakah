# Development and deployment

## Tested local single-origin launch

After installing Python/Node dependencies, run `bash scripts/start-local.sh` from the repository root and open `http://127.0.0.1:8080`. See `audit/DEMO_GUIDE.md` for isolated databases and reset. `FRONTEND_DIST` enables FastAPI serving of the built frontend; the launcher sets the exact allowed loopback origins and applies migrations. Unknown `/api/...` requests return JSON404, not SPA HTML. Never use this loopback development recipe as a public production deployment.

## Local Docker Compose

Docker Engine/Desktop with Compose v2 is required. Copy `.env.example` to `.env` and replace both placeholder values with distinct random hex strings (`python3 -c 'import secrets; print(secrets.token_hex(32))'`). Never commit `.env`.

```sh
docker compose up --build
```

Visit `http://localhost:8080`. Nginx serves the React build and proxies `/api/` to FastAPI. Backend migrations run before Uvicorn. PostgreSQL has a named volume and is not published on the host. Backend port 8000 is loopback-only for OpenAPI/readiness diagnostics. Compose is a **local demo configuration**, not a production exposure recipe. AI is intentionally unavailable; insecure cookies are used only on local HTTP.

`docker compose down` preserves the data volume. `docker compose down -v` **deletes all local application data**; use only when intentionally resetting an isolated demo. No known-password public account is seeded.

## Production checklist

- Terminate HTTPS at a trusted ingress; set `ENVIRONMENT=production`, `COOKIE_SECURE=true`, a cryptographically random `SECRET_KEY`, and exact HTTPS `ALLOWED_ORIGINS`.
- Deploy frontend/API on the same site. Keep access tokens in memory and refresh tokens in HttpOnly cookies; do not put credentials in localStorage.
- Restrict direct API/database access. Do not blindly trust forwarded client-IP headers. Add edge rate limiting before scaling beyond one API process; in-process limits are not a distributed quota.
- Run `alembic upgrade head` as a single release job before starting replicas. Back up before migrations; test restore and rollback planning in staging.
- Supply a real reset-email provider before public account onboarding; development outbox behavior is not email delivery.
- Keep `AI_MODE=unavailable`. No inference integration is enabled; future integration requires a separate approval/security review.
- No real payment, bank-sync, brokerage execution or compliance certification is included. Vet advertisers/destinations separately.
- Static Vercel hosting alone cannot run this Python/PostgreSQL application. Existing `vercel.json` only builds the frontend; configure a trusted same-site API reverse proxy when using Vercel, or use the supplied Nginx deployment.

## Backups

For a configured local Compose instance:

```sh
docker compose exec -T db pg_dump -U barakah -d barakah -Fc > barakah-backup.dump
```

Treat dumps as sensitive financial data: encrypt at rest, restrict access, apply retention and never add them to Git. Restore into a **separate empty test database**, run `pg_restore --no-owner`, and verify row counts/authenticated reads before relying on the backup. Never test restores over a live database. Back up the application secret securely outside the repository; rotating it invalidates sessions.

## Verification limits

See `audit/TEST_RESULTS.md` for current commands actually executed; `docs/testing/` is historical. A committed Dockerfile/Compose file is not evidence that container startup was tested. Public hosting, real SMTP and live market providers require their own configured smoke checks. No AI provider is part of this release.
