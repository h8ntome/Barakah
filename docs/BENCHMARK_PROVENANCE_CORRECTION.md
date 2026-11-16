# Benchmark identity correction — additive export

The historical comparison's `candidate_config.model` and `.revision` contain the **baseline template defaults**, not the effective candidate identity. The runner saved `config.yaml` as `metadata.config` without incorporating the CLI model/revision overrides; the comparison exporter copied that field. This was a provenance-labeling defect, not a newly measured result.

**No inference was rerun. No historical raw response, metadata, processed score, comparison JSON, frozen dataset, or submission artifact was rewritten.**

## Effective recorded identities

| Run | Model | Immutable revision |
|---|---|---|
| Original matched run | `LiquidAI/LFM3-1.7B` | `1da06bec6a819da10b54c67e5c90972b46d81871` |
| Candidate matched run | `h8notme/barakah1` | `912a5697cf9d85adf065ee512f509cfa236459d4` |

These identities agree across the matched runs' raw rows, metadata fingerprints and checkpoint manifests. This agreement is artifact provenance, not independent proof of training lineage or a new inference execution.

- [New identity-v2 comparison export](evidence/benchmark-comparison-v2.json): separates `*_template_config` from `*_effective_run_settings`, records supporting identity fields and input/exporter hashes, and explicitly flags the candidate's differing template identity.
- [Unmodified historical comparison](../benchmark/results/comparisons/20261115/comparison.json): retain it as evidence, but do not interpret its legacy `*_config` fields as effective model identity.
- [Original artifact/weight provenance](../benchmark/reports/20261115/MODEL_PROVENANCE.md): preserved historical report; includes separate checkpoint hashes. Its former training-lineage uncertainty is superseded by the [verified training provenance correction](TRAINING_PROVENANCE_CORRECTION.md); licensing and held-out independence remain unresolved.

The exporter rejects contradictory identities. Older raw records that omit a revision are explicitly marked `raw_rows_partial`; absence is not silently treated as raw-row verification. A missing fingerprint is never filled from template defaults.

## Results remain unchanged

| Comparison scope | Calculation engine | Original LFM3 | Barakah candidate |
|---|---:|---:|---:|
| Same 15 Zakat numerical tasks | **15/15** | **12/15** | **11/15** |
| Full 40 numerical tasks | Not evaluated outside its Zakat scope | **36/40** | **32/40** |

The rules column comes from the preserved [rules-release processed run](../benchmark/results/processed/rules-release_20261115T164650954399+0000.json), paired on the same 15 question IDs. Numeric grading uses an absolute tolerance of **0.01**. The other **60 conceptual responses per model remain unreviewed**; unavailable human correctness/safety/hallucination scores are not zero errors or a passing grade. The rules result is evidence for a scoped calculation engine, **not fine-tuning superiority**. The Finance improvement objective was not demonstrated. That limitation alone does not establish ineligibility; the [FAQ in the official 22-page guide](https://drive.google.com/file/d/15tYD48XRmCgWbk1_lLDtc8lebi6qm-4-/view) does not impose a minimum accuracy threshold.

The separate [50-scenario exploratory study](../personal_finance/README.md) does not replace the original matched comparison or establish improved advice quality. Training/test independence remains unverified.

## Reproduce without overwriting evidence

From a benchmark environment with its analysis dependencies installed:

```sh
python benchmark/scripts/compare_models.py \
  --baseline original-matched_20261115T153923318073+0000 \
  --candidate barakah-matched_20261115T154845353654+0000 \
  --output /tmp/barakah-comparison-identity-v2.json
python -m pytest benchmark/tests/test_run_provenance.py -q
```

The output path must not already exist. This reads existing scores and provenance only; it does not load a model. New future inference metadata additionally records `effective_config` separately from the unchanged template `config`, including CLI-resolved model/revision and actual device/precision. Existing runner hashes continue to describe the historical runner, not this updated source.

**This project is a prototype and is not financial advice.** Islamic-finance answers are educational, not religious certification.
