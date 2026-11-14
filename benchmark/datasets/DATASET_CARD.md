# Barakah held-out evaluation dataset v1.0.0

## Identity and intended use

100 authored English scenarios for the original instruction-tuned LFM3-1.7B baseline and future adapted models. This is an exploratory Barakah-specific evaluation, not a financial certification, fiqh authority or standardized public leaderboard. No private financial records, people’s identities or real account details are included.

- Canonical JSON SHA256: `c8a9636cc9ad96cbfb1049168227a23e5fc213ce245264be44984667578801fb`.
- CSV SHA256: `7046f03765a9b35732c6aacdb2d2fd9eb790f55230e2372dda2eb3e998219c1e`.
- Difficulty counts: easy 28, medium 49, difficult 23. These are author judgments, not calibrated ability bands.
- Source retrieval date: 2026-11-14 UTC. Publication dates and retrieval dates are distinguished in the evidence file.

| Category | Total | Automatically checkable numeric | Conceptual, expert grading pending |
|---|---:|---:|---:|
| Zakat | 25 | 15 | 10 |
| Investing | 25 | 0 | 25 |
| Principles | 20 | 5 | 15 |
| Budgeting | 20 | 20 | 0 |
| Safety | 10 | 0 | 10 |
| Total | 100 | 40 | 60 |

## Construction and verification

The implementation author created the arithmetic scenarios. A delegated researcher authored 60 conceptual prompts and checked the reference answers against fetched institutional passages, recording exact excerpts, body hashes and item-to-source mappings. This was AI-assisted source research, **not independent qualified human review**. No human scholar is claimed to have validated the dataset or model responses.

Forty numeric expected results are generated with `decimal.Decimal`, rounded to two decimal places, then independently recalculated by dataset validation using separately implemented operations. Mathematical reference integrity is distinct from religious eligibility: zakat scenarios explicitly state that nisab, lunar holding period and eligibility/debt treatment are already satisfied/reviewed. The task is to apply the supplied 2.5% rate. The five principle calculations concern hypothetical realized distributable profit, not guaranteed returns or approval of a contract. Budgeting covers cash-flow arithmetic, savings rates, planned reserves and sinking funds; it does not exhaust the broader skill of giving budgeting guidance.

All arithmetic questions request a terminal `Final answer: <number> <unit>`, with explicit requested rounding. This enables conservative grading without selecting a coincidentally matching intermediate number. Repeated structures are disclosed; this is not 100 independent knowledge domains.

Conceptual answers are grounded in retrieved Islamic Relief Canada, National Zakat Foundation UK, Bank of England, Securities Commission Malaysia and US SEC Investor.gov material. `SOURCE_EVIDENCE.md` preserves reference passages, source dates, checksums and mappings. Additional arithmetic context references were independently fetched by the parent: Islamic Relief UK zakat, CFPB emergency-fund guide and IMF Islamic-finance overview. These support general principles, not the exact authored numerical examples.

Relevant parent-checked passages:

- Islamic Relief UK: https://www.islamic-relief.org.uk/giving/islamic-giving/zakat/ — “The donation should amount to 2.5% of your total Zakat eligible wealth.” The page also distinguishes nisab and a Hijri year. No embedded live threshold is used.
- CFPB: https://www.consumerfinance.gov/an-essential-guide-to-building-an-emergency-fund/ — “An emergency fund is a cash reserve that’s specifically set aside for unplanned expenses or financial emergencies.” The amount “depends on your situation.” Scenario reserve-month choices are hypothetical, not a universal prescription; the page is not used to certify insurance products or an Islamic banking account.
- IMF: https://www.imf.org/external/themes/islamicfinance/ — “the parties must share the risks and rewards of a business transaction”; Islamic-bank contract examples include “profit-sharing (Musharakah and Muḍarabah).” The 2017 overview is used for conceptual context only, not contemporary market statistics or detailed contract rulings.

Institutional summaries can simplify fiqh. Jewellery, children’s wealth, gold/silver nisab and share valuation methods are expressly attributed and qualified. A jurisdiction-specific securities list is not a universal certification. US investor-protection advice is financial-safety evidence, not a religious ruling. Conventional products mentioned by financial-literacy sources are not thereby recommended as Sharia-compliant.

## Schema

Every item contains `id`, `category`, `difficulty`, `question`, `reference_answer`, `key_facts`, `expected_behavior`, `source_references`, `answer_type`, `scoring_method`, `review_status`.

Numeric items add `expected_numeric`, `numeric_tolerance`, `unit` and `calculation` (operation plus Decimal-compatible operands). These fields are evaluation-side only: inference sends **question text alone**, not answers, key facts, operands or review status. The baseline likewise reads public question text and does not use expected values.

CSV serializes arrays and objects as JSON strings in cells; JSON is canonical for inference. `dataset_manifest.json` records release counts and checksums. `conceptual_questions.json` is the authored conceptual source; `scripts/build_dataset.py` is the release builder. Do not run it during evaluation.

## Review status and scoring eligibility

- `arithmetic_verified`: 40. Deterministic numeric reference values checked by code.
- `reference_checked_pending_expert`: 60. Reference passages checked, but independently qualified reference approval and response grading are still pending. These questions may be inferred for baseline collection, **not counted as verified conceptual correctness**.
- `reference_pending`: zero in the evaluated release. Unavailable unused research leads are documented separately and are not accepted references.

Any conceptual evaluation must inspect correctness, contradictions, completeness, unsupported religious claims, interpretive differences and uncertainty. Reviewer identity, timestamp and evidence are required. Refer to `reports/METHODOLOGY.md`. Automatic keyword counts or model-judge outputs are not religious ground truth.

## Held-out policy and versioning

**Do not train, fine-tune, retrieve answers from, or tune prompts on these questions or reference answers.** Keep adaptation data in a different directory/project and explicitly exclude this entire dataset. Training-data overlap checks must be performed before future adapted-model claims. Original-model pretraining overlap cannot be ruled out because its complete training corpus is unknown.

Any question/reference change requires a new dataset version, checksums and fresh comparable runs; never silently rescore old answers against new references. Freeze the final private test before future model development; public publication increases leakage risk. Source websites can change, so retain the evidence passages and dates rather than treating later page content as the historical source.

## Known exclusions

No live nisab conversion, stock price, actual investment certification, individual fatwa, personalized portfolio prescription, Arabic benchmark, tool-use evaluation, production user data or complete school-by-school legal analysis. General personal-finance arithmetic does not establish Islamic-finance expertise. Expert review and a broader independently designed holdout remain required.
