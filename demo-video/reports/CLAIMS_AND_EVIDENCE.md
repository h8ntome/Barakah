# Claims and evidence

Every substantive claim is bounded to this checkout, isolated synthetic demo, or explicitly historical benchmark. No video claim relies only on a training script, mock adapter, or proposed feature.

| Film claim / visual | Supporting evidence | Boundary |
|---|---|---|
| Barakah is an Islamic personal-finance prototype | `PRODUCT.md`; actual five destinations in `barakah-ui/src/App.jsx`; browser captures | Not production-ready, not financial advice |
| Amina is a fictional demo user | `backend/app/demo.py`, `scripts/capture-demo.py`, profile persistence assertion | Existing Try Demo owner; display name changed through real Settings |
| Real authenticated account | `assets/recordings/login.mp4`; actual `/api/v1/demo` request in `reports/browser-network.txt` | Passwordless synthetic demo auth, not fabricated session storage |
| $4,500 income, $2,850 expenses, $1,650 surplus | `backend/app/demo.py`; `assets/recordings/dashboard.mp4`; `dashboard-ui.txt` | November 2026 fictional transactions, USD |
| Date filter and category breakdown work | `dashboard.mp4`, `spending.mp4`, capture assertions on $4,200 prior-month income and restored $1,650 current surplus | Changing input triggers genuine API state updates |
| Account balances and profile persist | End-of-capture reload assertions; `capture-log.json` | Tested refresh persistence in isolated SQLite; not a claim of cloud or bank sync |
| $375 illustrative zakat | `backend/app/calculations.py`, actual form submission and saved snapshot in `zakat.mp4` / `zakat-saved.png` | $15,000 declared eligible wealth, 2.5%, fictional manual $5,000 nisab, haul attested; not all dashboard assets |
| Zakat calculation is not AI | `backend/app/calculations.py`; no model inference in route | Deterministic arithmetic only |
| Giving total $125 | `giving-history-ui.txt`, `giving.mp4`; two seed records $50 and $75 | Recorded giving elsewhere; no transfer and no audited charity discovery |
| Portfolio $8,500; allocation 58.82/29.41/11.76% | `backend/app/demo.py`; `holdings.png`, `portfolio.mp4`; arithmetic 5000/8500,2500/8500,1000/8500 | Fictional dated manual valuations. Rounded percentages total 99.99%; graphic uses proportional widths, no return claim |
| Portfolio screening is unverified | Actual holding labels, seed without screening assessments, `portfolio.py` | No universal halal label, no current market/compliance approval |
| Private local AI connected through the app | `assets/recordings/ai-live.mp4` (177 frames, 5.9 seconds); actual screenshot `ai-live.png`; `ai-live-evidence.json` | Genuine supplied browser click → backend → model → rendered response; private local service, not hosted; public AI remains unavailable per release handoff |
| Pinned live model identity | Response metadata: `h8notme/barakah1`, revision `912a5697cf9d85adf065ee512f509cfa236459d4` | Service-attested metadata, not independent weight attestation; do not infer benchmark/application prompt equivalence |
| $825 surplus correct; high-yield savings recommendation contradicts no-interest instructions | Exact first response in `ai-live-evidence.json`, displayed through unaltered actual screenshot | Adverse result, not safe advice; disclaimers do not repair the recommendation |
| Follow-up wrongly dismisses $200 parental transfer | Exact first sentence of second response in `ai-live-evidence.json`; 3100 − 2275 − 200 = 625 | Exact excerpt labeled follow-up; not a fabricated continuation of footage; remaining raw response retained, including repeated high-yield savings advice |
| Current original numeric 36/40 vs candidate 32/40 | `benchmark/results/comparisons/20261115/comparison.json`; run IDs and SHA256 in `release-comparisons.json` | Same 40 numeric questions, single run; no general superiority |
| Simple rules 15/15 vs candidate 11/15 | `benchmark/results/comparisons/rules-release_20261115T164650954399+0000__barakah-matched_20261115T154845353654+0000.json` | Same 15-task zakat subset and candidate run, not mixed denominators; rules win |
| Benchmark prompt differs from application prompt | Comparison `candidate_config.system_prompt` is neutral; live evidence records application prompt/template hashes | Numeric scores are not verified deployed-advice or safety accuracy |
| Dataset 100 across five categories | `benchmark/datasets/benchmark_questions.json`, manifest/hash checks in repository evidence and `verify-evidence.py` | Authored test set; unknown model pretraining overlap, not proven unseen training data |
| 40 arithmetic / 60 conceptual awaiting expert review | `review_status` counts; dataset card; no expert-reviewed items | No expert-validation or verified safety/hallucination-rate claim |

## Rejected claims

No model superiority, improved advice/safety, verified conceptual accuracy, on-device/browser inference, public AI availability, live stock prices, guaranteed safety, certified halal holdings, financial/religious advice or production readiness. The connected local service is shown honestly alongside its current failures. No response or inference wait time is invented.

## Timeline and evidence scope

- 00:00–01:05: existing visual design and other real app captures preserved.
- 01:05–01:10.9: all 177 original frames of the live capture at normal speed, under the existing scene dissolve. No acceleration or invented latency.
- 01:10.9–01:17: actual screenshot reading hold; 01:17–01:31: enlarged actual response plus exact follow-up excerpt and corrected available surplus.
- 01:31–01:47: both current matched numeric comparisons and conceptual-review/prompt caveats.
- 01:47–01:55: local connected / advice unverified / public unavailable.

Historical unavailable-AI captures and reports are retained for provenance, not current-runtime claims. No official requirements were researched again; release packaging/eligibility remains the parent's responsibility.
