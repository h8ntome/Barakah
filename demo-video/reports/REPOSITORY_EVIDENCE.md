> **Historical pre-release report — not current release status or approval.** This document describes the earlier unavailable-AI build/export. Local AI is now connected, advice remains unverified, and public AI remains unavailable. See [FINAL_RELEASE.md](FINAL_RELEASE.md) and [CLAIMS_AND_EVIDENCE.md](CLAIMS_AND_EVIDENCE.md) for the current film. Original findings below are preserved, not reasserted.

# Repository evidence for the demo film

**Scope:** static, read-only repository audit. No app imports, database connections/operations, service calls, training, inference, migrations, or test-suite execution. Only this external report was written. “Ready” below means implemented in source, **not a verified running deployment**. Paths are relative to `/Users/hadi/Documents/Barakah`.

## Feature readiness matrix

| Feature | Film-safe readiness / limitation | Primary evidence |
|---|---|---|
| Try Demo | Implemented: isolated fictional owner, 24-hour expiry, reset replaces owner and invalidates old access; bounded cleanup of up to 100 expired demo owners. No fixed credentials. | `backend/app/demo.py`; existing assertions in `backend/tests/test_demo.py` |
| Accounts, cash flow, budgets, dashboard | Implemented deterministic tracking and stored-data summaries; no bank sync or money movement. | `backend/app/finance.py`, `backend/app/calculations.py` |
| Zakat | Educational estimate from declared assets, liabilities, nisab and user-attested haul; history/payment records supported, not a religious ruling or payment processor. | `backend/app/giving.py`, `backend/app/calculations.py`, `backend/app/schemas.py` |
| Sadaqah / goals | Implemented records and contribution progress; not transfers. Donation intents and zakat payments explicitly report `payment_processed: false`. | `backend/app/giving.py` |
| Portfolio / screening | Manual holdings, trades, cost basis, dated quotes and configurable educational ratio checks. Seed holdings are **unverified**, despite one fictional holding’s “screened equity example” name. No brokerage execution or certified halal classification. | `backend/app/portfolio.py`, `backend/app/models.py`, `backend/app/calculations.py` |
| Live market / metal prices | Unconfigured: stock lookup returns 503 `market_provider_unavailable`; metal prices return `prices: null`, `source: manual_entry_required`, `is_live: false`. | `backend/app/market.py` |
| AI advisor | **Deliberately unavailable; active app checkpoint: none.** Only `ai_mode: Literal['unavailable']` is accepted. No model loader, inference transport or generated advice in boundary. Authenticated health returns provider/status `unavailable`, `is_demo: false`. Valid authorized send returns 503 `ai_unavailable`, `response: null`, saves no messages/conversations and loads no private history/totals. Historical owned chat remains readable/deletable. Consent cannot enable AI. | `backend/app/ai.py`, `backend/app/advisor.py`, `backend/app/config.py`, `docker-compose.yml`, `audit/AI_INTEGRATION.md`; existing `backend/tests/test_advisor_ads.py` |
| Auth | Registration/login/profile/password/reset/deletion implemented; Argon2 passwords, HS256 access JWTs (15 minutes), hashed refresh/CSRF tokens, rotating 30-day refresh sessions, trusted-Origin/CSRF checks. Demo users cannot password-login. Reset delivery defaults unconfigured and returns 503. Production requires strong secret, secure cookies, explicit HTTPS origins. Rate limiter is in-process, not distributed. | `backend/app/auth.py`, `backend/app/security.py`, `backend/app/config.py`, `backend/app/mail.py` |
| Persistence / schema | SQLAlchemy owner-scoped records and cascading owner FKs; exact Decimal storage (SQLite text, PostgreSQL NUMERIC(24,6)); transactions commit/rollback, SQLite `BEGIN IMMEDIATE`. Default URL `sqlite:///./barakah.db`. Five Alembic revisions, source head `c28e9f1b2a53`; applied DB version unknown. `/health` is liveness; `/api/v1/health` checks DB/schema separately from AI. | `backend/app/db.py`, `backend/app/models.py`, `backend/app/common.py`, `backend/app/schemas.py`, `backend/alembic/versions/`, `backend/app/main.py` |

## Exact Try Demo fixture (USD)

