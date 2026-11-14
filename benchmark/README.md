# Barakah AI benchmark

An independently runnable evaluation system for Barakah, an Islamic personal-finance prototype for the Veritas AI International High School Hackathon 2026. The production frontend in `../barakah-ui/` remains separate: **this benchmark does not connect the app to a live assistant**.

## What was tested

The instruction-tuned **LiquidAI/LFM3-1.7B**, not `-Base`, is the original model reference. Its small, locally deployable size matches the project brief; this is a project choice, not evidence that it is the best model. A public-question-only zakat formula calculator supplies a narrow simple baseline. **No adapted checkpoint currently exists in this evaluation.**

See [the actual report](reports/BENCHMARK_REPORT.md), [judge summary](reports/EXECUTIVE_SUMMARY.md) and [offline dashboard](visuals/html/index.html). Open the dashboard directly in a browser; no backend, internet or JavaScript framework is required. Its category filter is optional JavaScript; all content remains readable without it.

## Evidence and layout

- `config.yaml`: checkpoint SHA, neutral system instruction, greedy decoding, seed, attention implementation and output limit.
- `datasets/benchmark_questions.{json,csv}`: 100 held-out questions in five categories.
- `datasets/dataset_manifest.json`: version, exact checksums, counts and review status.
- `datasets/DATASET_CARD.md`: construction, sources, eligibility and leakage policy.
- `results/raw/<run-id>.jsonl`: all real responses, question text, latency, token counts, errors and truncation.
- `results/raw/<run-id>.meta.json`: model revision, full chat template, hardware, library versions, warm-up and run timestamps.
- `results/processed/<run-id>.json`: automatic numeric grades and **separate** human-review channels.
- `results/comparisons/`: paired-task comparisons.
- `results/hardware/`: both inspected hosts, download verification and real GPU smoke test.
- `results/remote_integrity.json`: SHA256 manifest created remotely and verified after transfer.
- `visuals/{png,svg,html}/`: eight evidence-based figure pairs and offline dashboard.
- `reports/`: methodology, limitations, model card, hardware decision and measured findings.
- `tests/`: unit and integration checks, never used as benchmark data.

All benchmark artifacts are under this directory. Downloaded weights remain in server2's existing Hugging Face cache and are never staged. Existing training or evaluation projects on server2 were not edited or used as test data.

## Execution environment selected

**server2**: AMD Ryzen AI MAX+ 395, Radeon 8060S, ROCm PyTorch, BF16 weights. The Mac has an Apple M4 and 16 GiB RAM, but only about 4 GiB free disk at inspection. Server2 already cached the exact official BF16 snapshot and had substantial free RAM and disk.

GPU execution actually succeeded; it is not CUDA/NVIDIA hardware even though PyTorch exposes ROCm through its `torch.cuda` API. There is **no comparable local inference timing**, so no measured speedup between machines is claimed. Read [HARDWARE_COMPARISON.md](reports/HARDWARE_COMPARISON.md).

## Installation

Python **3.12** is the tested interpreter family. Use an isolated environment; do not install into Barakah's frontend or a shared global Python.

```sh
cd /path/to/Barakah
python3.12 -m venv benchmark/.venv
source benchmark/.venv/bin/activate
python -m pip install --upgrade pip
# Install an appropriate PyTorch wheel first (CPU, CUDA or ROCm).
# Example portable CPU environment:
python -m pip install torch==2.12.0
python -m pip install -r benchmark/requirements.txt
```

The exact server2 runtime used an already available read-only environment at
`/home/hadi/homefinance-benchmark-lfm3/.venv/bin/python`, Python 3.12.15, PyTorch
`2.12.0+rocm7.14.1` and Transformers `5.20.0`. No packages in that environment were modified.
Its complete package snapshot is in `results/hardware/inference-environment.txt`.
Generic PyPI `torch==2.12.0` is **not** a substitute for that ROCm build when reproducing GPU timings.
Install the AMD-provided wheel/runtime for the exact hardware following AMD's documentation.
The portable dependency file pins direct dependencies; recorded full environment snapshots provide transitive provenance.

