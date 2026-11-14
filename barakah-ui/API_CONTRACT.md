# Barakah frontend integration contract — DRAFT FOR TEAM REVIEW

**Proposal, not an established backend API.** No server, endpoints, authentication, payment processing or AI integration is implemented. The current application uses only local asynchronous mocks. The backend teammate must approve transport, schemas, religious methodology, authorization, privacy and error semantics before integration.

## Boundary and conventions

UI → `src/services/index.js` → local `mockAdapter` → `src/mocks/data.js`. Pages never fetch. `src/types/api.d.ts` documents the complete adapter interface. `src/services/useResource.js` handles reads, stale-request suppression, loading and retry. Mutation forms preserve drafts on failure.

- IDs: stable, opaque strings, such as `cause-water`. IDs generated for demo messages/intents are session-local, never bank/charity identifiers.
- Money: **major units** (25 means USD 25.00, not 25 cents). Finite JSON numbers, at most two decimal places. Display calculation converts asset values to integer cents before summing and rounds zakat once to the nearest cent. A real backend may prefer decimal strings or integer minor units; map those inside its adapter, not the UI.
- Currency: ISO 4217 `USD` only in this prototype. A proposed currency setting needs approved PKR/other-currency support, trustworthy dated FX, currency precision and conversion policy. Changing a symbol is not conversion.
- Dates: ISO 8601 UTC, e.g. `2026-01-15T09:41:00.000Z`. Display dates use explicit UTC. Static fixture dates are sample dates, not live valuation timestamps.
- Percentages: allocations and displayed growth are 0–100; `illustrativeRate` is a fraction, 0.025. Trends are arbitrary display samples, not market series.
- Every service returns a Promise of its documented resource, not a transport envelope. Arrays may be empty. Mock latency is 420ms (1,800ms with `mockSlow=1`).
- All data is local and resets on refresh. No localStorage, credentials, account linking or telemetry. Mock donation intentions never change campaign totals or create payment receipts.

## Operations and possible transport

All paths below are **unapproved suggestions only**, relative to a future teammate-owned base. They are not contacted by this app and must not be treated as existing endpoints.

| Adapter operation | Input | Current mock output | Proposed transport for discussion |
|---|---|---|---|
| getDashboard() | none | Dashboard with displayName, currency, insight, sample trend/growth and computed summary | GET /dashboard |
| getZakatProfile() | none | ZakatProfile with assets, example nisab/rate, sample flag, updatedAt | GET /zakat/profile |
| saveZakatProfile(payload) | currency, complete assets object | updated ZakatProfile | PUT /zakat/profile |
| getPortfolio() | none | unverified sample Portfolio, allocations and fictional holdings | GET /portfolio |
| getInvestmentEducation() | none | EducationItem[] | GET /education/investing |
| getCauses(filters) | optional category, query | Cause[] after combined filtering | GET /causes with agreed query names |
| createDonationIntent(payload) | causeId, amount, currency | demo-only DonationIntent | POST /donation-intents |
| getAdvisorContext() | none | welcomeMessage and starterQuestions | GET /advisor/context, or approved client-owned content |
| sendAdvisorMessage(payload) | text, optional conversationId | one deterministic local assistant message | POST /advisor/messages |

## Example resources (proposed client-facing shapes)

### Dashboard, currency and summary

```json
{
  "id": "dashboard-demo-001",
  "displayName": "Hadi",
  "currency": "USD",
  "isDemo": true,
  "sampleChangePercent": 4.2,
  "samplePeriodDays": 30,
  "insight": "Set aside a manageable amount for giving.",
  "trend": [12, 18, 17, 29, 25, 38],
  "summary": {
    "totalAssets": 24750,
    "liabilities": 0,
    "netWorth": 24750,
    "eligibleBase": 24750,
    "estimatedDue": 618.75
  }
}
```

Home derives its visible summary from the shared editable profile, not the initial dashboard snapshot, so savings immediately update both screens. Dashboard service reads also reflect the saved mock profile. The future adapter/state agreement should identify an authoritative summary, cache invalidation and version/conflict handling.

