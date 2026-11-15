# Feature coverage ledger

This is the integration acceptance checklist, not a declaration of completion. Starting state: frontend-only mock prototype, no backend. Final evidence will be entered after execution.

| Feature | API/database requirement | Browser acceptance |
|---|---|---|
| Authentication | Register/login/logout, rotation/revocation, profile/preferences, password/reset/delete | Create user; restore after reload; logout blocks workspace; login restores records |
| Accounts | Owned CRUD; currency; opening/current balances | Add and manage account |
| Transactions | Owned CRUD; positive Decimal values; transfers; idempotency; filters | Add income/expense; edit/delete; dashboard changes |
| Dashboard | Stored amounts, per-currency summary, no fake trend/FX | Verify known income/expense/net worth |
| Budgets | Monthly category budget vs actual, remaining/utilization | Add budget and verify progress |
| Zakat | Gold/silver Nisab, dated manual prices, haul, liabilities, rounding, stored history/payments | Calculate/save/pay partially and verify remaining |
| Sadaqah | Donation record CRUD/date/category/recipient; summaries/goals | Record contribution; filter history; no money-transfer claim |
| Investments | Multiple portfolios, trade ledger, average cost/fees/gains, manual valuation provenance | Create portfolio, buy/sell, inspect holdings/history |
| Screening | Versioned configurable criteria, dated source, missing-data uncertainty | Show uncertain result without invented fundamentals |
| AI | Provider abstraction, bounded chat, owner-only history, mock label, consent | Send; receive; reload history; new/delete conversation; retry errors |
| Advertising | Admin approval, campaign windows, context-only serving/events/analytics | Only eligible sponsored placement rendered |
| Error handling | Structured validation/auth/dependency errors, rollback | Empty states; unavailable service and retry without data loss |
| Deployment | Alembic SQLite/PostgreSQL; process vs dependency health | Serve frontend/backend together |

Deferred external integrations must be listed in the final report: payments are tracking-only; no live quote or metal provider is assumed; no final model weights are available. Any further incomplete item must be named explicitly, rather than described as complete by association with a passing build.
