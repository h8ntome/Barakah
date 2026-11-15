# Barakah release audit — 15 November 2026

**Overall competition readiness: NOT READY.** The code, truthful demonstration and write-up are deliverable, but the Finance challenge's requested advantage over a simple rule is not demonstrated, training/test independence cannot be established, and model advice has material failures. A working transport is not a trustworthy financial or religious adviser. Do not silently turn these into PASS or certify organizer eligibility.

**This project is a prototype and is not financial advice.**

## Current boundaries

- **Public demo:** <https://barakah-gamma.vercel.app/>. Real authenticated fictional-data financial workflows work; AI remains unavailable. This task did not reconfigure its hosting or make the private model public. Public smoke results apply to the deployment observed, not automatically to every later source commit.
- **Local opt-in AI:** actual browser → FastAPI → private authenticated loopback/SSH-tunneled service → pinned `h8notme/barakah1` → persisted conversation → browser was exercised. It requires a compatible operator-managed model runtime; it is not a hosted public AI endpoint or a bundled laptop model.
- **Default:** `AI_MODE=unavailable`, no provider call or saved failed send. Financial tools work independently.
- **Financial accounting:** Decimal; owner-scoped records; no bank sync, payments, brokerage execution, live price feed or Sharia certification. A model answer never updates a ledger or calculator result.
- **Submission package:** only the ignored root `submissions/` folder is the local handoff. Only its `UPLOAD_TO_DRIVE/` subfolder is intended for public sharing. No package contents are Git artifacts. No Drive upload, sharing change, email or form submission is implied by a Git push.

## Findings and repairs

| Priority / finding | Resolution and evidence |
|---|---|
| P1: shared-cookie account switch could replay another owner's private draft after refresh | Owner identity participates in the HTTP client's request generation. A different-owner refresh invalidates the old request. Three unit cases and a real two-tab regression verify no replay or persistence under B. |
| P1: new AI capability needed consent, minimization and atomic persistence rather than a fake reply | Pinned loopback service, bounded authenticated transport, no automatic financial context, saved consent, no automatic retries, and post-inference session/owner/history revalidation. SQLite/PostgreSQL regressions plus actual model/browser/busy/outage tests. |
| P2: provider HTTP 504 became generic 503 | Explicitly mapped to `ai_timeout`; regression includes provider 504. No failed response is persisted. |
| P2: expired AI authentication and account-switch boundary | Safe authenticated preflight can refresh the same owner; actual generation is sent once and never automatically replayed. |
| P2: saving zakat history did not refresh Home | Invalidate the dashboard after save; 32-check browser journey verifies the new outstanding amount without reload. |
| P2: demo preparation could hit an occupied/unowned port | Refuse port 8095 before build/migration and refuse an unverified running launcher. Three release-helper tests cover collision, configurable demo origin and preserving failed-check receipts. |
| P2: demo-tooling advisory | ESLint updated; scoped `minimatch:11.0.8` override resolves GHSA-g3hv-75wg-m249. npm audit is zero; source assertions, TypeScript and ESLint pass afterward. No wholesale dependency upgrade. |
| P2: misleading stale claims and artifacts | Current README/local-AI documentation, final PDF/film and this report distinguish default/public unavailable mode, real private inference and separate offline evaluation. Older reports retain explicit historical labels. |
| Unresolved: advice reliability | Correct initial $825 surplus, then contradictory interest-product advice and a wrongly dismissed $200 parental obligation. Broader probes also produce incorrect arithmetic and false generalizations about gold. Preserved, not filtered or relabeled correct. Public AI remains disabled. |

The independent AI integration review returned **OK with notes** and identified the 504 issue above. Its read-only verdict did not establish inference or test success; those were checked separately. All coding/review agents were AI tools, not independent qualified human advisers. [Additional consolidation review and scope probes](FINAL_CHECKS.md).

## Executed checks

