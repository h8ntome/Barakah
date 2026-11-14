# Barakah

**Islamic Finance for a Blessed Tomorrow.**

A complete React 18 frontend prototype: five interactive screens, a single-phone desktop showcase, and an edge-to-edge mobile app. **Frontend only.** No backend, database, authentication, market feed, live AI, payments, credentials or cloud infrastructure.

## Run

Node **20.19+ or 22.12+** (Vite 7 requirements).

```sh
cd barakah-ui
npm install
npm run dev
```

The app serves on the local address Vite prints (normally http://127.0.0.1:5173).

```sh
npm test
npm run build
npm run preview
```

The prototype needs no environment variables and makes no remote service or font requests at runtime. Fonts and their licenses are bundled. All sample changes reset on refresh; there is deliberately no storage of financial information.

## Explore the demo

- **Home:** sample 24,750 USD net worth, local estimate, four destination shortcuts, interactive priorities and an everyday financial habit.
- **Zakat:** edit all four asset categories and liabilities, preview the estimate, save asynchronously, and see Home/Zakat update together. Cancel leaves the saved profile unchanged.
- **Invest:** sample 18,420 USD portfolio with allocation chart, explicitly fictional baskets, and three educational screening criteria. No live certification or orders.
- **AI Chat:** three suggested questions or your own text; deterministic local examples with pending/retry/edit states. Enter sends. Conversation survives switching tabs.
- **Give:** combine search/category filters, explore illustrative causes, choose preset/custom amounts and confirm a **demo intention only**. No money is sent.
- Native dialogs provide focus containment, Escape/backdrop dismissal and return focus. In-flight mutations cannot be accidentally dismissed.

## Mock request controls

Use the production preview for fault demos. React StrictMode replays read effects in development.

- `/?mockError=getDashboard` — initial error, then Try again succeeds.
- `/?mockError=saveZakatProfile,createDonationIntent,sendAdvisorMessage` — first mutation attempt fails; the draft is retained for retry.
- `/?mockError=getPortfolio,getInvestmentEducation,getCauses,getZakatProfile,getAdvisorContext` — resource errors.
- `/?mockEmpty=causes,portfolio` — empty resource states.
- `/?mockSlow=1` — 1.8s requests instead of 420ms. Controls can be combined.

Faults occur once per named operation per page load, not randomly. A new query never gets overwritten by a stale response.

## Structure

```text
src/
  App.jsx                  shared profile and active destination; tabs stay mounted
  components/ui.jsx        reusable UI, charts, native dialog and request states
  screens/                 Home, Zakat (+ editor), Invest, Chat, Give (+ gift dialog)
  services/
    index.js               sole replaceable adapter-selection point
    mockAdapter.js         asynchronous local operations and validation
    useResource.js         read lifecycle, retry and stale-result protection
  mocks/data.js            all fixture values and deterministic example replies
  types/api.d.ts           documented client-facing API shapes
  utils/finance.js         formatters and provisional pure display calculations
  styles.css               responsive tokens, components and states
public/fonts/              local licensed fonts
tests/                     Node unit and adapter contract tests
API_CONTRACT.md            proposed teammate handoff, not implemented endpoints
```

The desktop panel and phone use the same navigation state. Screens import service functions/hooks, never fetch. The mock adapter owns its local copy, while React owns the displayed editable profile. Financial totals are derived from that profile every render.

## Important limitations

USD is a prototype choice, not a user-selected or converted currency. The simplified zakat illustration is `max(0, assets − liabilities) × 0.025`, rounded to cents. It does not test nisab or lunar holding-period eligibility. The nisab shown is a nonlive example; asset eligibility, debt treatment, precious-metal rates and scholarly methodology require qualified review.

Portfolio performance, chart values, holdings, causes and beneficiaries are illustrative. Portfolio holdings are separate from the eligible-investments entry. The guide is not an AI scholar or a live model; its answers are education, not personalized advice or a fatwa.

Before real launch: agree the draft contract with the backend teammate, replace only the adapter/configuration/schema mapping for existing flows, and separately scope auth, vetted screening, currency/FX, charity verification, secured advisor behavior and payments. See **API_CONTRACT.md**.

## Acceptance checklist

1. At 320px, 390px, tablet and desktop, verify no horizontal overflow, readable text, scrollable content above persistent tabs and visible focus.
2. Change cash from 12,000 to 13,000; preview/save must show 25,750 net worth and 643.75 estimated zakat. Set all amounts to zero, then test liabilities greater than assets. Cancel must not save.
3. Test dialog keyboard containment, Escape and restored trigger focus; fields reject negative/overprecision amounts.
4. Switch investment segments; allocation totals 100%; no verified/guaranteed-return claims.
5. Search “school”, combine categories, search nonexistent text and clear filters. Exactly one category stays selected.
6. Choose preset/custom gifts; confirmation explicitly says no money moved. Retry a failure without losing amount.
7. Send every chat starter, Enter-send custom text, switch tabs and return, and retry a failure without duplicate user messages.
8. Inspect slow, error, retry and empty resources with mock query controls; check browser errors and production build.

No lint script existed in the supplied starter. Automated Node tests cover money edge cases, validation, adapter isolation, async behavior, filtering, draft-safe failures, demo intentions and deterministic responses. Browser validation is recorded in `QA.md`.

## Assets

`reference/barakah-concept.png` is the team-supplied concept, retained as design guidance and never shipped as the app UI. The arch logo is authored SVG; interface art uses Lucide line icons. Font sources/licenses: `public/fonts/`. No third-party beneficiary photos or invented endorsements.

Repository-level `PRODUCT.md`, `DESIGN.md` and `.impeccable/surfaces/app.md` record product/design decisions. Build output, dependencies, secrets and browser screenshots are excluded from Git.