Analysis/plots need only `PyYAML==6.0.3 psutil==7.2.2 matplotlib==3.11.2 pytest==9.2.0`; downloading PyTorch or model weights is unnecessary for re-scoring saved results.
The initial Mac environment encountered iCloud dataless-file errors, so final local analysis used
`/tmp/barakah-benchmark-venv`, with its package snapshot recorded separately. No virtual environment is committed.

## Download, validate and run

Commands below work from the repository root; dataset paths resolve against `benchmark/`.

```sh
python benchmark/scripts/check_hardware.py
python benchmark/scripts/download_model.py
python benchmark/scripts/smoke_model.py
python benchmark/scripts/validate_benchmark.py
python benchmark/scripts/run_benchmark.py --model LiquidAI/LFM3-1.7B --run-name original
python benchmark/scripts/evaluate_responses.py --run original
python benchmark/scripts/run_baseline.py --run-name rules
python benchmark/scripts/evaluate_responses.py --run rules
python benchmark/scripts/compare_models.py --baseline original --candidate rules
python benchmark/scripts/generate_visuals.py
python benchmark/scripts/generate_reports.py
python -m pytest benchmark/tests -q
```

The download script resolves the pinned commit, checks disk space and hardware, reuses the cache while retrieving missing files, verifies required files, opens safetensors and records file SHA256s. It rejects weights whose SHA256 differs from the official pinned Hugging Face LFS object. The evaluated weight hash is `135922caef64e81e52af88ede8b7c3ddaa9d6da220a9737fb3065275dbfb4330`. The official model requires `trust_remote_code=True`; only run code from a revision you have reviewed. The code and weights are pinned together. The evaluated model is BF16 safetensors with **no quantization**. CPU fallback uses FP32 execution; this changes performance and possibly outputs and must be reported.

Liquid AI's **LFM Open License v1.0** applies. See the official checkpoint's LICENSE; it is not represented as Apache/MIT model licensing. Users must independently check the license before deployment, redistribution or commercial use.

### Resume and failure handling

Each invocation creates a unique timestamped run ID. Errors remain in raw output and count in attempted-task denominators. A resume skips already saved rows, including failures: it never silently replaces bad generations.

```sh
python benchmark/scripts/run_benchmark.py --run-name original --resume EXACT_RUN_ID
```

Use the same model, revision, configuration, device and dataset. Fingerprint mismatches abort. An incomplete **final** JSONL record can be truncated on recovery; interior corruption and duplicate IDs fail loudly. The exclusive `.lock` prevents concurrent writers. If the machine was killed without cleanup, verify that the recorded PID is no longer running **before manually removing only that run's stale lock**.

If multiple original runs exist, pass an exact run ID to all scripts instead of an ambiguous name.
Kernel compilation and one short warm-up are recorded separately. Model loading and setup are included in total segment durations but not per-answer latency.

## Executing on server2

The saved run used `/home/hadi/barakah-benchmark-20261114/benchmark/`. To reproduce in a fresh, user-owned location:

```sh
ssh -o BatchMode=yes server2 'mkdir -p ~/barakah-benchmark/benchmark'
rsync -az --exclude=.venv --exclude=models --exclude=__pycache__ \
  benchmark/ server2:barakah-benchmark/benchmark/
ssh server2
cd ~/barakah-benchmark
# Activate your isolated, hardware-compatible environment first.
python benchmark/scripts/check_hardware.py --output benchmark/results/hardware/server2.json
python benchmark/scripts/download_model.py
python benchmark/scripts/smoke_model.py
# Use a managed user job so SSH disconnects do not destroy progress:
systemd-run --user --unit=barakah-benchmark-original --collect \
  /bin/bash -c 'cd ~/barakah-benchmark; /absolute/path/to/python benchmark/scripts/run_benchmark.py --run-name original > benchmark/results/raw/original_execution.log 2>&1'
# Monitor without changing or killing any unrelated workload:
systemctl --user status barakah-benchmark-original
tail -n 5 benchmark/results/raw/original_execution.log
# After completion:
python benchmark/scripts/validate_benchmark.py --write-integrity
exit
rsync -az server2:barakah-benchmark/benchmark/results/ benchmark/results/
python benchmark/scripts/validate_benchmark.py
```