[Machine-readable receipt summary](evidence/release-checks.json) records timestamps, exact test commands (private paths sanitized), precommit revision, before/after source-tree hashes, status and log hashes. Original logs and earlier failed attempts remain in the ignored local audit folder. The receipt runner used Python 3.15.1; **backend execution used Python 3.13.5**. Node 26.12.1/macOS arm64 and Chromium were used locally. Post-push CI and fresh-clone outcomes are recorded separately in the final handoff rather than inferred here.

| Check | Outcome | Scope |
|---|---|---|
| Fresh hash-locked Python installation | **PASS** | 37 packages installed from `backend/requirements.lock`; isolated venv |
| SQLite backend, locked environment | **PASS** | 162 tests; 1 explicitly PostgreSQL-only skip; one upstream TestClient deprecation warning |
| Disposable PostgreSQL backend, locked environment | **PASS** | 163 tests, including isolation/concurrency/migrations |
| Frontend tests / production build | **PASS** | 69 tests; Vite build completes |
| Real default-mode financial browser journey | **PASS** | 32 checks, including restart/login persistence, calculations, unavailable AI and mobile no-overflow |
| Real two-tab session switch | **PASS** | 3 checks; revoked A mutation attempted once; draft absent under B after reload |
| Real local AI browser journey | **PASS (integration only)** | 7 checks: consent, exact identity, follow-up history, conversation switching/reload, separate-owner isolation, logout |
| Real model boundary probes | **PASS (boundary only)** | 7 grouped checks: auth/input/context limits, busy concurrency, IDOR rejection, in-flight consent revocation, actual outage/no writes, explicit retry after restart |
| Public hosted browser journey | **PASS** | 21 checks; public AI truthfully unavailable; only synthetic QA records touched |
| Benchmark implementation | **PASS** | 77 tests; fresh independent rational arithmetic reproduces all 40 references and both original strict scores |
| Exploratory personal-finance integrity | **PASS** | 16 artifact checks in an isolated copy; 6 dataset/reference and 3 rubric tests; frozen originals untouched |
| Release utilities | **PASS** | 3 regressions |
| Dependency advisories | **PASS at scan time** | App npm, demo npm and all 37 installed locked Python packages: zero known advisories; not a security guarantee |
| Secret scanner | **Raw scan FAIL; triage PASS** | Current-tree four detections are one token-rotation prose sentence and three public SHA256 checksums of a review mapping, not credentials. No blanket suppression; raw findings retained. History also reviewed. |
| Final video | **PASS with stated QA limit** | 115.008-second container; 3,450 frames decode; source/type/lint checks, audio levels, local ASR and uninterrupted playback pass. Parent inspected final contact sheet/full frames. No subjective listening claimed. |
| Final one-page PDF | **PASS** | Required headings/disclaimer, selectable text, working link annotations and visual layout inspected; rebuilt against final release SHA during packaging |
| Docker runtime / external SMTP / physical assistive devices / hard GPU-hang cancellation | **NOT_RUN** | No claim of production verification |
| Real financial transfers, brokerage or live market feeds | **NOT_APPLICABLE** | Not implemented; no money moved |

Mocked HTTP/model tests prove protocol and failure handling, **not inference quality**. Live probes are separate development observations, not a new held-out score. A service metadata response is authenticated attestation; checkpoint inventory rehash and runtime inspection provide additional provenance, not cryptographic proof of a GPU execution.

## Model and evaluation identities

- Candidate full checkpoint: `h8notme/barakah1@912a5697cf9d85adf065ee512f509cfa236459d4`.
- Foundation comparator: `LiquidAI/LFM3-1.7B@1da06bec6a819da10b54c67e5c90972b46d81871`.
- Original dataset SHA256: `c8a9636cc9ad96cbfb1049168227a23e5fc213ce245264be44984667578801fb`.
- Personal-finance dataset SHA256: `4160cb05aa36e2c2f968634251befc9b527746e644ff6a118845db6dd32ff558`.
- Original matched runs: `original-matched_20261115T153923318073+0000` and `barakah-matched_20261115T154845353654+0000`.
- Fresh simple-rule run: `rules-release_20261115T164650954399+0000`; same 15-question numeric subset, no latency comparison across different machines.
- Live model runtime: PyTorch 2.12.0+rocm7.14.1 / Transformers 5.20.0 / AMD Radeon 8060S. Greedy, seed 2026, one beam, BF16/SDPA, eight CPU threads, repetition penalty 1.0, thinking disabled, 384-token cap. The application system prompt differs from the offline neutral benchmark prompt. [Exact setup](local-ai.md).

