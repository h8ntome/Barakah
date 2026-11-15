#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/../.."
export HF_MODULES_CACHE=/home/hadi/ai/hf-barakah-cache/modules
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
PY=/home/hadi/homefinance-benchmark-lfm3/.venv/bin/python
MODE=$($PY -c 'from datetime import datetime,timezone; print("reduced" if datetime.now(timezone.utc)>=datetime(2026,11,15,16,33,tzinfo=timezone.utc) else "full")')
# Creation is exclusive. Preserve all logs and errors, including load failure.
(set -o noclobber; printf '%s mode=%s\n' "$(date -u +%FT%TZ)" "$MODE" > personal_finance/results/launch.txt) || exit 1
"$PY" personal_finance/scripts/run_inference.py --model-key base --mode "$MODE" > personal_finance/results/base.log 2>&1
BASE_STATUS=$?
"$PY" personal_finance/scripts/run_inference.py --model-key candidate --mode "$MODE" > personal_finance/results/candidate.log 2>&1
CANDIDATE_STATUS=$?
printf 'base_exit=%s candidate_exit=%s\n' "$BASE_STATUS" "$CANDIDATE_STATUS" > personal_finance/results/exit_status.txt
if [ "$BASE_STATUS" -eq 0 ] && [ "$CANDIDATE_STATUS" -eq 0 ]; then
  "$PY" personal_finance/scripts/analyze.py > personal_finance/results/analysis.log 2>&1
else
  exit 1
fi
