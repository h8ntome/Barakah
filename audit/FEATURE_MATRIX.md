# Final feature matrix

> Historical pre-opt-in snapshot. See [current release audit](../docs/RELEASE_AUDIT.md) and [local AI setup](../docs/local-ai.md). The public demo still has unavailable AI; local opt-in now has separate real inference evidence. Historical results below are preserved, not overwritten.

**Scope:** verified local application using the real FastAPI backend, migrated SQLite and PostgreSQL integration tests. The public Vercel deployment remains blocked/unverified; do not read these rows as hosted-site approval. Test counts/commands are in `TEST_RESULTS.md`.

| Feature | Frontend | Backend | Database | Integration | Executed tests/evidence |
|---|---|---|---|---|---|
| Registration | Form + validation + duplicate feedback | Argon2id, normalized email,409 duplicate, throttle | Unique owner, hashed password | Browser201 → dashboard | auth/demo browser; direct SQL hash/user check; auth tests |
| Login/session/logout | Login, protected workspace, refresh, sign out |15-minute access, rotating30-day refresh, CSRF/revocation | Hashed refresh/session ownership | Real browser logout/login/refresh; process restart | auth tests, browser auth/demo + restart |
| Password recovery/change | Request/token/new-password and change-password forms | One-use reset, expiry, revoke sessions, delivery unavailable error | Hashed reset tokens | Browser reset through private test outbox | reset browser4; backend auth/mail tests. Real SMTP untested |
| Demo | Visible Try Demo; label; Settings reset | Unique non-admin seed,24h expiry, bounded cleanup | All normal owner-scoped records; atomic seed/reset | Two browsers isolated; writes persist; reset replaces only own demo | auth/demo20; seed rollback/expiry/isolation tests |
| Dashboard | Stored totals, category bars, recent history, budgets/goals/zakat, portfolio value | Exact per-currency summaries; no FX or fabricated valuations | Aggregates owned records | Mutations recalculate; refresh/restart retains values | finance corrections23; main journey31; dashboard tests |
| Transactions | Add/edit/delete/filter income/expenses | Positive-amount model, atomic balance reversal, no overdraft, account ownership | Exact Decimal balances, FK/constraints | $500−$120=$380; edits/deletes/filter/reload | finance tests + corrections browser |
| Budgets | Add/edit/delete, spent/remaining/progress/overspend | Category/currency/month uniqueness; actual ledger spending | Owned monthly budgets | $400−$275=$125; $450 exceeds by$50 | backend + corrections browser |
| Zakat | Manual/gold/silver methods, manual prices/date, rate, haul, asset-treatment notes | Decimal eligibility calculation; user-resolved asset/debt classification | Immutable profile snapshots; mutable owned payment records | $15,000×2.5%=$375; payment correction/deletion updates outstanding | zakat/audit finance tests + browser |
| Sadaqah | Add/edit/delete/date/recipient/notes, history/totals | Separate voluntary-giving kind; no payment execution | Owned giving rows | Totals/reload checked; never becomes zakat automatically | backend + main/corrections browser |
| Investments | Holdings/trades/metadata/remove, manual zero valuation, allocation bars, screening | Exact weighted-average costs; safe latest-trade snapshots; date/evidence checks | Owned portfolios, trades, immutable screening history |10×$50=$500→12×$50=$600; oversell rollback; confirmed deletion | portfolio repair browser + backend parity tests |
| Savings goals | Home/Give access, target/date, edits/deletes, contribution correction/removal, progress | Atomic owned contributions and Decimal progress | Goal/contribution FK cascade | Hajj $5,000/$1,250=25%, remaining$3,750 | backend + corrections browser |
| Settings/profile | Name/country/timezone/language/currency; logout/password controls | Validated profile, no admin mass assignment | Owner preferences persisted | Name/currency survive reload/login; USD records not relabeled | backend auth + main browser |
| AI chat | Header/history/input/send/questions/loading/error/empty states | **Intentionally unavailable**,503; no inference/network/fake response | No new chat writes; legacy owned history retained | Send keeps draft, no phantom messages; navigation stable | unavailable/no-network tests, Chat SSR, browser journey |
| Security/isolation | In-memory token, safe React rendering, useful errors | Owner checks, parameterized ORM, bounded body/auth limits, CSRF/origins | Per-owner FKs, rollback, hash-only credentials | Two-account browser probes deny mutations/read leakage/admin escalation |21 browser ownership checks; both DB suites |
| Responsive/accessibility basics | Existing visual identity;320/390/768/1280px, keyboard tabs, labels, native disclosures | N/A | N/A | All five destinations navigable without document overflow |22 viewport/keyboard checks; screenshots visually inspected |
| Public deployment | Static Vercel configuration only | **Not provisioned/verified there** | **Not provisioned/verified there** | **Blocked**; known alias404 | Live HTTP check, initial reproduction notes |

## Deliberate boundaries

- No real bank connection, donations, brokerage execution, live prices, FX or verified religious certification.
- Monetary accounting is server-side Decimal. JavaScript Number is used only to format values and position progress bars.
- Contribution amounts are earmarked progress, not additional wealth or donation receipts.
- Existing pre-audit trades lack reversal snapshots; individual corrections are unavailable. New trades can be corrected/removed newest-first; deleting a whole tracked holding explicitly removes its history. No migration invents old trade order.
- The current frontend still uses native disclosure panels; some panels close after a successful reload of their parent list. This does not lose persisted records.
- Actual mobile hardware, Safari/Firefox, full screen-reader testing and public production infrastructure were not verified.
