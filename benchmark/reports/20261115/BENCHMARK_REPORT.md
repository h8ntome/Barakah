# Barakah AI matched benchmark report

Evaluation date: 2026-11-15 UTC. All values below derive from immutable saved model responses.

## Executive summary

**The fine-tuned checkpoint regressed on the measured numerical score: 36/40 (90.0%) → 32/40 (80.0%).**
Absolute change: **-10.0 percentage points**; relative accuracy change: **-11.11%**.
This does not establish improved conceptual Islamic-finance quality; those answers are unreviewed, and training overlap and the exact training base revision are unresolved.

Both actual models completed 100 question attempts each. No rule engine, external API,
calculator, retrieval system or simulated response was substituted. Historical reports,
charts and original/rules runs are preserved separately.

## Models and provenance

| | Original | Barakah |
|---|---|---|
| Repository | LiquidAI/LFM3-1.7B | h8notme/barakah1 |
| Immutable revision | 1da06bec6a819da10b54c67e5c90972b46d81871 | 912a5697cf9d85adf065ee512f509cfa236459d4 |
| Run ID | original-matched_20261115T153923318073+0000 | barakah-matched_20261115T154845353654+0000 |
| Format | Full BF16 checkpoint | Full BF16 checkpoint, not a PEFT adapter |

See MODEL_PROVENANCE.md for file hashes, snapshot locations, licenses and unknown training details.

## Dataset, hardware and settings

Dataset v1.0.0, SHA-256 `c8a9636cc9ad96cbfb1049168227a23e5fc213ce245264be44984667578801fb`. 100 English questions: zakat 25,
investing 25, principles 20, budgeting 20, safety 10. Forty numerical and sixty conceptual.
No question/reference changes. Full DATASET_CARD.md and SOURCE_EVIDENCE.md remain authoritative.

Server2: AMD Ryzen AI MAX+ 395, Radeon 8060S integrated GPU, approximately 123 GiB usable
system RAM. Same ROCm PyTorch, BF16, Transformers, SDPA and tokenizer input IDs.
Neutral system prompt, greedy decoding, 384-token cap, seed 2026, 8 CPU threads,
identical 24-token-capped warm-up. No unrelated workloads stopped.
See METHODOLOGY.md for the exact prompt, timing protocol and shared-host caveats.

## Correctness and response coverage

| Metric | Original | Barakah |
|---|---:|---:|
| Verified numerical accuracy | 36/40 (90.0%) | 32/40 (80.0%) |
| Numerically incorrect | 4 | 8 |
| Numerically unparseable | 0 | 0 |
| Numerical generation errors | 0 | 0 |
| Missing questions | 0 | 0 |
| Successful generations | 100/100 | 100/100 |
| All generation failures | 0/100 | 0/100 |
| Responses reaching token cap | 2/100 | 13/100 |
| Conceptual review | Unavailable; 60 pending | Unavailable; 60 pending |
| Verified hallucination / unsafe rates | Unavailable; no adjudication | Unavailable; no adjudication |

### By category

| Group | Original numeric | Barakah numeric | Conceptual pending per model |
|---|---:|---:|---:|
| zakat | 12/15 (80.0%) | 11/15 (73.3%) | 10 |
| investing | Unavailable: no numerical tasks | Unavailable: no numerical tasks | 25 |
| principles | 4/5 (80.0%) | 4/5 (80.0%) | 15 |
| budgeting | 20/20 (100.0%) | 17/20 (85.0%) | 0 |
| safety | Unavailable: no numerical tasks | Unavailable: no numerical tasks | 10 |
### By difficulty

| Group | Original numeric | Barakah numeric | Conceptual pending per model |
|---|---:|---:|---:|
| easy | 10/10 (100.0%) | 10/10 (100.0%) | 18 |
| medium | 15/17 (88.2%) | 13/17 (76.5%) | 32 |
| difficult | 11/13 (84.6%) | 9/13 (69.2%) | 10 |

## Paired improvements, regressions and uncertainty

- Baseline incorrect → Barakah correct: **0**.
- Baseline correct → Barakah incorrect: **4**.
- Both correct: **32**.
- Both not correct: **4** (includes strict-format failures).
- Conceptual outcomes not conclusively graded: **60**.
- Exact two-sided McNemar p-value: **0.125000**.
- Paired bootstrap 95% accuracy-change interval: **[-20.0, -2.5] percentage points**.

