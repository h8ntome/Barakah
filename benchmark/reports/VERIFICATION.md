# Execution and verification record

## Actual execution

- Original run: `original_20261114T184206126429+0000`, server2, completed 2026-11-14T19:03:48.013272+00:00.
- Official instruction-tuned `LiquidAI/LFM3-1.7B`, revision `1da06bec6a819da10b54c67e5c90972b46d81871`.
- BF16 safetensors SHA256 matches the official pinned Hugging Face LFS object: `135922caef64e81e52af88ede8b7c3ddaa9d6da220a9737fb3065275dbfb4330`.
- Existing official cache reused; successful model/tokenizer load and real GPU smoke inference preceded the full run. No substitute or local redundant checkpoint copy.
- All 100 frozen questions attempted, 100 responses retained, zero generation exceptions. Forty numeric tasks scored: 36 correct, four incorrect, zero unparseable. Sixty conceptual grades await qualified review. Two responses reached the configured token cap.
- Rules run: `rules_20261114T184236288070+0000`, local Mac, 15 matched zakat tasks; 15 correct. No model-token throughput is claimed for this formula baseline.

## Synchronization and result integrity

Remote validation generated a SHA256 manifest covering **16 raw, processed and hardware evidence files**, verified after transfer. Model weights were not transferred. `validate_benchmark.py` checks canonical JSON/CSV hashes, schema, unique IDs, independently recalculated arithmetic, run dataset fingerprints, hardware metadata and processed-to-raw/metadata hashes. Interrupted-tail recovery does not remove valid interior records. Stale processed files and scoring-time mutations are rejected.

Both server2 validation and local post-transfer validation passed. The manifest intentionally covers remote artifacts; local baseline, local analysis versions, plots/reports and test logs are additional local outputs, not misrepresented as remotely generated files.

## Automated tests

Command from the final analysis snapshot:

```sh
python -m pytest benchmark/tests -q -o cache_dir=/tmp/barakah-test-cache
```

**44 passed, zero skipped**, including real-run visualization integration, schema/counts/missing references, duplicate IDs, numerical tolerance/units, generation-error denominators, empty results, missing candidate model, human review provenance and exact-response binding, local checkpoint mutations, resume environment changes, interrupted JSONL recovery, raw/metadata scoring races, stale scores, hardware fields and transfer tampering. See `results/tests.log` for the actual captured output. Synthetic unit fixtures are never used to generate published figures or scores.

The Python modules compiled successfully. Full server2 package versions and local analysis package versions are saved separately. The existing server2 Python environment was consumed read-only, not modified.

## Fresh-context code review

A separate review agent inspected the connected runner, grader, baseline, comparisons, plotting, validation and tests. Its concrete findings led to normalized currency/percentage/time units; null rather than invented baseline token measurements; stricter resolved resume-environment checks and per-segment provenance; complete local checkpoint hashing; reviews bound to run/dataset/response; processed artifacts bound to exact raw/metadata inputs with mutation detection; and unavailable-safe, metadata-driven figures.

The final regression suite exercises those corrections. No external professional code audit, human scholarly validation or religious correctness certification is claimed. The exact initially executed runner is archived as `results/hardware/evaluated_run_benchmark.py`; the published runner adds recovery/provenance safeguards without changing the measured generation protocol.

## Rendered dashboard checks

The completed offline dashboard was opened with a dedicated ephemeral Chromium session through `agent-browser`:

- Desktop **1440 × 1000**: 100 response entries, all chart images loaded, no horizontal overflow, no reported page errors.
- Mobile **320 × 780**: no horizontal overflow; screenshot visually reviewed.
- Earlier **390 × 844** responsive rendering was also inspected while the genuine run was partial; no mock scores were used.
- Category filter changed from 100 responses to **25 zakat responses**. The intermediate budgeting filter showed the expected **20** entries.
- Screenshots were actually opened and visually inspected. They remain temporary verification artifacts, not necessary committed deliverables.
- Mechanical Impeccable design detector returned `[]` (no findings), saved as `results/dashboard_design_check.json`.
- Browser sessions were closed; no app backend or external hosted scripts/fonts were used.

## What remains unverified

Independent qualified expert approval of all conceptual references and grading of 60 conceptual answers; independent safety/hallucination review of all 100 responses; repeated-run stability and a comparable local LLM speed measurement; future adapted-checkpoint performance. The published null/pending fields must not be read as zero failure rates or a claim of religious authority.