### Zakat profile, save payload and provisional breakdown

```json
{
  "id": "zakat-demo-001",
  "currency": "USD",
  "assets": {
    "cash": 12000,
    "investments": 10500,
    "gold": 1500,
    "business": 750,
    "liabilities": 0
  },
  "illustrativeNisab": 6380,
  "illustrativeRate": 0.025,
  "updatedAt": "2026-01-15T09:41:00.000Z",
  "isDemo": true
}
```

Save sends only `{ "currency": "USD", "assets": { ...all five fields... } }`. Each field is required, nonnegative, at most 999,999,999.99, with cent precision. That upper bound is a demo input limit, not a religious rule.

`src/utils/finance.js` is a **provisional educational display utility**:
- totalAssets = cash + investments + gold + business
- netWorth = totalAssets − liabilities (may be negative)
- eligibleBase = max(0, netWorth)
- estimatedDue = eligibleBase × 0.025, rounded to cents

It intentionally does **not** gate on nisab or determine eligibility, haul, asset qualification or debt deductibility. The 6,380 USD threshold is an undated, nonlive illustration, not a universally current threshold. Future backend authority requires collaboratively agreed methodology. Proposed future metadata: valuation date, dated commodity prices, nisab metal/method/source, scholarly methodology/version, haul evidence, currency/FX source, user reminders and payment history. These fields are **not** implemented or treated as known facts.

### Portfolio and screening status

```json
{
  "id": "portfolio-demo-001",
  "currency": "USD",
  "value": 18420,
  "sampleChangePercent": 6.8,
  "samplePeriodDays": 30,
  "isDemo": true,
  "screeningStatus": "unverified",
  "trend": [12, 19, 17, 26, 33],
  "allocations": [
    { "id": "diversified", "label": "Diversified", "percent": 40, "color": "#0B7750" },
    { "id": "healthcare", "label": "Healthcare", "percent": 20, "color": "#549EAD" },
    { "id": "consumer", "label": "Consumer", "percent": 18, "color": "#9CCFAE" },
    { "id": "energy", "label": "Energy", "percent": 12, "color": "#D5B669" },
    { "id": "other", "label": "Other", "percent": 10, "color": "#BAC9BF" }
  ],
  "holdings": [
    { "id": "holding-demo-001", "name": "Cedar Growth Basket", "category": "Diversified", "value": 7368, "isFictional": true }
  ]
}
```

Displayed holdings are a subset, not the complete portfolio. The portfolio is independent of the zakat eligible-investments entry. There are no real tickers or certified companies. Proposed future screening metadata must identify provider, methodology, statement date, assessment date and status limitations. Broker connections, portfolio purification, risk disclosures and trade execution are outside this frontend.

Education returns objects like `{ "id": "business-activities", "title": "Start with the business", "description": "Review activities and revenue sources..." }`. Three cards cover activities, ratios and ongoing monitoring.

### Causes and donation intentions

Filters: `{ "category": "Education", "query": "school" }`. Categories: All, Education, Relief, Masjid. Query matches the trimmed, case-insensitive title; both filters apply together.

```json
{
  "id": "cause-water",
  "title": "Provide Clean Water",
  "category": "Relief",
  "raised": 3420,
  "goal": 5000,
  "currency": "USD",
  "illustration": "water",
  "description": "An illustrative water project, not a verified campaign.",
  "isDemo": true
}
```

```json
{
  "causeId": "cause-water",
  "amount": 25,
  "currency": "USD"
}
```

```json
{
  "id": "intent-demo-1",
  "causeId": "cause-water",
  "amount": 25,
  "currency": "USD",
  "status": "demo_confirmed",
  "isDemo": true,
  "paymentProcessed": false,
  "createdAt": "2026-01-15T09:41:00.000Z"
}
```