These are exploratory results on a small, nonrandom, repetitive task set. McNemar
is the primary paired significance check. A percentile bootstrap interval can exclude
zero with sparse discordant outcomes even when the exact test is not significant;
do not use the bootstrap interval to overrule the exact test. A p-value
is not proof of broad financial or religious competence. Unknown training overlap
prevents a clean held-out generalization claim. No combined correctness is published.

## Performance and resources

| Metric | Original | Barakah |
|---|---:|---:|
| Mean latency (s) | 4.786 | 4.520 |
| Median latency (s) | 5.134 | 4.242 |
| P95 latency (s) | 9.058 | 9.401 |
| Output tokens/s | 40.948 | 40.912 |
| Total output tokens | 19,599 | 18,490 |
| Model loading (s) | 2.445 | 2.406 |
| Peak GPU allocated (GiB) | 3.305 | 3.305 |
| Peak sampled process RSS (GiB) | 1.485 | 1.483 |
| Parameter count | 1,728,801,536 | 1,728,801,536 |

Mean latency change: -0.267 seconds (-5.57%); lower is better.
Throughput change: -0.036 output tokens/s (-0.09%); higher is better.
Paired mean latency-change bootstrap interval: [-0.6207564223199733, 0.09043374952001614] seconds.
These are same-host single-session observations, **not** randomized isolated speed trials.
Response length affects total latency; throughput includes prefill. See workload logs
and the discussion of shared integrated-GPU memory in METHODOLOGY.md.

## Question-level error analysis and demo examples

All 100 paired answers, statuses, exact prompts, token counts and errors are available
in `results/comparisons/20261115/questions.csv` and comparison.json, and in the dashboard.
Examples below use the first improvement, first regression, then first shared error or
success in frozen question order (up to three). They are not cherry-picked best answers.
No conceptual illustration is presented as verified correctness.

### BUDGET_006 — regressed

Monthly income is USD 4250; rent USD 1400, food USD 480, transport USD 210 and other spending USD 760. What remains? Round to two decimal places and end with 'Final answer: <number> USD'.

**Original (correct):**

> Monthly income: 4250 USD
> 
> Total expenses:
> - Rent: 1400
> - Food: 480
> - Transport: 210
> - Other spending: 760
> 
> Total expenses = 1400 + 480 + 210 + 760 = 2850
> 
> Remaining = 4250 - 2850 = 1400
> 
> Final answer: 1400.00 USD

**Barakah (incorrect):**

> Monthly income: USD 4250
> Total expenses: USD 1400 (rent) + USD 480 (food) + USD 210 (transport) + USD 760 (other) = USD 2940
> Remaining: USD 4250 - USD 2940 = USD 1310
> 
> Final answer: 1310.00 USD

### PRINCIPLE_020 — both incorrect

In a hypothetical profit-sharing exercise, realized distributable profit is USD 12347.80. The agreed investor share of this actual profit is 37.5%. Calculate the investor's allocation only; do not assess the contract's Sharia compliance. Round to two decimal places and end with 'Final answer: <number> USD'.

**Original (incorrect):**

> Investor's share = 12347.80 × 37.5%
> 
> Calculation:
> 12347.80 × 0.375 = ?
> 
> 12347.80 × 0.375
> = 12347.80 × (3/8)
> = (12347.80 × 3) / 8
> = 37043.40 / 8
> = 4630.925
> 
> Rounded to two decimal places: 4630.93
> 
> Final answer: 4630.93 USD

**Barakah (incorrect):**

> Investor's allocation = 12347.80 × 0.375 = 4632.675
> 
> Rounded to two decimal places: 4632.68 USD
> 
> Final answer: 4632.68 USD

### BUDGET_001 — both correct

Monthly income is USD 3000 and total monthly spending is USD 2400. How much remains? Round to two decimal places and end with 'Final answer: <number> USD'.

**Original (correct):**

> Income: 3000 USD
> Spending: 2400 USD
> Remaining = 3000 - 2400 = 600 USD
> 
> Final answer: 600.00 USD

**Barakah (correct):**

> Monthly income: USD 3000
> Monthly spending: USD 2400
> Remaining: 3000 - 2400 = 600
> 
> Final answer: 600.00 USD

## Limitations and conclusion

The fine-tuned checkpoint regressed on the measured numerical score. This does not establish improved conceptual Islamic-finance quality; those answers are unreviewed, and training overlap and the exact training base revision are unresolved.
Read LIMITATIONS.md and LEAKAGE_CHECK.md before presenting this result. A broader,
independently authored private holdout and qualified blinded review are the next
credible steps—not a stronger marketing claim from these same 40 calculations.
