# Barakah integration test plan

## Baseline inspection

Starting branch: `feat/barakah-frontend`, commit `e957342`; clean working tree. Remote fetched: only the existing frontend branch exists. Preserve its history and `benchmark/` unchanged.

Existing stack: React 18.3, JavaScript, Vite 7, lucide-react, plain CSS. Routing is React state across Home, Invest, Zakat, AI Chat, Give, not URL routing. `App.jsx` owns tab and asset state; chat remains mounted. `useResource` supplies asynchronous reads and retry. Services select a local mock adapter; no server or auth/database/environment API setup existed. Existing tests: Node test runner, 16 finance/mock service checks. No browser automation suite existed. Existing frontend visual direction remains authoritative.

## Feature integration inventory

| Existing surface / interaction | Required authoritative capability |
|---|---|
| Desktop and mobile navigation, Home quick actions | Preserve navigation; protect authenticated workspace |
| Home greeting, financial overview, asset action, priority rows | Current user, actual account balances/transactions, latest saved Zakat; refresh on mutation |
| Zakat edit asset modal, preview, save | Server Decimal calculation; manual dated metal prices, Nisab choice, haul flag, stored breakdown |
| Zakat history/payment tracking (new) | Saved calculations and partial payments, ownership |
| Invest portfolio/explore segmented control, allocation, holdings | Portfolios, buy/sell ledger, manual quotes with provenance, gains; preserve educational criteria |
| Give search/category filters, cause selection, gift amount presets/custom amount/confirmation | Real donation records/history and summaries; explicitly no payment processing |
| Chat starter questions, composer, retry/edit, tab-retained history | Authenticated persistent conversation CRUD, provider abstraction, timeout/error handling, explicit mock label |
| Authentication/settings (new) | Registration/login, memory access token, secure refresh cookie, reset/change password, preferences, deletion |
| Finance manager (new) | Accounts, income/expense/transfer CRUD, filtering, budgets, authoritative dashboard |
| Sponsored placement (new) | Approved active contextual campaigns; impression/click events; no chat targeting |

## Gates

1. Backend unit/API/security tests: Decimal math, ownership, malformed/negative/nonfinite values, transfer exclusion, currency isolation, auth expiry/revocation/reset/rate limit, admin denial.
2. Migrate an empty SQLite database and a dedicated local PostgreSQL database; verify readiness and schema version. Never use another project's database.
3. Frontend unit tests and production build.
4. Browser against real backend: register → account → income/expense → dashboard → budget → Zakat save/payment → donation → portfolio/trade/screen → AI reply/history → reload → logout/protected → login/persistence.
5. Failure paths: missing providers, unreachable model, bad input, unavailable database, failed browser API request and retry, empty records.
6. Screenshots and narrow/mobile layout inspection. Record only fictional test data, never credentials/tokens.
7. Small bounded load probe with actual environment/results, not a capacity claim.
8. Confirm no benchmark changes; commit and push without force.

## Evidence policy

Execution is complete for the native/local gates; results and explicit external/deployment exceptions are recorded in `test-results.md`. Mock provider checks establish adapter behavior, not model quality. Missing live market/model services must return unavailable/uncertain, not invented data. Docker execution can only be claimed if Docker is present. See `test-results.md` for final counts and exceptions.
