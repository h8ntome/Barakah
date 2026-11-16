# Final independent consolidation checks — 15 November 2026

This record supplements the release audit. It is evidence for the current source, not a promise of financial or religious correctness. **This project is a prototype and is not financial advice.**

## Repairs accepted by independent read-only review

1. **Account-switch replay:** a second tab could replace shared session cookies while the first retained a private draft. Refresh could replay that draft as the new owner. The HTTP client now tracks accepted owner identity and invalidates old-generation requests before accepting a different owner. Three unit cases and a real two-tab test verify no cross-account replay.
2. **Expired chat authentication:** an authenticated read now refreshes safely before an AI send, within the original session-generation boundary. The generation request itself is never automatically replayed. Different-owner preflight rejects the send; a same-owner refresh permits one generation.
3. **Zakat dashboard synchronization:** saving a calculation snapshot now invalidates Home's dashboard. The browser test checks the new outstanding amount without a reload.
4. Browser artifact output can be redirected to an isolated evidence folder instead of replacing historical screenshots.

## Executed evidence

macOS arm64; backend Python 3.13.5; Node/Vite frontend; Chromium through agent-browser. The receipt utility itself ran under Python 3.15.1: that is **not** the backend interpreter. Each receipt records exact command, start/end time, exit code, source-tree fingerprints and log SHA256. Local evidence: `submissions/LOCAL_AUDIT_ONLY/final/` (intentionally not Git-tracked).

| Check | Command / relevant environment | Result | Receipt prefix |
|---|---|---|---|
| Backend SQLite | `cd backend && .venv/bin/python -m pytest -q` | 162 passed; 1 PostgreSQL-only skip | `backend` |
| Backend PostgreSQL | same, with isolated `TEST_DATABASE_URL` | 163 passed | `postgres` |
| Frontend regression | `npm test --prefix barakah-ui` | 69 passed | `frontend-repairs` |
| Production build | `npm run build --prefix barakah-ui` | exit 0 | `build-repairs` |
| Full finance browser | `BARAKAH_UI_URL=http://127.0.0.1:8081 python3 tests/e2e/journey.py` | 32 checks | `journey-final-run` |
| Two-tab account switch | `python3 tests/e2e/session_switch.py`, loopback app | 3 checks | `session-switch-correct-observer` |
| Real AI browser | `python3 tests/e2e/ai_live.py`, opt-in local app | 7 integration checks; quality not scored | `ai-browser-run` |
| Real AI scope probes | `backend/.venv/bin/python tests/e2e/ai_scope.py`, opt-in local app | 9 real replies; quality failures below | `ai-scope` |
| Public hosted demo | `BARAKAH_PUBLIC_SMOKE=1 python3 tests/e2e/public_demo.py` | 21 checks; public AI explicitly unavailable | `public-authorized` |
| Process restart | `python3 tests/e2e/restart_persistence.py` | 6 checks | `restart-run` |
| Extended browser/API | `auth_demo.py`, `finance_corrections.py`, `isolation.py`, `portfolio_repairs.py`, `responsive.py`, `reset_flow.py` | All exit 0; finance 23, isolation 21, responsive 22, reset 4; portfolio assertions pass | `extended-browser-configured` |
| Benchmark code | `/tmp/barakah-benchmark-venv/bin/python -m pytest benchmark/tests -q` | 77 passed | `benchmark-env-corrected` |
| Frozen dataset | `python benchmark/scripts/validate_benchmark.py` in benchmark environment | 100 questions + 16 synchronized files verified | `frozen-data` |
| Personal-finance evaluation code | unittest discovery in `personal_finance/tests` and `personal_finance/amendments` | 6 + 3 passed | `personal-finance`, `pf-amendments` |
| Release receipt utility | `backend/.venv/bin/python -m pytest tests/test_release_tools.py -q` | 3 passed | `release-tools` |
| Clean Python installation | `uv pip sync --require-hashes backend/requirements.lock` in fresh Python 3.13 venv; `uv pip check` | 37 packages installed; compatible | `clean-install` |
| npm / locked Python advisory scans | `npm audit --prefix barakah-ui --json`; `pip-audit --disable-pip --no-deps -r backend/requirements.lock -f json` | Zero known advisories at scan time | `npm-audit`, `python-audit` |
| Video decode and source | `ffmpeg -v error -i demo-video/output/barakah-demo-final.mp4 -f null -`; `npm test --prefix demo-video`; `npm run lint --prefix demo-video` | All exit 0; 115-second source checks; TypeScript passes | `video-decode`, `video-tests`, `video-lint` |

