# Personal Finance Domain Adaptation Benchmark v1.0 — results

## Bottom line

Both pinned models completed all **50 scenarios**, with no inference errors or missing responses. Under the frozen, strict **labeled numeric extraction** rule, the base passed **5/23** and barakah1 passed **9/23**. This is a narrow, formatting-sensitive result—not evidence that the candidate gives better financial advice, reasons better, or is safer. **No human quality scores or overall winner are reported.**

A required subjective-rubric dimension was initially omitted. A transparent late, prospective correction is recorded below. The original release and outputs were not changed or rerun.

## Actual results

| Measure | LiquidAI/LFM3-1.7B | h8notme/barakah1 |
|---|---:|---:|
| Responses / planned | 50 / 50 | 50 / 50 |
| Generation errors | 0 | 0 |
| Strict numeric passes / eligible | 5 / 23 (21.7%) | 9 / 23 (39.1%) |
| Parsed but incorrect numeric result | 0 | 3 |
| Unparseable final numeric fields | 18 | 11 |
| Responses reaching 384-token cap | 27 / 50 | 17 / 50 |
| Generated tokens, excluding warmup | 16,081 | 15,786 |
| Checkpoint loading seconds | 2.421 | 2.413 |
| Total run seconds | 405.783 | 398.607 |
| Subjective human scores | NULL | NULL |

Paired numeric outcomes: both correct **3**; base only **2**; candidate only **6**; neither **12**. All 23 eligible scenarios are retained in the denominator. The remaining 27 scenarios have no automated numeric score. There were no selective retries, permissive rescoring, excluded failed-format cases or outcome-selected subsets. The full run, not the predeclared 12-item fallback, was used.

Unparseable means the answer failed the exact final amount/unit contract; it does **not** establish incorrect arithmetic in the narrative. Likewise, a passing final number does not establish a correct, consistent or safe explanation. The high format-failure and token-cap rates materially limit interpretation. No statistical or causal generalization is claimed from this small authored set.

Source: `results/analysis/summary.json` and `numeric_records.json`; an independent implementation reproduces the 5 and 9 pass counts in `results/final_validation.json`.

## Freeze, execution and rubric deviation

| Event | UTC, 2026-11-15 |
|---|---|
| Original 50-question / rubric / rules / config freeze | 16:18:54.072817 |
| Actual base inference start | 16:19:04.224753 |
| Worker prospective rubric amendment | 16:22:26.257062 |
| Parent canonical rubric receipt, parent-reported no PF output/score inspection | 16:25:04 |
| Base complete | 16:25:50.019740 |
| Candidate start | 16:25:50.945488 |
| Canonical parent rubric adopted by worker | 16:27:14.696300 |
| Candidate complete | 16:32:29.564056 |
| Automated numeric analysis created | 16:32:30.469856 |
| Final integrity/parity validation and first worker numeric-result inspection | after 16:33:03 |

**Initial phase-3 deviation:** the original frozen human rubric used communication/empathy and omitted a separate reasoning/trade-offs dimension. Since inference had already begun, the original freeze was preserved. The supervisor's canonical prospective rubric supplies the exact required five: financial correctness; practical usefulness; personalization; reasoning and trade-offs; safety and uncertainty. It was adopted before worker inspection of generated answer text or numeric outcomes. It is **not** represented as part of the original pre-inference freeze. The earlier worker correction is superseded audit history, not an alternative active rubric.

Only `results/analysis/reviewer_packets_canonical/` is intended for future human review. Its 50 randomized A/B pairs contain **500 null dimension scores**, reviewer identity/qualification/timestamps unset, exact response hashes and scenario references. The identity mapping is separate at `results/analysis/private_mapping/identity_mapping.json`. The original unamended packets remain solely for audit and must not be scored. No explicit model-name strings were detected in canonical response text by the limited name scan; style can still weaken blinding.

### Key hashes

- Original freeze manifest: `9b1536cfdae0fadbb1bb68ba4d78f97f9a26d204e28a3c0e8370ca312955ddbb`
- Questions: `4160cb05aa36e2c2f968634251befc9b527746e644ff6a118845db6dd32ff558`
- Original rubric, preserved: `5b8149c32cdcf6810d03fc5d6d7b94a274032262802d7011a14a825b570327d8`
- Numeric rules: `1407edb941c88870bea0f572e9d62134ae0fcd18fa57d8ad9184d168a45360ff`
- Inference configuration: `b32293d1a895ca305b25bbab4f30b009238807e52c06db6e1d3633f2e83ad0e9`
- Canonical parent rubric: `27ab3aa1571a66d0b637355caf0284b999e0c6a836b32d41484c8f43d8ed5503`