Source: `backend/app/demo.py::seed`; amounts below are source constants or arithmetic derived from the implemented calculators, **not queried live balances**. Dates use `date.today()`; previous history uses the last day of the prior month; goal date is today + 365 days.

- **2 accounts:** checking opens **1,350.00**, savings **12,000.00**. Current-month salary **4,500.00**; expenses Housing **1,500.00**, Food **400.00**, Transport **300.00**, Utilities **250.00**, Household **400.00** = **2,850.00**. Checking ends **3,000.00**; combined cash **15,000.00**.
- **8 transactions:** current month 6; prior month salary **4,200.00** and Household expense **4,200.00** (zero net effect). Current-month savings **1,650.00**, savings rate **36.67%**.
- **3 budgets:** Food **500.00** / spent **400.00** / remaining **100.00**; Housing **1,500.00** / spent **1,500.00** / remaining **0.00**; Transport **350.00** / spent **300.00** / remaining **50.00**.
- **1 zakat profile + 1 history:** cash **3,000.00**, savings **12,000.00**, other assets/liabilities **0.00**; manual fictional nisab **5,000.00**, haul complete, default rate **0.025**. Eligible base **15,000.00**, due **375.00**. **No zakat payment seeded.** The separate portfolio is not automatically included in this declared zakat profile.
- **2 sadaqah records:** community kitchen **50.00**, education fund **75.00**; total **125.00**. Records say no payment sent.
- **1 goal + 1 contribution:** Hajj target **5,000.00**, saved **1,250.00**, remaining **3,750.00**, progress **25.00%**. This is tracked progress, not a checking-account debit.
- **3 holdings + 3 buys:** DEMO-A **100 × 50 = 5,000.00**; DEMO-B **50 × 50 = 2,500.00**; DEMO-C **10 × 100 = 1,000.00**. Default fees **0.00**; manual quotes equal purchase prices. Total cost/value **8,500.00**, realized/unrealized gains **0.00**. Quote source: `Fictional manual valuation; NOT live`. Allocations **58.82% / 29.41% / 11.76%**. No screening assessments seeded.
- Dashboard total assets/net worth **23,500.00** = cash **15,000.00** + manual portfolio **8,500.00**, liabilities **0.00**. Do not confuse dashboard assets with zakat eligible base **15,000.00**.
- No advisor conversations/messages, causes, donation intents or ads are created by this seed.

**A second, different fixture exists:** `scripts/demo.py` is a loopback-only CLI that registers a regular private account, not the expiring Try Demo workspace. Do not mix its numbers into the film: opening **1,000.00**, salary **4,000.00**, Food **600.00**, Housing **1,200.00**, closing **3,200.00**; Food budget **800.00**. Zakat cash **12,000.00**, liabilities **1,000.00**, eligible **11,000.00**, gold **80.00/g × 85g = 6,800.00** nisab, due **275.00**, recorded payment **100.00**; sadaqah **50.00**. Holding **10 × 20.00 + 1.00 fee = 201.00** cost, quote **21.00**, value **210.00**, unrealized gain **9.00**. Neither seeder was run.

## Historical benchmark: actual file counts and processed results

Independently parsed `benchmark/datasets/benchmark_questions.json` and `.csv`: **100 JSON items, 100 unique IDs, 100 CSV rows**. `conceptual_questions.json` contains **60**, already included in the 100, not additional questions. Difficulty: **28 easy / 49 medium / 23 difficult**. Review status: **40 arithmetic_verified / 60 reference_checked_pending_expert / 0 expert-reviewed**.

| Category | Dataset | Numeric tasks | Saved original numeric correct | Conceptual pending |
|---|---:|---:|---:|---:|
| Budgeting | 20 | 20 | 20/20 | 0 |
| Investing | 25 | 0 | Not applicable | 25 |
| Principles | 20 | 5 | 4/5 | 15 |
| Safety | 10 | 0 | Not applicable | 10 |
| Zakat | 25 | 15 | 12/15 | 10 |
| **Total** | **100** | **40** | **36/40 (90%)** | **60** |

