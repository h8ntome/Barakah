# Connected frontend API boundary

The frontend now uses the implemented backend, not the former mock proposal. Authoritative route schemas are backend OpenAPI (`/docs`) and `docs/backend-api.md`; frontend wire types are documented in `src/types/api.d.ts`. The service boundary in `src/services/index.js` isolates every route.

## Transport

- Base: `VITE_API_BASE_URL`, default `/api/v1`; snake_case JSON; UUID/string IDs.
- Decimal strings for every monetary amount, quantity, fraction and threshold. Never sum financial values in the UI. USD/EUR/GBP/PKR/SAR/AED are separate currencies; no FX.
- Dates: `YYYY-MM-DD`; month: `YYYY-MM`; server timestamps UTC ISO. Forms submit dates without timezone conversion.
- Arrays are plain arrays, with `limit`/`offset` where supported. Aggregate dashboard/portfolio/summary endpoints are not paginated.
- Errors: `{error:{code,message}}`; 5xx and network errors get safe recovery copy. Drafts are retained on failure. Missing resources such as an unsaved zakat profile are explicit empty states, not fabricated records.
- `credentials: include`; access bearer token in memory only. Register/login/refresh return `{access_token,token_type,user}`. Refresh is shared across concurrent requests. Refresh/logout require trusted Origin and `X-CSRF-Token` read from `csrf_token`; refresh_token remains HttpOnly.

## Routes used

| Area | Routes and UI behavior |
| --- | --- |
| Auth | POST `/auth/register`, `/auth/login`, `/auth/refresh`, `/auth/logout`; PATCH `/auth/profile`; POST `/auth/password`, `/auth/reset/request`, `/auth/reset/confirm`; DELETE `/auth/me`. Profile fields: display_name, ai_consent, country, timezone, language, currency. |
| Accounts | GET/POST `/accounts`, PATCH/DELETE `/accounts/{id}`. Create includes name, account_type, currency, opening_balance. Update changes name only; delete rejects accounts with ledger entries. |
| Transactions | GET/POST `/transactions`, PATCH/DELETE `/transactions/{id}`. Full create/update payload: account_id, kind (income/expense), amount, category, description, occurred_on. GET filters account_id/category/query/start_date/end_date. Transfer ledger rows cannot be edited/deleted separately. |
| Transfers | POST `/transfers`: from_account_id, to_account_id, amount, occurred_on; same-currency manual ledger transfer. |
| Budgets | GET/POST `/budgets`, PATCH/DELETE `/budgets/{id}`. Full create/update payload category/currency/amount/month. Spent, remaining, utilization_percent are server-calculated. |
| Dashboard | GET `/dashboard?month=YYYY-MM`; per-currency balance, income, expenses, savings, total_assets, liabilities, net_worth and valuation_complete; savings_rate_percent is null with no income, expense_categories maps categories to decimal totals; asset_basis disclosure. Null valuations stay incomplete. |
| Zakat | GET/PUT `/zakat/profile`, GET `/zakat/estimate`, GET/POST `/zakat/history`, GET/POST `/zakat/payments`. Saved profile includes distinct cash/savings/other/investments/gold/silver/business/liabilities assets, nisab_method, manual_nisab or metal price, price_source, valuation_date, haul_start/complete and fractional rate. Configurable gold_nisab_grams/silver_nisab_grams default to "85"/"595" and accept positive six-decimal strings. Linked payments use history_id. Snapshots expose paid_amount/remaining_amount. |
| Giving | GET `/causes?query=&category=`; GET/POST `/donation-intents`; GET/POST `/sadaqah`, PATCH/DELETE `/sadaqah/{id}`, GET `/sadaqah/summary`. Sadaqah filters category/start_date/end_date; input amount/currency/paid_on/category/recipient/note. No payment processing. |
| Goals | GET/POST `/goals`, PATCH/DELETE `/goals/{id}`; full create/update payload name/currency/target_amount/target_date. GET/POST `/goals/{id}/contributions`, contribution input `{amount}`. Manual progress only; currency cannot change after contributions. |
| Portfolios | GET/POST `/portfolios`, PATCH/DELETE `/portfolios/{id}` (name; delete empty only). GET `/portfolio?portfolio_id=` for holdings and aggregates. POST `/portfolio/holdings` includes portfolio_id/symbol/name/currency. GET/POST `/portfolio/trades`; input holding_id/side/quantity/price/fees/traded_on. PUT `/portfolio/holdings/{id}/quote` with price/as_of/source. |
| Screening | PUT `/portfolio/holdings/{id}/screening`: prohibited_business nullable bool; nullable fractional debt_to_assets, interest_income_to_revenue, interest_assets_to_assets; configurable debt_threshold/income_threshold/interest_assets_threshold; source/methodology_source/assessed_on/notes. Server returns assessment with status, missing_inputs, failed_checks, methodology_version and disclaimer. No user-selectable compliant result. Holding needs_reevaluation flags stale screening; GET `/portfolio/holdings/{id}/screenings?limit=&offset=` returns dated assessment history. |
| Education | GET `/education/investing`; static server education cards. |
| Advisor | GET `/advisor/context`, `/advisor/conversations`, `/advisor/conversations/{id}/messages`; POST `/advisor/messages` with text, optional conversation_id and include_financial_context (default false); DELETE `/advisor/conversations/{id}`. Consent required. is_demo controls disclosure. |
| Ads | GET `/ads?context=dashboard|giving|education`; render only sponsored HTTPS placements returned by approval-filtered API. POST `/ads/{id}/events` with `{kind:"impression"|"click"}`; impressions are observed only when the placement is visible, once per mounted placement. No fabricated ad fallback or profile targeting. |

## Known boundaries

Reset delivery is a backend configuration concern; development outbox is not email delivery. Language/currency preferences do not localize the current English UI or convert records. A request interrupted after server commit may need history inspection before retrying. Browser refresh serialization is in-tab; the UI does not coordinate independent browser tabs. Chat history is persisted on the server. The provider receives `{text,system_prompt}`: current question, safety instructions, and only when explicitly requested the owner's current-month currency/income/expenses/savings aggregates. Prior messages and individual records are not sent; appended verified aggregates persist with the reply. Screening and zakat require user-supplied metadata and qualified review.

Legacy mock fixture tests are not an API contract and not evidence of backend or model correctness.