| Evaluation | Foundation / simple baseline | Candidate | Interpretation |
|---|---:|---:|---|
| Original strict numeric, 40 items | 36/40 (90%) foundation | 32/40 (80%) | Four regressions, zero improvements; 60 conceptual answers/model unreviewed |
| Same 15 zakat arithmetic items | 15/15 simple calculator | 11/15 | **FAIL: no advantage over the rule**; foundation was 12/15 |
| Exploratory personal finance, 23 strict numeric fields / 50 scenarios | 5/23 foundation | 9/23 | Format-sensitive increase, not reviewed advice quality; unparseable 18 vs 11, cap hits 27/50 vs 17/50 |

[Full original/exploratory report](../benchmark/rescue/REPORT.md) · [live response evidence](evidence/ai-live-final.json) · [broader adverse probes](evidence/ai-scope-smoke.json) · [pre-policy failure](evidence/ai-pre-policy-failure.json). An explicit no-interest instruction was added after an observed development failure and still failed; no safety improvement is claimed. Original references/raw answers and frozen evaluation policies were not altered to improve scores.

## Privacy, licensing and operational limits

No real financial context is sent automatically. Consent cannot recall already transmitted text; bounded history omits older turns. Timeouts/cancellation are cooperative, not hard GPU interruption. Busy returns an error instead of an unbounded queue. Response metadata is returned, not added as a new DB audit schema. Rate limits are per-process, not production distributed admission control. Use only fictional data for demonstration.

No weights, private tokens, database files, mail outboxes or runtime caches are bundled. The candidate card's Apache-2.0 label does not resolve the base LFM Open License v1.0. Exact checkpoint-linked training rows/hyperparameters are missing; lexical overlap screening does not prove independence. See [credits and rights](CREDITS.md). Do not invent human reviews, training details or license grants.

## Cleanup and history

A recoverable pre-release snapshot was taken outside the repository before edits. Initial staging was empty. Existing benchmark work and teammate commits were preserved; no reset, force-push or history rewriting. Old reports/media and adverse results remain available, with historical labels. Only the task-owned stopped disposable PostgreSQL cluster was removed during disk recovery; it was recreated for final tests. No user dataset, teammate service or weight cache was removed.

Generated movie exports/recordings/WAVs, QA frames, venvs, caches and runtime secrets remain ignored rather than swept into Git. Useful source, tests, source screenshots, comparison artifacts and credits are retained. No speculative deletion/refactor of legacy frontend mocks or unrelated benchmark code was needed. Final staging must be reviewed explicitly; `submissions/` must have zero tracked paths and the ignore rule must apply.

## Human submission gate

Deadline: **15 November 2026, 11:59 PM US Eastern = 16 November 2026, 9:59 AM Asia/Karachi**. The live form accepts a PDF/Word attachment; this release chooses **PDF attachment** as the single canonical write-up route. Current brief/site/form say video is optional/recommended (maximum two minutes), superseding the older guide's required-video wording. The example Drive folder is a reference, not an upload destination.

The submitter must verify identities/emails/schools, registration, contributions and the permitted build window/no pre-existing-project rule. Repository commits observed during the event do not prove all project work began then; the integrated checkpoint is an existing pretrained dependency, not newly trained by this release. Do not check the rules confirmation blindly. Final Drive/video links and anonymous access checks remain human steps because uploading, permission changes, email and submission were not authorized. See the ignored `submissions/START_HERE.md` for exact local files and remaining actions.
