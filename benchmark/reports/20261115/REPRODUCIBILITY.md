# Reproduce the matched evaluation

All commands below run from the **Barakah repository root** unless specified.
Use a fresh run tag/output directory; never overwrite a published run. The evaluated
runner is archived at `benchmark/results/hardware/matched_run_benchmark.py`.
The original dataset, config and numerical grading rules were not changed. The current
runner adds post-evaluation response-hash/recovery guards; the two measured runs used
the identical archived runner. Do not resume either published run with changed source.

## 1. Existing server2 environment (used, not modified)

```sh
ssh -o BatchMode=yes server2
PY=/home/hadi/homefinance-benchmark-lfm3/.venv/bin/python
"$PY" -c 'import torch,transformers; print(torch.__version__,transformers.__version__); print(torch.cuda.get_device_name(),torch.cuda.is_bf16_supported())'
free -h
df -h /home
ps -eo pid,comm,%cpu,%mem --sort=-%cpu | head -15
exit
```

The saved package list is `results/hardware/matched_inference_environment.txt`:
Python 3.12.15, torch 2.12.0+rocm7.14.1, Transformers 5.20.0, Accelerate 1.15.0,
Hub 2.2.0. Use the already-working ROCm environment. Generic PyPI torch is not a
replacement for this AMD build. No installs or system-package changes were required.
If reproducing elsewhere, create a dedicated venv and install hardware-compatible
PyTorch following AMD guidance, then compatible dependencies from the recorded list;
do not claim matched timing on different hardware/runtime.

For local scoring/plots/tests only (no model weights or torch needed):

```sh
python3.12 -m venv /tmp/barakah-analysis-new
/tmp/barakah-analysis-new/bin/python -m pip install \
  PyYAML==6.0.3 psutil==7.2.2 matplotlib==3.11.2 pytest==9.2.0
PY=/tmp/barakah-analysis-new/bin/python
# This session actually used the existing /tmp/barakah-benchmark-venv/bin/python.
```

## 2. Fresh remote workspace

```sh
TAG=$(date -u +%Y%m%dT%H%M%S)
REMOTE=barakah-benchmark-$TAG
ssh server2 "mkdir -p ~/$REMOTE/benchmark/results/{raw,processed,hardware} ~/ai/hf-barakah-cache"
rsync -az --exclude=.venv --exclude=__pycache__ --exclude=.pytest_cache \
  --exclude=models --exclude=results --exclude=visuals --exclude=reports \
  benchmark/ "server2:$REMOTE/benchmark/"
ssh server2
# Substitute the REMOTE value printed/used above:
cd ~/barakah-benchmark-YOUR_TAG
PY=/home/hadi/homefinance-benchmark-lfm3/.venv/bin/python
export HF_XET_CACHE=/home/hadi/ai/hf-barakah-cache/xet
export HF_MODULES_CACHE=/home/hadi/ai/hf-barakah-cache/modules
```

The actual evaluated workspace was `/home/hadi/barakah-benchmark-20261115/`.
Its original run used the existing module cache; candidate used HF_MODULES_CACHE after
an initial permissions failure. Reproduction above sets one writable cache consistently.
This affects loading/cache state, not the identical source code or generation settings.

## 3. Download and verify exact snapshots

```sh
"$PY" benchmark/scripts/checkpoint.py \
  --model LiquidAI/LFM3-1.7B \
  --revision 1da06bec6a819da10b54c67e5c90972b46d81871 \
  --output benchmark/results/hardware/original_checkpoint.json
"$PY" benchmark/scripts/checkpoint.py \
  --model h8notme/barakah1 \
  --revision 912a5697cf9d85adf065ee512f509cfa236459d4 \
  --cache-dir /home/hadi/ai/hf-barakah-cache \
  --output benchmark/results/hardware/barakah1_checkpoint.json
"$PY" benchmark/scripts/inspect_pair.py \
  --baseline benchmark/results/hardware/original_checkpoint.json \
  --candidate benchmark/results/hardware/barakah1_checkpoint.json \
  --output benchmark/results/hardware/checkpoint_compatibility.json
"$PY" benchmark/scripts/check_hardware.py \
  --output benchmark/results/hardware/before_models.json
"$PY" benchmark/scripts/validate_benchmark.py
```

`checkpoint.py` resolves a Hub SHA, verifies sizes and LFS hashes and saves every file
hash. Passing `--revision main` resolves today's commit for a *new* experiment; use the
fixed SHA above to reproduce this evaluation. Both primary runs rehash snapshot files
before inference. The candidate is full-model BF16. Adapter detection exists and the
runner fails closed for adapter input; no untested adapter inference is claimed.

## 4. Actual smoke tests and serial full inference

Do not run the two models simultaneously. Run both smoke checks first in a fresh
reproduction; this session's candidate smoke/full sequence waited for baseline completion.

