# Presentation asset provenance

These are **real app screenshots**, not mockups or generated UI. Captured on 2026-11-15 UTC from `http://127.0.0.1:8097`, serving the new uncommitted integration source. They are **not screenshots of the older public deployment**. The app's local date display may differ from UTC.

## Screenshots

| Asset | Session and inputs | Capture / transformation |
|---|---|---|
| [demo-overview.png](demo-overview.png) | Fresh isolated `barakah-presentation-20261115-fresh`; **Try Demo**, untouched fictional seed data | 1440 × 1000 viewport; native screenshot, no edits |
| [demo-zakat.png](demo-zakat.png) | Same synthetic demo, **Zakat** | 390 × 844 viewport; native screenshot, no edits |
| [ai-model-settings.png](ai-model-settings.png) | Separate fresh `barakah-presentation-personal-20261115-fresh`; fictional personal registration, Settings → AI Model → My API provider | 1280 × 1500 viewport; native `.ai-settings` screenshot, cropped to `(0, 0, 358, 610)` |

The settings crop excludes account identity and the element's offscreen portion. Model and API-key fields are empty; selection was **not saved**, consent was not enabled, and no connection test or provider call occurred. The active mode is correctly shown as Off. No screenshot contains an email, genuine key or real financial data. No text, totals, status or UI controls were composited or replaced. The existing browser-v3 image was inspected but **not reused**. All task-owned browser sessions were closed; no user/supervisor browser was attached.

[Machine-readable screenshot provenance](screenshots.provenance.json) records output SHA-256 hashes, viewport sizes, workflows, the pre-crop image hash and selected integration-source hashes. Source hashes were recorded after capture; they are context, not a reproducible-build attestation. The private raw element capture is not published because it adds no useful presentation evidence. Registration credentials and session state are not retained in these assets.

Reproduce using a **new named agent-browser session** on the integrated local app: open the app, set the recorded viewport, choose Try Demo and capture Home/Zakat. For the settings image use a separate fictional personal account on an operator-enabled installation; select My API provider without entering a key or saving/testing, screenshot `.ai-settings`, then apply the documented crop. Dynamic dates or synthetic workspace identifiers may change; do not expect byte-identical rerenders.

## Existing film thumbnail

[demo-film-thumbnail.png](demo-film-thumbnail.png) is a byte-identical copy of the previously verified film's `demo-video/output/thumbnail.png`, SHA-256 `17a55cd35d10a2a80020093bfb2a4b31b07478e7bd5ccd16f7d93022846ad593`. It is the authored film thumbnail incorporating real synthetic-data screenshots, not a single app screenshot or evidence of the new provider feature. It links to the supervisor-verified existing Drive video ID; no new upload or replacement is implied. The original file and public package remain untouched.

## Benchmark chart

[benchmark-calculations.svg](benchmark-calculations.svg) is a **new evidence chart**, not a UI screenshot. Historical charts and evaluation artifacts are untouched. [Source hashes and matched question IDs](benchmark-calculations.provenance.json) identify the preserved processed runs, raw JSONL/metadata, dataset, scoring implementation and candidate checkpoint manifest.

Reproduction/validation uses only saved results, **no inference**:

1. Read the processed `rules-release_20261115T164650954399+0000`, `original-matched_20261115T153923318073+0000` and `barakah-matched_20261115T154845353654+0000` JSON files.
2. Select `scores` rows with `category == "zakat"` and `numeric_task == true`; assert that all three sets contain the same 15 `question_id` values. Count `automatic_correctness == true`: **15, 12, 11**.
3. Verify each raw JSONL SHA-256 against its processed `raw_sha256`. Read `summary.automatic_numeric_correctness` for the two model runs: **36/40** and **32/40**. Check `pending_correctness_review == 60` for each and dataset numeric tolerance **0.01**.
4. Draw each zakat bar from a common zero baseline, with width `540 × correct / 15` in the 960 × 620 SVG. Include the full numeric results and unreviewed-response caveat, not only the favorable rules subset.

The rules result covers only these 15 calculations, not all 100 questions. It is not a fine-tuning, safety or religious-certification score. The historical comparison's mislabeled `candidate_config` is **not** used to identify the candidate or generate this chart. The integrated [provenance correction](../BENCHMARK_PROVENANCE_CORRECTION.md) and [corrected comparison v2](../evidence/benchmark-comparison-v2.json) preserve the historical artifacts while separating effective identity from template defaults.

## Inspection and limits

All three final PNGs were visually inspected. The SVG was opened in a separate fresh browser at 960 × 620, screenshotted and visually inspected for legible labels and uncropped results. No video was produced. Screenshots demonstrate interface state, not successful external inference, security certification or advice quality. The separately observed pinned-model arithmetic/follow-up/reload workflow is not depicted as a provider test or a benchmark improvement.
