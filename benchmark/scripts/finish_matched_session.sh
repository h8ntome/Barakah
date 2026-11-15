#!/usr/bin/env bash
# Run on server2 from the session root. Never interrupt another process.
set -euo pipefail
PY=/home/hadi/homefinance-benchmark-lfm3/.venv/bin/python
export HF_MODULES_CACHE=/home/hadi/ai/hf-barakah-cache/modules
# Wait only for this evaluation's own baseline service, not unrelated workloads.
while systemctl --user is-active --quiet barakah-original-20261115.service; do sleep 10; done
"$PY" - <<'PY'
import json
from pathlib import Path
files=list(Path('benchmark/results/raw').glob('original-matched_*.meta.json'))
assert len(files)==1 and json.loads(files[0].read_text())['status']=='completed', 'Baseline did not complete'
PY
"$PY" benchmark/scripts/check_hardware.py --output "benchmark/results/hardware/before_candidate_$(date -u +%Y%m%dT%H%M%S).json"
"$PY" benchmark/scripts/run_benchmark.py --model h8notme/barakah1 --revision 912a5697cf9d85adf065ee512f509cfa236459d4 --checkpoint-manifest benchmark/results/hardware/barakah1_checkpoint.json --run-name barakah-smoke --smoke-only > "benchmark/results/hardware/barakah_smoke_$(date -u +%Y%m%dT%H%M%S).log" 2>&1
"$PY" benchmark/scripts/run_benchmark.py --model h8notme/barakah1 --revision 912a5697cf9d85adf065ee512f509cfa236459d4 --checkpoint-manifest benchmark/results/hardware/barakah1_checkpoint.json --run-name barakah-matched > benchmark/results/raw/barakah_matched_execution.log 2>&1
"$PY" benchmark/scripts/check_hardware.py --output benchmark/results/hardware/after_models.json