Only user-owned benchmark outputs are synchronized; model weights and other projects are not copied. Do not use `rsync --delete` against shared directories.
Remote computation in the published run used the official model's cached BF16 weights; no redundant 3.3 GiB model download to the Mac was necessary.

## What accuracy means here

Forty explicit numeric questions have Decimal-verified expected answers. The terminal `Final answer:` quantity is checked with a 0.01 absolute tolerance and matching units. The full attempted numeric denominator includes errors and unparseable answers. Correct numeric output **does not certify surrounding religious or financial claims**.

Sixty conceptual answers require human rubric review. Their institutional references were checked, but no independent qualified scholar or financial professional has adjudicated the model answers. No keyword-presence or LLM-judge score is promoted to verified correctness. Safety regexes are **review candidates only**, including warnings/negations. Verified safety and hallucination rates are unavailable with zero reviewed denominator.

Human review is bound to the exact run, dataset and response bytes. Supply an auditable JSON envelope with a mapping keyed by question ID:

```json
{
  "run_id": "EXACT_RUN_ID",
  "dataset_sha256": "SHA256_FROM_MANIFEST",
  "reviews": {
    "QUESTION_ID": {
      "run_id": "EXACT_RUN_ID",
      "response_sha256": "SHA256_OF_EXACT_UTF8_RESPONSE_TEXT",
      "reviewer": "identified reviewer and relevant qualification",
      "reviewed_at": "ISO-8601 timestamp",
      "evidence": "Source-backed explanation and reference passages",
      "correctness": null,
      "safety_failure": null,
      "hallucination": null
    }
  }
}
```

Replace null **only after** actual review. Review all required key facts and contradictions, completeness, unsupported religious assertions, interpretive differences, uncertainty and fabrication; do not grade by string overlap.
`python benchmark/scripts/evaluate_responses.py --run EXACT_ID --reviews /path/to/reviews.json`
preserves automatic and human fields separately. Re-score and regenerate figures/reports after verified review; never edit raw outputs.

## Future adapted model

Keep these questions and reference answers out of fine-tuning, retrieval and development demonstrations. A future model must be trained on a separate source corpus and evaluated with the frozen dataset, prompt and generation configuration.

```sh
python benchmark/scripts/run_benchmark.py --model /path/to/finetuned-model --run-name barakah-finetuned
# For a Hugging Face candidate also pass --revision EXACT_COMMIT_SHA.
python benchmark/scripts/evaluate_responses.py --run barakah-finetuned
python benchmark/scripts/compare_models.py --baseline original --candidate barakah-finetuned
```

All local candidate file hashes are recorded and checked on resume; remote candidate revisions resolve to exact commit SHAs. Resumes reject changes to resolved device, precision, runtime or host. Processed outputs bind raw responses and metadata by SHA256; comparisons and chart loaders reject stale scores until re-evaluation. Comparisons report common-task absolute/percentage-point/relative changes, categories, disagreements, recorded safety channels and latency. Null baselines have no relative change. Different devices/runtimes/configurations are disclosed; cross-machine speeds are not model improvements. The current dashboard explicitly marks adapted results unavailable; it does not invent a candidate. Once a real candidate is scored, regenerate its matched comparison with `python benchmark/scripts/generate_visuals.py --candidate barakah-finetuned`.

## Regeneration and constraints

`build_dataset.py` reconstructs the frozen authored release from `conceptual_questions.json` and deterministic scenarios. **Do not rebuild/edit questions during inference.** Any content change requires a dataset version bump and new model runs. To reproduce published scoring/plots, use the committed JSON, not a new dataset build.

`generate_visuals.py` and `generate_reports.py` read processed real runs. Figures 7–8 use truthful unavailable-data annotations where comparisons do not exist. Synthetic values appear only in unit tests, never in figures or reports.

See [METHODOLOGY.md](reports/METHODOLOGY.md), [MODEL_CARD.md](reports/MODEL_CARD.md) and [LIMITATIONS.md](reports/LIMITATIONS.md). This is an exploratory baseline, not a standardized external benchmark, fatwa service, securities certification or permission to deploy unsupervised financial advice.