The canonical rubric is a byte-identical, read-only copy of the supervisor-authored `benchmark/rescue/personal_finance_rubric_amendment.json`; its adoption receipt is in `amendments/canonical_adoption.json`.

## Comparison integrity and runtime

- Base revision: `1da06bec6a819da10b54c67e5c90972b46d81871`.
- Candidate revision: `912a5697cf9d85adf065ee512f509cfa236459d4`.
- Both exact full checkpoint manifests were verified against cached server2 files before loading. No retraining, weight modification or calculator/retrieval in inference occurred.
- Same server2 AMD Radeon 8060S Graphics, BF16, SDPA, seed 2026, greedy decoding, one beam, 384 new-token limit, identical system prompt and chat template. Both runs used Python 3.12.15, PyTorch 2.12.0+rocm7.14.1 and Transformers **5.20.0**. Full hardware/software inventories are in each metadata file.
- All 50 question IDs and execution order agree; every actual prompt hash agrees. Supplemental no-generation tokenization confirmed all 50 complete input-token sequences agree and match the recorded input lengths/hashes.
- **Metadata nuance:** the frozen runner's `effective_generation_config` field stores the declared pre-merge configuration, despite its name. Installed Transformers fills unspecified fields from checkpoint defaults. A no-generation audit invoked the installed merge and length-resolution methods: the only pre-length difference was max_length 20 versus 262144; explicit max_new_tokens=384 overrides it for both. All 50 resolved operative configurations agree. See `results/resolved_generation_compatibility.json`, including method-source hashes and complete merged configurations. No frozen code was repaired or inference repeated.
- The fixed base-first order, nonexclusive shared hardware and warn-only determinism enforcement remain reproducibility caveats; timing is descriptive, not a controlled speed comparison.

## Training overlap and remaining uncertainty

The plausible corpus `Azfarhashmi/adaption-personal-finance-advice-dialogues` was verified at public revision `3dd7f33149d6cbf4ab9115f76242851506929b9d`. Its existing local 354,098,432-byte JSONL matched public LFS SHA256 `95f46af8ee1b4981aaa85a94fcb0701e51c27b987c2e6be1936bfc21fd103446` and was read only, not copied.

All **27,981 rows** were screened. There were **zero number-masked exact scenario matches**, **zero trigram-containment flags at 0.55**, and maximum containment **0.2444**. The author inspected the ten highest-ranked excerpts and found generic subject overlap rather than obvious scenario reuse. This limited lexical/author review does not exclude semantic paraphrases or contamination.

**Actual barakah1 fine-tuning rows, split and training manifest remain unavailable.** Its public card establishes the base model but does not name this corpus. Neither the scoped read-only server check nor corpus screening proves training lineage or holdout independence. The scenarios/references were AI-authored, not independently expert-validated.

## Validation and deliverables

- Six original stdlib tests pass, including independent Decimal expressions for all 23 numeric references, exact category counts, rubric anchors and strict parsing edge cases.
- Three supplemental rubric/packet tests pass, including canonical dimensions, integrity, response hashes and null scores.
- All **16 final artifact checks** pass: freeze, revisions, IDs/order, metadata, prompt/input/config parity, response integrity, independent numeric counts, canonical packet pairing and separation.
- All original frozen files are unchanged. The copied original `benchmark/` tree is unchanged locally. No original-repository writes, commits, pushes or staged files were created by this task.
- Local: `/tmp/barakah-rescue-pf-20261115/personal_finance/`.
- Remote: `/home/hadi/barakah-pf-rescue-20261115/personal_finance/`.
- Managed unit: `barakah-pf-rescue-20261115.service`; it completed with exit status 0. Durable launch, per-model logs, exit statuses, metadata and raw answers are retained.

**Next step:** independent review of the artifacts and then actual blinded human scoring using only the canonical packets. Do not claim a general advice-quality improvement, safety certification, confirmed training independence, Islamic-finance superiority or product integration from this benchmark.
