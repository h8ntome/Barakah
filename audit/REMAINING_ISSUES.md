# Remaining issues and limits

## P0 — Public hosted application is not verified/ready

**Reproduce:** request `https://barakah-gamma.vercel.app/` or `/api/v1/health`; the known alias returned Vercel404 during this audit. The original configuration was static-only. A subsequent hosting change adds the Python API entrypoint and ordered API/SPA routing; see `docs/VERCEL.md`. This does not provision the hosted database or authenticate the deployment account.

**Needed:** Neon terms acceptance and persistent hosted PostgreSQL, one migration release, and production alias verification. Vercel login, production secret/origin configuration and a real cloud build have now succeeded. Run demo isolation/persistence and the mandatory browser registration flow against that exact deployment after provisioning. Only Barakah's project settings were updated (Node24 and server-side configuration); the operator must personally accept Neon terms. No database or paid plan has been created, and no production alias has been changed. A Git push alone does not fix infrastructure or prove deployment success.

The user's exact failing registration URL/request remains unknown; the configured local baseline worked, and the separate unsupported-origin403 was reproduced. Do not claim the particular reported public failure is conclusively diagnosed or fixed.

**Verified fallback:** `bash scripts/start-local.sh` provides a working laptop demo. The final overall hosted-release verdict remains **NOT READY**, despite passing local core workflows.

## P2 — Legacy and non-latest trade correction is deliberately bounded

**Reproduce:** migrate a database containing older trades without sequence/reversal snapshots, then open Trade history. Those rows show legacy correction unavailable. A non-latest new trade also cannot be corrected before removing newer trades.

Old same-day ordering/balances are not invented by migration. New latest trades are fully correctable/removable. The owner may explicitly remove an entire tracked holding/history and re-enter it; that is destructive and never automatic. Supporting arbitrary historical edits requires a separate audited ledger-replay design.

## P2 — Public email recovery requires a provider

**Reproduce:** run without `RESET_OUTBOX` or SMTP, then request a password reset. It reports delivery not configured. Local private-outbox recovery passed; external SMTP delivery was not provisioned or tested. Configure verified STARTTLS SMTP before remote public onboarding.

## P3 — Disclosure panels may close after successful writes

**Reproduce:** record/correct a goal contribution. The parent list reloads and its native disclosure closes; reopen Contributions to continue. Persisted amounts/progress remain correct. Broad state-management rewrites were avoided.

## Operational limits, not hidden implementations

- Tested load is a small single-process demonstration. In-process throttles are not distributed limits; production needs trusted edge limiting, HTTPS, backups, monitoring and capacity testing.
- No mutation idempotency keys. If a network failure leaves completion uncertain, inspect history before manually resending. Financial POSTs are not automatically retried except after an authenticated401 rejection.
- Demo expiry is enforced at24 hours; physical cleanup occurs in batches on later demo starts, not a scheduled timer. Separate browsers are isolated; tabs in the same profile share normal auth cookies.
- Real-bank sync, payments, brokerage execution, live prices, FX, scholarly certification, automatic corporate actions and AI inference are not implemented or falsely simulated. Only AI is intentionally unavailable among the requested core tracking workflows.
- UI language preference is saved but the interface remains English. Record dates are stored as entered; preferred timezone does not rewrite past dates.
- Chromium viewport emulation and basic keyboard checks passed; physical iOS/Android, Safari/Firefox, assistive-technology certification and exhaustive security/load testing were not performed.
- Docker configuration is supplied, but Docker runtime was not executed. PostgreSQL integration and SQLite process-restart persistence were executed.
- Upstream Starlette TestClient emits one httpx/httpx2 deprecation warning; no tests fail from it.

## Worktree incident

The harness-created worktrees under `Documents/worktrees/` became inaccessible with OS `Resource deadlock avoided`. Attempts to move them also failed. Partial AI edits were left untouched there; portfolio had no successful edits in that location. Fresh isolated worktrees under `~/.cache/barakah-worktrees/` completed normally, and their tested commits were integrated. No unrelated worktrees or teammate changes were deleted. Those inaccessible scratch worktrees remain outside the application branch; filesystem cleanup is not claimed completed.
