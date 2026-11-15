> **Historical pre-release report — not current release status or approval.** This document describes the earlier unavailable-AI build/export. Local AI is now connected, advice remains unverified, and public AI remains unavailable. See [FINAL_RELEASE.md](FINAL_RELEASE.md) and [CLAIMS_AND_EVIDENCE.md](CLAIMS_AND_EVIDENCE.md) for the current film. Original findings below are preserved, not reasserted.

# Production readiness audit — 15 November 2026

Audited commit: `3fe4fa7b4d6324cb4f235dc1a1b3536d2c032335`. No application or benchmark source was changed for this production.

## Architecture

- Frontend: React 18.3.1, Vite 7.3.8, `barakah-ui/src/main.jsx` → `App.jsx`. Existing emerald/mint/ivory UI, Georgia wordmark/editorial type, local DM Sans and Manrope. Original desktop editorial panel and interactive phone retained; mobile capture uses the app's existing responsive layout.
- Backend: FastAPI 0.163.0, `backend/app/main.py`, `/api/v1`. SQLAlchemy 2.0.40 + Alembic 1.15.2; SQLite isolated for filming, PostgreSQL supported but not used in this production.
- Authentication: Argon2id passwords, in-memory access JWT, rotating HttpOnly refresh cookie and CSRF protections. Existing Try Demo endpoint creates a unique non-admin owner; no password or authentication secrets appear in footage.
- Schema: owner-scoped users, sessions, accounts, transactions, budgets, goals/contributions, zakat profiles/history/payments, sadaqah, portfolios/holdings/trades/quotes/screening history, advisor conversations/messages. Decimal amounts, not binary floating-point accounting. See `backend/app/models.py`; migration head `c28e9f1b2a53`.
- Model serving: **none in the app**. `backend/app/config.py` accepts only `AI_MODE=unavailable`; `ai.py` has no inference transport or model loader. Active checkpoint: **none**. The historical benchmark's model is not connected to the UI.
- Historical model: `LiquidAI/LFM3-1.7B`, revision `1da06bec6a819da10b54c67e5c90972b46d81871`, BF16 Transformers/ROCm on server2. No verified team-adapted checkpoint. Weights are not included in this project and were not downloaded for the app.

## Runtime readiness

| Area | Finding | Film treatment |
|---|---|---|
| Demo authentication | Working, isolated existing Try Demo mechanism | Actual browser sign-in recorded; fictional profile renamed Amina Rahman through Settings |
| Dashboard | Working stored totals, month filter, categories | Actual date changes and spending navigation |
| Persistence | Profile and totals survive browser refresh | Verified, not just a React-state demonstration |
| Zakat | Working server calculation and immutable saved snapshot | $15,000 declared eligible wealth × 2.5% = $375, with fictional $5,000 nisab and attested haul |
| Sadaqah | Working record history and totals | $125 across two fictional records; no payment processing |
| Investments | Working manually valued holdings, allocation, education | $8,500 fictional valuations; screening explicitly unverified |
| Screening | Educational configurable machinery exists; no seeded assessments or external certification | No approval claim; source/date/manual limits shown |
| AI chat | UI and real request path work; inference deliberately unavailable | Actual submit → unavailable message. No substituted response |
| Market feed | Unconfigured | No live prices or return claims |
| Cause directory | Empty; no approved causes seeded | Not presented as working charity discovery |
| Benchmarks | Existing 100-question dataset and historical results available, provenance hashes checked | Narrow 15-question arithmetic comparison and exact model failure shown |
| Expert validation | 60 conceptual questions pending, no verified expert results | Clearly disclosed |
| Production deployment | Not verified, not used | Loopback-only isolated prototype |

## Safe demo environment

`demo-video/scripts/prepare-demo.py start` builds the existing frontend into `demo-video/.runtime/app-dist`, migrates only `demo-video/.runtime/demo.sqlite`, and starts the backend on `127.0.0.1:8095`. It does not reuse the default database or running teammate servers. No production records were touched. The ephemeral demo expires after 24 hours; rerunning capture creates a fresh demo. Credentials are not required or saved.

## Existing fixture, not the proposed illustrative fixture

$4,500 income − $2,850 expenses = $1,650 surplus. Checking $3,000 + savings $12,000 = $15,000 cash; manually valued portfolio $8,500 → tracked net assets $23,500; liabilities $0. The declared zakat profile contains $15,000, not all $23,500 dashboard assets. The portfolio is not automatically included in the zakat profile: treatment requires independent eligibility review. No claim that excluding those holdings is universally correct.

Giving history is $50 + $75 = $125, not the suggested $320. Seeded Hajj goal is $5,000, with $1,250 progress; this earmark is not extra wealth. No mock stock-price feed, certified approvals, real people's finances or user testimonial is shown.

## Test commands actually run for production

- `(cd backend && env -u TEST_DATABASE_URL .venv/bin/python -m pytest -q)` → **113 passed**, one Starlette/httpx deprecation warning. Tests use temporary isolated DBs.
- `npm test --prefix barakah-ui` → **64 passed**.
- Isolated Vite production build → passed.
- `python3 demo-video/scripts/capture-demo.py` → completed real UI workflow, assertions and capture logs.

## Blocking competition limitation

The official rules require AI/ML to perform the main function, not merely AI-assisted development. The Finance brief asks for comparison to a simple rule and an advantage. This app currently has no live AI, and the preserved narrow benchmark favors the calculator. The video is an honest polished prototype demonstration, **not evidence that the current submission satisfies those core requirements**. Do not submit it as proof of functional AI. No large integration/refactor or training was attempted to conceal this boundary.