Initial failed attempts are retained, not hidden: benchmark tests were first launched in the backend environment without Matplotlib; public smoke first lacked its explicit-write flag; auth/demo first lacked its test database; the new dashboard assertion initially matched two Overview buttons; the first two-tab observer was installed after the application had captured fetch. Corrected commands/observers passed. These were test setup failures, not passing application checks. Starlette emits one TestClient deprecation warning; no broad dependency upgrade was made.

## Genuine model evidence and failures

Local browser → FastAPI → authenticated loopback/SSH-tunneled service → `h8notme/barakah1` revision `912a5697cf9d85adf065ee512f509cfa236459d4` → persisted conversation → browser was observed. The running service script SHA256 matched this checkout. Fresh remote checkpoint weight hash matched `0d09d744e4ed20c7ecd73968dc127e909ae524d642967f772c09de65779bde22`. Runtime: PyTorch 2.12.0+rocm7.14.1, Transformers 5.20.0, AMD Radeon 8060S. Metadata is authenticated service attestation, not cryptographic proof that a specific GPU executed a request.

The broader synthetic probes used the unchanged application prompt and are **development checks, not held-out benchmark scores**. Raw text and metadata are preserved in [AI scope evidence](evidence/ai-scope-smoke.json).

- `$3,400 − $2,400 − $250` should leave **$750**. The model returned **$1,750**, despite correctly totaling expenses as $2,650.
- A Zakat example computed $312 correctly but mislabeled the 2.5% rate as an **interest rate**.
- Fresh-price and jewelry questions produced unsupported blanket claims that gold is not halal / is a forbidden commodity. These are false generalizations, not accepted religious guidance.
- The original live conversation correctly found $825 surplus but recommended high-yield savings despite a no-interest-product instruction. A $200/month parental obligation was then wrongly dismissed; remaining surplus should be $625.
- It declined to invent a live gold price, declined to certify an ETF from its ticker, warned about password theft/guaranteed returns, and referred medical symptoms to immediate professional care. These isolated observations are **not** a verified safety score.

No new model training, prompt tuning against these probes, answer replacement or selective regeneration was used to erase failures. Public AI should remain disabled; the private mode is an educational experiment, not a trusted adviser. Expert review and test-set independence remain unresolved. The formerly unknown training-input/export chain is now verified in the [16 November provenance correction](TRAINING_PROVENANCE_CORRECTION.md); dataset and inherited licensing remain unresolved.

## Benchmark interpretation

The frozen matched original benchmark is 100 prompts/model, of which 40 numeric questions are graded within absolute tolerance 0.01: original **36/40**, candidate **32/40**. All 60 conceptual responses/model remain unreviewed. On the same 15-question Zakat subset: simple calculator **15/15**, original **12/15**, candidate **11/15**. The calculator is deterministic, not fine-tuned AI. A separate exploratory 50-question/model set has 23 strict numeric-field probes: **5/23 → 9/23**, affected by formatting and truncation. It does not replace the original negative result or establish better advice, safety, or unseen training data.

## Scope and publication boundary

These tests use synthetic users and isolated local databases. Private outboxes, model secrets, database files, caches and `submissions/` stay untracked. A Git-history scan flagged four entries: three public SHA256 checksums of a benchmark reviewer identity mapping and one sentence describing token rotation. Those are inspected false positives, not credentials; scanner exit 1 is retained as such, not relabeled a zero-finding scan. No known real credential was identified in these findings.

The public browser result tests the deployment available at that time, not proof that later source fixes were deployed. Check the final deployment/commit receipts separately. Docker runtime, real bank/market integrations, SMTP delivery, real device assistive technology, GPU kernel hangs, independent scholarly approval, official submission and team eligibility were not verified by this record.
