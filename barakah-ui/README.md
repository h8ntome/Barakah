# Barakah frontend

React 18 / Vite interface for the Barakah backend. The original emerald editorial panel, phone layout, mobile safe areas and five-destination navigation are preserved. Financial records are server-backed; the browser does not calculate balances, zakat, cost basis, screening results or giving totals.

## Run

Node 20.19+ or 22.12+:

```sh
cd barakah-ui
npm ci
cp .env.example .env
npm run dev
```

Start the backend separately on `127.0.0.1:8000` using its README. Vite proxies `/api` to that address without rewriting the browser Origin. The backend must allow the frontend origin (normally `http://127.0.0.1:5173`). If another process uses that port, explicitly configure the actual frontend port in backend `ALLOWED_ORIGINS`.

`VITE_API_BASE_URL` defaults to `/api/v1`. This is public configuration; never add API keys, signing secrets or model credentials to Vite variables. Production requires an HTTPS same-site reverse proxy for `/api`, a correctly configured backend Origin allowlist and secure cookies. Static hosting alone does not provide the backend.

```sh
npm test
npm run build
npm run preview
```

## Connected workflows

- **Account access:** registration, login, cookie-backed session restoration, logout, password change, reset request/token confirmation (emailed URL tokens are captured once into memory and immediately removed from the address bar) and permanent account deletion. Settings include display name, country, IANA time zone, language/currency preference and explicit advisor consent. Preferences do not imply localization or currency conversion.
- **Home:** authoritative month-filtered totals separated by currency. Manage accounts, transactions and transfers; search descriptions and filter by account/category/date; create, edit and delete monthly budgets with server spending/utilization. Missing valuations remain visibly incomplete. Monthly savings rate and expense categories are displayed directly from the server; no-income savings rates are not shown as zero.
- **Zakat:** manually classify assets/debts with separate gold, silver, savings and other eligible values (avoid counting savings again in cash/bank), choose manual/gold/silver nisab, enter dated price/source, configurable metal nisab weights in grams, rate and haul attestation. Save server estimates to history and link manual payment records. Recorded paid/remaining figures come from the server. No payment processing or religious ruling is implied.
- **Invest:** create/rename/delete empty named portfolios, add holdings, record buys/sells and dated manual quotes. Configure evidence and ratio thresholds for server screening; missing evidence stays uncertain. Stale screenings show the server re-evaluation notice; paginated assessment history preserves dated evidence and methodology. Trades do not move account cash; quotes are not live; screening is educational rather than certification.
- **AI Chat:** consent-gated prompts, persistent conversation selection, new conversation and deletion, drafts per conversation, loading/failure recovery. Local demonstration replies are labeled from server metadata. Only the current question is sent to the configured model; stored history can be reviewed/deleted. No financial data is automatically sent.
- **Give:** approved cause search/category filters, giving intention records, sadaqah CRUD and category/date-filtered history/totals. Create/edit/delete charitable goals and record contributions with paginated history. These are manual records, never checkout or payment receipts.
- **Sponsored placements:** contextual approved API ads only, labeled sponsored/not endorsement, with HTTPS links and no financial/chat targeting by the frontend. Visible-only impressions and link clicks are reported to the event API; hidden mounted screens do not count impressions. No invented campaign data or fallback promotions.

## Security and state

`src/services/httpClient.js` keeps the access token only in its closure. Requests include cookies and bearer authentication. Refresh and logout send `X-CSRF-Token` from the readable `csrf_token` cookie; the refresh token is HttpOnly and never read by JavaScript. One shared refresh promise prevents rotation races within the app. Requests are bound to the session generation, so old responses and retries cannot cross logout/login account changes. A delayed 401 within the same session reuses an already rotated token; protected requests retry once only. Non-auth failures never automatically retry financial writes.

Money, quantities, rates and thresholds remain decimal strings throughout forms/transport. Formatting may convert for display; no browser financial arithmetic is authoritative. Missing values are not displayed as zero. Payment calculation choices are fetched separately across all pages; paginating calculation history cannot silently change a payment link. List histories paginate; account/portfolio choices and conversation messages fetch all server pages. There is no localStorage/sessionStorage of tokens, records or drafts. Drafts survive navigation and failed requests but not reload/logout. If a mutation loses its response, review history before retrying: the API does not provide mutation idempotency keys.

`useResource` suppresses stale responses after filters change or components unmount. Native controls have stable accessible labels; forms prevent duplicate submission while pending. No automatic payment or brokerage actions exist.

## Code and validation

- `src/services/index.js`: real route/payload boundary; no runtime mock selector.
- `src/services/httpClient.js`: transport/session/error boundary.
- `src/screens/`: connected workflows; `Management.jsx`, `PortfolioForms.jsx`, `Settings.jsx` provide focused sections.
- `src/components/forms.jsx`, `FinancialForms.jsx`: controlled inputs, pending/error/success states and paging.
- `src/types/api.d.ts`: connected API shape documentation; backend OpenAPI remains authoritative.
- `tests/httpClient.test.js`, `apiBoundary.test.js`: transport, refresh/CSRF/error, payload precision and route tests.
- `tests/legacyMockAdapter.test.js`: explicitly legacy mock-only fixture regressions. `finance.test.js` retains legacy calculation tests plus display checks. Neither establishes backend correctness. The old `mockAdapter`, `mocks/data.js` and provisional calculation utility are not imported by production screens.

See `API_CONTRACT.md` and `QA.md`. Root/backend documentation covers deployment, database, provider configuration and backend validation. No real banking, brokerage, payment rail, live-price service or certified scholarly screening is claimed.