Gift validation: 1–100,000 USD, two decimal places, known cause. Presets/custom input converge on one controlled amount. UI disables duplicate submission while pending and retains amount/cause on failure. Only `demo_confirmed` exists now; it means no money moved. Future states such as pending, requires_action, succeeded, failed or canceled need approval and dedicated payment UX. Never relabel this demo confirmation as a successful payment. Backend/product must vet charities, consent, privacy, zakat eligibility vs sadaqah, idempotency, payment provider flow and receipt issuance before real launch.

### Advisor context and messages

```json
{
  "text": "How do I calculate zakat?",
  "conversationId": "conversation-demo-001"
}
```

```json
{
  "id": "message-demo-1",
  "role": "assistant",
  "text": "A common starting point is 2.5% of eligible wealth, subject to nisab and holding-period conditions...",
  "createdAt": "2026-01-15T09:41:00.000Z",
  "isDemo": true
}
```

`getAdvisorContext()` returns `{ "welcomeMessage": AdvisorMessage, "starterQuestions": string[] }`. Input: trimmed text, 1–1,000 characters. Mock keyword selection is deterministic; it never sends conversation content off-device. Chat remains mounted across tab changes, but resets on reload. Failed requests show retry/edit; retry does not add another user bubble. There is no streaming or model inference.

A future secured advisor backend needs agreed conversation ownership, privacy/sensitive-data policy, source citations, curated vetted retrieval, safety checks and scholarly review. Generic finance dialogue training is not evidence of Islamic-finance expertise. API keys must never enter browser source or Vite variables.

## Pending, error and empty-state agreement

| Operation | Pending UI | Recovery / common errors |
|---|---|---|
| Dashboard / zakat profile | full device loading status and skeleton | Try again; future unavailable, unauthorized or missing-profile cases |
| Save profile | disabled fields + Saving assets | draft kept; retry; invalid input, unsupported currency; future version conflict |
| Portfolio / education | local screen loading | Try again; empty holdings invite education; future unavailable/stale source |
| Causes | local loading on query/category changes | Try again or clear filters; [] is a valid empty search result; newer filters win stale races |
| Donation intent | disabled inputs + Confirming demo gift | amount/cause kept, retry; unknown cause, invalid amount/currency; future eligibility/payment errors require agreement |
| Advisor context | local guide loading | Try again |
| Advisor message | pending example status; sending disabled | retry same question or edit it; empty/overlong question; future rate-limit/safety errors |

Services reject `Error` with safe user-facing `message`. Injected failures additionally expose `code: "MOCK_UNAVAILABLE"`; validation currently throws ordinary Error. Proposed future normalized error fields (`code`, `retryable`, `fieldErrors`, `requestId`) need agreement. Do not expose stack traces, private financial data or raw server errors to users.

Mock test controls (comma-separated):
- `?mockError=getDashboard,saveZakatProfile,getCauses,createDonationIntent,sendAdvisorMessage` fails the first listed request once per page load. Any operation in the table is supported.
- `?mockEmpty=causes,portfolio`
- `?mockSlow=1`

Use production preview for deterministic fault demonstrations; React StrictMode intentionally replays development read effects.

## Swapping adapters later (documentation only)

1. Agree resource shapes, currency/precision, validation, errors, authorization, dates and religious authority with the backend teammate.
2. Teammate implements an `httpAdapter` matching `ServiceAdapter`, reading one `VITE_API_BASE_URL` configuration value. No such adapter, config dependency or fixed live URL exists here.
3. Select it in `src/services/index.js`. Normalize transport envelopes, dates, money and errors there. Components continue importing the same functions.
4. Agree session security and never put secrets in browser config. For mutations, define server-side validation, conflict handling and idempotency before real transactions.
5. Replace the provisional calculation authority through the agreed service/state mapping. Preserve explicit estimate provenance and eligibility language; do not silently replace example nisab with an undated number.
6. Re-run unit/service checks and the interaction acceptance checklist in README, including unavailable/empty/slow states. Additional live-account or payment workflows will need separately agreed scope, not cosmetic relabeling of this prototype.