- Original run `original_20261114T184206126429+0000`: actual raw JSONL **100 unique responses**, processed **100 scores**; **36 correct, 4 incorrect, 60 nonnumeric**, **0 generation errors**, **0 missing**, **2 truncated**. Incorrect IDs: `PRINCIPLE_020`, `ZAKAT_007`, `ZAKAT_008`, `ZAKAT_015`.
- Rules run `rules_20261114T184236288070+0000`: actual raw/processed **15 each**, **15/15 correct**. Processed `missing_responses: 85` reflects the intentionally narrow scope against the 100-item dataset, not 85 failed generations. Matched zakat comparison: model **12/15 (80%)**, calculator **15/15 (100%)**, **+20 percentage points**, not fine-tuning improvement.
- Original processed latency: mean **12.836641286650265 s**, median **13.425578521502757 s**, P95 **24.576828320998175 s**; **19,599 output tokens**, **15.268012529400812 tokens/s** aggregate. These are historical server2 timings, not app latency or Mac inference performance.
- **6/100 heuristic-flagged responses are review candidates, not confirmed safety failures.** Human-reviewed correctness, verified safety failure rate and verified hallucination rate are **null/unavailable** with **0 reviewed**; all **100** safety/hallucination reviews remain pending.

Primary evidence: `benchmark/results/raw/{run_id}.jsonl` and `{run_id}.meta.json`, `benchmark/results/processed/{run_id}.json`, `benchmark/results/comparisons/original_20261114T184206126429+0000__rules_20261114T184236288070+0000.json`.

## Model identity and provenance boundary

- Historical evaluated model: **Liquid AI’s instruction-tuned `LiquidAI/LFM3-1.7B`**, not `LFM3-1.7B-Base`, approximately **1.73B parameters**. Revision **`1da06bec6a819da10b54c67e5c90972b46d81871`**. No adapted/fine-tuned candidate is present in the saved results; no active app checkpoint is configured.
- `benchmark/config.yaml`, original raw metadata, `benchmark/reports/MODEL_CARD.md`: BF16, no quantization, Transformers/ROCm on AMD Radeon 8060S (`server2`), greedy batch-one generation, thinking disabled, **384-token cap**, seed **2026**, SDPA. Recorded run completed **2026-11-14T19:03:48.013272+00:00**.
- `benchmark/results/hardware/model_download.json` records reused official cache, **286 tensors**, **3,457,635,448-byte** safetensors and recorded verified SHA256 **`135922caef64e81e52af88ede8b7c3ddaa9d6da220a9737fb3065275dbfb4330`**. Weight hash is historical metadata, **not reverified against external weights in this audit**. `benchmark/models/` contains only `.gitkeep`; model card says no weights included. License recorded as **LFM Open License v1.0**.
- Dataset JSON SHA256 **`c8a9636cc9ad96cbfb1049168227a23e5fc213ce245264be44984667578801fb`**. Audit recomputed JSON/CSV hashes against the manifest and both processed files’ dataset/raw/metadata hash bindings: **all matched**.
- `benchmark/datasets/DATASET_CARD.md` and `SOURCE_EVIDENCE.md` distinguish authored arithmetic and AI-assisted institutional source research from independent qualified review. Source excerpts, dates, hashes and mappings exist; no external sources were fetched in this audit.

**Film claim guardrails:** say “historical baseline: 36 of 40 numeric tasks,” never “90% Islamic-finance accuracy.” Small authored English dataset, repeated templates, single run, unknown pretraining overlap, no expert conceptual grading, incomplete safety evidence, finite output cap and shared hardware limit generalization. Rules baseline assumes eligibility and cannot provide religious advice. No fine-tuning improvement, live AI integration, app-wide benchmark, cross-host speedup or certification is demonstrated. Historical benchmark prose calling the frontend a mocked prototype is not authoritative for the current backend-backed application.

## Validation / residual risks

Read source and existing tests only; no tests added or run (backend tests would operate databases). Standard-library `python3 -B` read-only scripts counted datasets/raw/processed records and checked SHA256 bindings. One initial inspection assumed every score had `status` and raised `KeyError` on conceptual rows; corrected with an explicit nonnumeric category and rerun successfully. No repository files were edited or staged. Final inspected `git diff --cached --name-only` was empty; `git status --short` showed an unrelated concurrently appearing `?? demo-video/`, untouched by this audit.

Runtime UI, deployed environment, database state, SMTP delivery and migrations remain unverified. Existing tests provide source-level corroboration, not fresh passing test evidence. Recommended next step: independent review of this report, then a separately authorized runtime rehearsal using the **Try Demo** fixture; film AI as explicitly unavailable.
