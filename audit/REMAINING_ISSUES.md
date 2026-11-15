# Remaining issues and limits

> Historical pre-opt-in snapshot. See [current release audit](../docs/RELEASE_AUDIT.md) and [local AI setup](../docs/local-ai.md). The public demo still has unavailable AI; local opt-in now has separate real inference evidence. Historical results below are preserved, not overwritten.

## Resolved — Public hosted demo verified

The former404/static-only blocker is resolved at **https://barakah-gamma.vercel.app**. The real frontend and Python API are deployed to Vercel, with a newly provisioned free Neon PostgreSQL database (initially empty, then migrated). Homepage and API readiness return200. **21 real-browser public checks passed**: editable demo, reload persistence, two-tester isolation, owner-only reset, HTTPS cookies, registration/login/logout and mobile layout. See `artifacts/logs/public-demo.txt`, screenshots in `artifacts/public/`, and `docs/VERCEL.md`.

**READY for remote fictional-data demonstration.** This does not certify production financial-service readiness. AI remains unavailable and email recovery requires SMTP.

Production was published explicitly with the CLI. Git branch tracking remains set to `main`; for future automatic production releases select `audit/full-application-fix` in Vercel's dashboard, or continue deliberate `vercel deploy --prod` releases. A Git push alone currently creates previews, not a new production release.

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
