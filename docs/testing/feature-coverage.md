# Feature coverage and limitations

Final verified state, 2026-11-15. API tests run on both SQLite and PostgreSQL; browser checks use the real PostgreSQL-backed API, not the legacy mock adapter.

| Feature | Implemented | Verification |
|---|---|---|
| Authentication | Registration/login/logout, owned preferences, UTC lifecycle timestamps, password change/reset, refresh rotation/revocation, account deletion | API/security tests; browser registration/reload/logout/login and four reset assertions |
| Accounts/transactions | Account CRUD, exact balances, income/expense CRUD, atomic same-currency transfers, category/date/search filters and sorting | API math/ownership/concurrency tests; browser account/income/expense and failed-network draft/retry |
| Dashboard/budgets | Per-currency balances/assets/liabilities/net worth, monthly income/expense/savings/rate/category totals, category/month budgets and overspending | API deterministic calculations; browser known totals and remaining budget |
| Zakat | Independent asset categories/debt, configurable gold/silver weights and manual thresholds/prices/rate, haul attestation, immutable estimate snapshots and linked partial payments | Formula/API/ownership tests; browser calculation/save/payment and remaining balance |
| Giving/goals | Sadaqah CRUD/filtering, current-month/year totals, donation count, recipient/cause distribution, goals CRUD/contributions, approved causes and manual donation intents | API tests including owner-only distributions; browser record/goal/contribution |
| Investments | Multiple portfolios, holdings, buy/sell ledger, fee-aware weighted basis, realized/unrealized gains, dated manual quotes, allocations and returns | API decimal boundary/oversell tests; browser portfolio/holding/trade/quote and net-worth update |
| Screening | Versioned configurable ratio/business checks, preserved history, evidence source/date/validity, stale re-evaluation, explicit uncertainty | API/history/migration tests; browser uncertain result and custom validity surviving reload |
| AI | Mock/local provider interface, explicit consent, optional owner-only monthly aggregates, bounded persistent conversations, timeout/failure rollback and health | API with real local HTTP fixture; browser mock label, verified totals, persisted history; **no final model tested** |
| Advertising | Admin-only campaigns/approval/windows, explicit contextual targeting, sponsored disclosure, impression/click counts and admin analytics | API/admin/visibility tests; real browser impression and click each confirmed in isolated DB |
| Resilience | Structured sanitized errors, request limits, transactional rollback, empty/loading/retry states | Failure/security tests; browser blocked request and draft-preserving retry |
| Deployment | Alembic migrations and version-aware readiness; SQLite/native PostgreSQL; Docker/Nginx/Compose scaffolding | Native migrations/schema check/build passed; **containers not run** |

## Deliberate boundaries / remaining work

- No real bank/payment/broker connection or automatic cash adjustment for trades/giving. Cash accounts must exclude separately tracked securities. Closing a holding means selling its full recorded quantity; immutable trade history remains.
- No external/live security or precious-metal feed, historical-price charts, dividends/splits/corporate actions or FX. Six two-decimal currencies only. Missing quotes remain unavailable, not guessed. Saved preferences do not implement full localization or per-user calendar boundaries; current-month/year aggregations use the server calendar.
- Religious qualification remains user-declared and educational. No named scholarly standard is certified; no automated haul monitoring or charitable receipt verification.
- Final fine-tuned LFM3 weights/runtime are not present. Local provider tests validate HTTP/error/privacy contracts, not model quality. No streaming/retrieval citations; opted-in context is limited to monthly totals, not raw records, full portfolios or previous messages.
- No write idempotency keys or automatic failed-write replay. After an ambiguous network response, inspect current records before resubmission; the UI preserves drafts but cannot prove a lost response meant a failed commit.
- Admin operations use the API/CLI, not a separate admin UI. Advertiser identity is stored, but formal vetting, advertising fraud defense and billing-grade analytics are operational work.
- Production HTTPS/ingress, distributed rate limits, backup restoration, real SMTP and sustained-load/penetration testing are still deployment gates. Browser evidence covers Chromium desktop and a 390px viewport, not every browser/device or assistive technology.
- Existing users upgraded from the first schema have unknown creation timestamps; new users receive UTC timestamps. Do not infer historical dates from migration time.

See [test results](test-results.md), [security checks](security-tests.md), and [integration evidence](integration-results.md). `benchmark/` and existing design/history were preserved.
