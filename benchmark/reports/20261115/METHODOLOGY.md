# Matched-model methodology — 2026-11-15

## Frozen evaluation
Dataset v1.0.0: 100 English questions, canonical file SHA-256
`c8a9636cc9ad96cbfb1049168227a23e5fc213ce245264be44984667578801fb`.
Questions and references were not edited. There are 40 deterministic numerical tasks
(20 budgeting, 15 zakat, 5 principles) and 60 conceptual tasks (25 investing,
15 principles, 10 zakat, 10 safety). Author-assigned difficulty: 28 easy, 49 medium,
23 difficult across the full dataset. Numeric difficulty denominators are reported separately.

The historical 2026-11-14 baseline has 100 unique intact records, matching dataset and
revision, and valid raw/metadata score hashes. It scored 36/40. It is preserved but
**not used for primary timing comparisons**. The historical 15-question rules run
is neither a language model nor the Barakah candidate and is excluded entirely.

## Inputs and inference
Both models receive only this system prompt and the frozen public question:
> You are a helpful assistant. Answer accurately and clearly. State uncertainty and ask for missing information when needed. Do not invent sources.

No references, expected values, rubrics, key facts, calculators, retrieval or hidden
instructions enter inference. The existing question order is retained, batch size 1.
A tokenizer renders system/user messages with add_generation_prompt=true,
enable_thinking=false; the resulting string is tokenized with add_special_tokens=false.

Both use max_new_tokens=384, do_sample=false, repetition_penalty=1.0, use_cache=true,
seed=2026, BF16, SDPA and 8 CPU threads. One identical warm-up question,
"What is 2 + 2? Answer briefly.", is capped at 24 tokens before each run.
Smoke runs are separate, are not scored and contain no benchmark questions.
Every full-run answer is retained, including errors and truncations; no best-of selection.

The full model snapshots use AutoModelForCausalLM and their own AutoTokenizer with
pinned, locally hashed custom code. Their three modeling source files and chat
templates are byte-identical. Tokenizer serialization differs, but **all 100 rendered
public prompts and input token-ID sequences are identical**, verified by
`results/hardware/checkpoint_compatibility.json`.
The stored generation_config differs in its Transformers version and a candidate
max_length setting; explicit max_new_tokens=384 takes precedence. Both run metadata
files retain the inherited configuration. No compatibility-adjusted run was needed.

## Numerical evaluation
The existing terminal-answer grader is unchanged. Only an unambiguous terminal
"Final answer: <number> <unit>" is accepted. Decimal tolerance is 0.01; matching
currency, percent or months units are required. Incorrect units are incorrect;
missing units or ambiguous/missing format is unparseable. Coincidental intermediate
numbers are never evidence of correctness. Surrounding prose is not certified.

Accuracy uses all 40 attempted numerical tasks, including unparseable answers and
generation failures. Report missing responses and failures separately. No overall
100-question accuracy combines unreviewed conceptual answers with these scores.

## Human review
The references have institutional source checking, not qualified expert approval.
See HUMAN_REVIEW.md for independent, response-hash-bound review. Correctness,
hallucination and safety are distinct channels with distinct reviewed denominators.
No model judge or heuristic flag is treated as verified judgment. Missing metrics
are null/unavailable, never zero.

## Performance protocol and limits
Both full runs execute sequentially on server2's Radeon 8060S, same working ROCm
PyTorch/Transformers installation, BF16 and SDPA. No unrelated process was killed or
reconfigured. The host also runs ComfyUI and Unsloth services. Workload snapshots and
partial 10-second telemetry are retained; monitoring started during the baseline,
not before its first question. This is a matched-environment **single-session
observational comparison**, not an isolated, randomized, repeated performance trial.

Timing starts after tokenization and a device sync, ends after synchronized generation,
and includes prefill and decoding. Output counts include generated special/end tokens;
decoded text omits them. Aggregate throughput is total output tokens divided by summed
successful generation time, not the mean of per-answer rates and not pure decode speed.
Mean/median/P95 use successful responses; P95 is nearest rank.
Response length, prefix length, thermals, power policy, compilation and shared activity
can affect timing. No cross-hardware speedup or production serving latency is claimed.

Loading time covers tokenizer/model deserialization and transfer to GPU, not prior
checksum verification or warm-up. Peak GPU allocation is PyTorch process memory
after warm-up, not driver-wide memory. Process RSS is sampled after answers, not a
continuous system maximum. The integrated GPU shares physical RAM; do not add GPU
and RSS measurements as if they were independent physical memory pools.

## Reproducibility and integrity
Python and PyTorch seeds are set; deterministic algorithms are requested with
warn_only=true. Cross-version/device bitwise determinism is not guaranteed.
Each answer is fsync-written to JSONL. Exclusive locks reject concurrent writers;
resume checks dataset/config/model/revision/checkpoint inventory/runtime/template and
runner hash, rejects duplicate IDs and never replaces prior failures. Only a torn final
JSONL line can be repaired. Completion requires exactly the full question-ID set.
Raw outputs, metadata, source snapshots and file manifests are retained.
The exact evaluated runner is archived in results/hardware/matched_run_benchmark.py.
After both runs completed, the published runner gained additional per-record response
hashes and recovery-identity checks; those safeguards were unit-tested, not retroactively
inserted into raw outputs. Both full runs used the same archived inference source.
Resume a published run only with its original archived runner, not a changed source file.
The final scorer adds null-safe truncation counting and its own source hash; the terminal
numeric grading logic is unchanged and both final score files use the identical scorer hash.
Do not run build_dataset.py or edit the frozen config for this comparison.

## Statistics and attribution
Per-model numerical intervals use Wilson 95% intervals. Paired accuracy change uses
20,000 paired question bootstrap samples (seed 2026); exact two-sided McNemar tests
use discordant numerical outcomes. Paired latency-change intervals use the same
question-level bootstrap. Report percentage points separately from relative percent
change. These are descriptive intervals for authored, nonrandom and repetitive tasks;
independence and population representativeness are weak. In this run the percentile bootstrap interval excludes zero while the exact McNemar
test is not significant at 0.05 (p=0.125). Sparse discordant outcomes make percentile
bootstrap intervals fragile; **McNemar is the primary paired significance check**,
not the visually narrower bootstrap interval. No causal or comprehensive
fiqh-competence claim follows. Unknown training overlap and unknown exact training
base revision further limit attribution to fine-tuning alone.
