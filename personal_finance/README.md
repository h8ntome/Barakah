# Personal Finance Domain Adaptation Benchmark v1.0

**50 newly authored English scenarios:** budgeting 10; saving, debt, decisions, literacy and conversations 8 each. This tests general personal-finance adaptation, not Islamic-finance superiority or production integration.

## What is measured

- **23 limited numeric probes:** exact final `ANSWER_AMOUNT` and `ANSWER_UNIT` extraction, with Decimal references and an absolute 0.01 tolerance. A right number is **not** a finding of correct/safe financial advice. Formatting failures count as failures, not ignored cases.
- **Five human dimensions, 0–4 (prospectively amended):** financial correctness; practical usefulness; personalization; reasoning/trade-offs; safety/uncertainty. All actual subjective scores remain **null**; no independent human review has been performed.
- **Disclosed protocol deviation:** the initial 16:18:54Z freeze omitted a standalone reasoning/trade-offs dimension and included communication/empathy instead. Inference began at 16:19:04Z. A separately hashed worker amendment was frozen at 16:22:26Z. The supervisor subsequently supplied the canonical rubric (receipt 16:25:04Z; adopted 16:27:14Z), which is the only active human-review rubric. Both declarations preceded worker/parent inspection of generated answer text or numeric outcomes. Original frozen files are unchanged; the worker amendment remains superseded audit history. Use only canonical reviewer packets; see `amendments/canonical_adoption.json`.
- **Paired comparison:** identical questions, system prompt, template, greedy generation settings, seed, hardware and token budget. The models differ in their pinned full checkpoints. Fixed base-first order is a possible timing/load confound, not an outcome-based choice.

## Reproduce and inspect

From `/tmp/barakah-rescue-pf-20261115` (or the matching server2 root):

```sh
python3 -m unittest discover -s personal_finance/tests -v
python3 -c "import sys; sys.path.insert(0,'personal_finance/scripts'); from benchmark_lib import verify_freeze; verify_freeze()"
```

The standard-library tests, numeric analysis, overlap screening and release verification need no external packages. Inference uses the **existing** server2 environment at `/home/hadi/homefinance-benchmark-lfm3/.venv/bin/python`, plus the copied `benchmark/scripts/{checkpoint,common,check_hardware}.py` dependencies. Exact model snapshots must already exist at the locations in the copied manifests; inference is offline and rehashes all checkpoint files. Do not install/repair infrastructure as part of this benchmark.

The **historical** managed launch was (do not rerun against these outputs):

```sh
systemd-run --user --unit=barakah-pf-rescue-20261115 \
  --property=WorkingDirectory=/home/hadi/barakah-pf-rescue-20261115 \
  --property=RuntimeMaxSec=1800 \
  /usr/bin/bash /home/hadi/barakah-pf-rescue-20261115/personal_finance/scripts/run_pair.sh
```

The shipped run already occupies its output directories; **do not rerun it**. The runner refuses an existing model directory. The pair script refuses an existing launch record. It never selectively repeats failed/truncated/unparseable answers. Inference has no calculator, retrieval or other model tools. The full mode was selected before either model ran. A deadline fallback of first two IDs per category was declared beforehand, not selected by results.

**Future full reproduction:** the historical `run_pair.sh` permanently selects reduced mode after 2026-11-15 16:33 UTC. Preserve that frozen script, but do not use it to reproduce all 50 later. In a fresh copied root with no existing `results/base` or `results/candidate` (and a unique managed systemd unit), explicitly invoke in sequence:

```sh
export HF_MODULES_CACHE=/home/hadi/ai/hf-barakah-cache/modules
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
PY=/home/hadi/homefinance-benchmark-lfm3/.venv/bin/python
"$PY" personal_finance/scripts/run_inference.py --model-key base --mode full
"$PY" personal_finance/scripts/run_inference.py --model-key candidate --mode full
"$PY" personal_finance/scripts/analyze.py
"$PY" personal_finance/amendments/export_canonical_packets.py
```

Preserve this release's original results separately; never delete them to make a rerun fit.

## Evidence map

- `questions.json`: scenarios, authored human reference considerations, numeric specifications.
- `rubric.json`, `numeric_rules.json`, `inference_config.json`: frozen evaluation contract.
- `freeze_manifest.json`, `freeze_manifest.sha256`, `results/freeze_event.json`: immutable pre-inference SHA256 freeze and time.
- `PROVENANCE.md`, `evidence/`: corpus lineage uncertainty, public HF metadata, read-only server probe, overlap report, pre-freeze tests.
- `results/{base,candidate}/responses.jsonl`: preserved raw answers, tokens, timing, truncation, errors and hashes.
- `results/{base,candidate}/metadata.json`: pinned revisions, verified manifests, software/hardware, declared generation config, load times and status. The frozen field named `effective_generation_config` is pre-merge; see the next audit for resolved runtime defaults.
- `results/resolved_generation_compatibility.json`: installed Transformers default-merge and length-resolution audit; all 50 operative configs equal. The candidate's inherited max_length differs before resolution but is overridden by the shared max_new_tokens setting.
- `results/tokenizer_compatibility.json`, `results/final_validation.json`: all 50 input-ID sequences, actual prompt hashes and final artifact parity verified.
- `results/analysis/summary.json`: counts and paired numeric outcomes, **not a general-quality leaderboard**.
- `results/analysis/numeric_records.json`: per-item limited extraction outcomes.
- `results/analysis/reviewer_packets_canonical/`: distribute only this corrected-rubric directory to independent human reviewers. The original `reviewer_packets/` is retained for audit only and must not be used for scoring.
- `amendments/canonical_parent_rubric.json`: supervisor's canonical prospective late rubric, SHA256 `27ab3aa1571a66d0b637355caf0284b999e0c6a836b32d41484c8f43d8ed5503`. `export_canonical_packets.py` applies it without changing original outputs or scores. Earlier worker amendment is superseded. No change to questions, numeric rules or inference.
- `results/analysis/private_mapping/`: identity key, separate from reviewer packets; do not give to reviewers before scoring. Public generation config contains the randomization seed; keep that away from blinded reviewers too.
- `REPORT.md`: actual run findings and limitations (written after inference).

The corpus was not copied into this deliverable. Read-only overlap screening can be reproduced where it already exists:

```sh
python3 personal_finance/scripts/overlap.py /tmp/homefinance-corpus/train_0.jsonl
```

This recreates the same report but should not be used to edit a frozen release; use a separate copied audit workspace if changing screening inputs. The checked corpus's 27,981 records match a public pinned HF LFS hash. Actual fine-tuning rows are unavailable, and lexical non-overlap does not establish semantic or training-set independence.

## Interpretation boundaries

The scenarios and rubric were authored by an AI assistant and are not independently validated financial advice. Conversation items are static conversation updates in a single prompt, not live multi-turn tests. The 384-token ceiling can truncate otherwise useful advice or final labels. Formatting compliance, not just arithmetic skill, affects the numeric metric. No subjective winner, safety certification, training-set independence, domain-adaptation causal attribution or production readiness is established. This benchmark does not connect any model to a product.