```sh
"$PY" benchmark/scripts/run_benchmark.py --model LiquidAI/LFM3-1.7B \
  --revision 1da06bec6a819da10b54c67e5c90972b46d81871 \
  --checkpoint-manifest benchmark/results/hardware/original_checkpoint.json \
  --run-name original-smoke --smoke-only
"$PY" benchmark/scripts/run_benchmark.py --model h8notme/barakah1 \
  --revision 912a5697cf9d85adf065ee512f509cfa236459d4 \
  --checkpoint-manifest benchmark/results/hardware/barakah1_checkpoint.json \
  --run-name barakah-smoke --smoke-only

# Full runs: create a managed user job so an SSH disconnect cannot discard progress.
systemd-run --user --unit=barakah-matched-YOUR_TAG --collect \
  --setenv=HF_MODULES_CACHE=/home/hadi/ai/hf-barakah-cache/modules \
  /bin/bash -c 'set -e; cd ~/barakah-benchmark-YOUR_TAG;
  PY=/home/hadi/homefinance-benchmark-lfm3/.venv/bin/python;
  "$PY" benchmark/scripts/run_benchmark.py --model LiquidAI/LFM3-1.7B \
    --revision 1da06bec6a819da10b54c67e5c90972b46d81871 \
    --checkpoint-manifest benchmark/results/hardware/original_checkpoint.json \
    --run-name original-matched > benchmark/results/raw/original_matched_execution.log 2>&1;
  "$PY" benchmark/scripts/run_benchmark.py --model h8notme/barakah1 \
    --revision 912a5697cf9d85adf065ee512f509cfa236459d4 \
    --checkpoint-manifest benchmark/results/hardware/barakah1_checkpoint.json \
    --run-name barakah-matched > benchmark/results/raw/barakah_matched_execution.log 2>&1'
systemctl --user status barakah-matched-YOUR_TAG
```

Published full run IDs:
- `original-matched_20261115T153923318073+0000`
- `barakah-matched_20261115T154845353654+0000`

The run ID is printed as the last log line and stored in its `.meta.json`. Success
requires metadata status completed, 100 unique IDs, and inspection of failure counts.
Do not interpret the service's completion alone as 100 successful generations.

For safe recovery, rerun the exact command with `--resume EXACT_RUN_ID`. Keep model,
revision, manifest, config, dataset, device, runtime and runner source unchanged.
Do not remove a `.lock` without verifying its recorded PID is dead. Completed records,
including failures, are never replaced; no best-of answer selection is supported.

Optional shared-host telemetry during the managed job:

```sh
"$PY" benchmark/scripts/monitor_workload.py \
  --output benchmark/results/hardware/workload_samples.jsonl \
  --units barakah-matched-YOUR_TAG
```

## 5. Score and transfer lightweight evidence

```sh
"$PY" benchmark/scripts/evaluate_responses.py --run original-matched
"$PY" benchmark/scripts/evaluate_responses.py --run barakah-matched
"$PY" benchmark/scripts/validate_benchmark.py
exit
# Copy only this NEW workspace's outputs; never --delete, never copy model weights.
rsync -az "server2:$REMOTE/benchmark/results/" benchmark/results/
```

If the local repository already contains matched runs, use the exact new run IDs below,
not a prefix that resolves to multiple runs. Scoring can alternatively run locally on
saved raw files and metadata with the lightweight analysis Python.

## 6. Paired comparison, figures and reports

The session-specific output below is already published; choose a new directory to rerun.
Both full run IDs appear in BENCHMARK_REPORT.md and comparison.json.

```sh
PY=/tmp/barakah-benchmark-venv/bin/python
"$PY" benchmark/scripts/paired_analysis.py \
  --baseline EXACT_ORIGINAL_RUN_ID --candidate EXACT_BARAKAH_RUN_ID \
  --output benchmark/results/comparisons/NEW_TAG
"$PY" benchmark/scripts/paired_visuals.py \
  --comparison benchmark/results/comparisons/NEW_TAG/comparison.json \
  --output benchmark/visuals/NEW_TAG
"$PY" benchmark/scripts/paired_reports.py \
  --comparison benchmark/results/comparisons/NEW_TAG/comparison.json \
  --output benchmark/reports/NEW_TAG
"$PY" -m pytest benchmark/tests -q
```

The dashboard currently links to the published 20261115 documentation/comparison
namespace; for a differently named publication, update those links as part of publishing
and rerun link validation. Do not label an alternate experiment as this one.

Open `benchmark/visuals/20261115/html/index.html` directly in a browser. It requires
no web server, internet, API, framework or live model. A separate `review.html` supports
blinded conceptual assessment; see HUMAN_REVIEW.md.

## 7. Validate the published artifact set

```sh
"$PY" benchmark/scripts/validate_benchmark.py
"$PY" benchmark/scripts/validate_paired_artifacts.py \
  --comparison benchmark/results/comparisons/20261115/comparison.json \
  --visuals benchmark/visuals/20261115 \
  --verify-manifest benchmark/results/comparisons/20261115/artifact_integrity.json
```

Actual browser integration (requires the installed agent-browser CLI):

```sh
bash benchmark/tests/check_dashboard.sh
```

Post-inference tensor verification, on server2 after both models have stopped:

```sh
"$PY" benchmark/scripts/verify_weight_difference.py \
  --baseline benchmark/results/hardware/original_checkpoint.json \
  --candidate benchmark/results/hardware/barakah1_checkpoint.json \
  --output benchmark/results/hardware/weight_difference_NEW.json
```

The validator rechecks raw/processed provenance, recomputes paired statistics,
compares chart inputs, checks all question IDs and local dashboard links, verifies
PNG dimensions, and checks the archived evaluated runner hash. The integrity manifest
is written once only after final artifacts are complete. Browser checks and the test
receipt are recorded in VERIFICATION.md. No credentials or multi-gigabyte weights are
part of these artifacts.
