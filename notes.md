# Barakah — shared agent notes

This is the shared handoff file for AI agents working on this repository. Read it before relevant work and update it when you confirm a decision, finish a meaningful change, discover a blocker, or hand work to another agent.

## How to maintain this file

- Keep notes concise, actionable, and current. Replace obsolete status rather than appending an endless transcript.
- Date important findings and distinguish **verified**, **reported**, and **proposed** information. Recheck dated facts before relying on them.
- Record what changed, why, how it was checked, and what remains. Preserve other agents’ work and attribution.
- Never store secrets, tokens, credentials, private financial information, or raw conversation logs here.
- This file supports coordination; it does not override the user’s instructions or agreed ownership boundaries.

## Project and ownership

- **Product:** Barakah — “Islamic Finance for a Blessed Tomorrow.”
- **Frontend:** React 18 + Vite + lucide-react + standard CSS, located in `barakah-ui/`.
- **Scope:** frontend-only prototype. A separate teammate owns backend, database, authentication, payments, market data, and live AI integration. Do not implement those without a new explicit assignment.
- `benchmark/` and `.pytest_cache/` were present as unrelated, untracked work during frontend delivery. They were left untouched. Check ownership before editing or staging them.

## Important files

- `README.md` — repository entry point and Vercel configuration guidance.
- `barakah-ui/README.md` — setup, features, mock controls, and acceptance checklist.
- `barakah-ui/API_CONTRACT.md` — **draft**, not an approved or implemented backend API.
- `barakah-ui/QA.md` — dated validation evidence and testing limits.
- `PRODUCT.md`, `DESIGN.md`, `.impeccable/design.json` — product context and implemented design system.
- `barakah-ui/src/services/index.js` — single adapter-selection boundary.
- `barakah-ui/src/services/mockAdapter.js` — asynchronous local services.
- `barakah-ui/src/mocks/data.js` — sample data and deterministic advisor responses.
- `barakah-ui/src/types/api.d.ts` — documented service/resource shapes.
- `barakah-ui/src/utils/finance.js` — formatters, validation, provisional zakat calculation.

## Current frontend behavior

- Five working destinations: Home, Invest, Zakat, AI Chat, Give.
- Home and Zakat derive their totals from one editable React profile. Default sample net worth is USD 24,750; illustrative estimated zakat is USD 618.75.
- Zakat uses `max(0, assets − liabilities) × 0.025`, rounded to cents. This does **not** establish nisab eligibility, haul, asset qualification, or an authoritative religious ruling.
- **No AI model is connected.** `sendAdvisorMessage()` selects predefined keyword-based examples in the mock adapter. No OpenAI/Claude/model inference or external chat requests occur.
- Chat, filters, and other screen state survive tab switches. Local demo changes reset on refresh; no browser persistence is implemented.
- Donations are simulated intentions only. No payment, real donation, or receipt is created. Securities, returns, causes, and beneficiaries are illustrative.
- Default currency is USD. Currency/FX support, religious methodology, security and real integrations require agreement with the backend teammate.

## Running and checking

From the repository root:

```sh
cd barakah-ui
npm install
npm test
npm run build
npm run dev
```

Use a Node version supported by Vite 7 (20.19+ on Node 20, or 22.12+). No environment variables are needed for the demo.

**Last verified 2026-11-14:** clean installation, production build, and all 16 Node tests passed; npm audit reported zero vulnerabilities. Browser checks covered 320px through desktop, primary interactions, loading/error/retry/empty states, and dialog keyboard behavior. Full real-device, screen-reader, Safari and Firefox audits were not performed.

## Git and deployment handoff

**Verified 2026-11-14:** configured remote was `origin` → `https://github.com/h8ntome/Barakah/`; frontend work was pushed to `feat/barakah-frontend`. Always inspect the current branch, remote and staged files before publishing; do not force-push or include another teammate’s files.

- `e10ee1ed4c64c594a65e906b6505fd898c7581a1` — complete frontend/mock-service delivery.
- `60035c085b9e6ef9e1383c46342533f8013d39cb` — root `vercel.json` and deployment guidance.
- Root Vercel configuration installs with `npm ci --prefix barakah-ui`, builds with `npm run build --prefix barakah-ui`, serves `barakah-ui/dist`, and supplies an SPA fallback.
- **Open blocker, last checked 2026-11-14:** GitHub reported the Vercel deployment of `60035c0` successful, but `https://barakah-gamma.vercel.app` still returned 404. `/barakah-ui/index.html` exposed unbuilt source HTML. Do not claim the public site works based only on a successful deployment status.
- The agent could not inspect/change Vercel project settings or promote the deployment because Vercel required login. Next authorized operator should verify Root Directory `.`, Production Branch `feat/barakah-frontend`, repository-supplied build/output settings, and production promotion; then check the actual public UI in a browser. These settings were recommended, not confirmed as the current dashboard configuration.
- This checkout is cloud-synced and repeatedly offloaded source and `.git` files, causing intermittent `Resource deadlock avoided`/mmap errors. Local validation snapshots were used when needed. Treat such errors as filesystem problems, not proof of bad Git credentials. Do not overwrite metadata or teammate work to work around them.

## Latest handoff

**2026-11-14 · coding assistant:** Created this shared notes file at the user’s request. Keep it maintained during subsequent project work, especially when the Vercel blocker is resolved, the API contract is approved, or the mock advisor is replaced by a real backend service.
