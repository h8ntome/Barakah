"""Provenance-only exports. No inference and no historical evidence changes."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from common import ROOT, digest
from compare_models import compare, effective_run_settings, processed
from run_benchmark import resolved_config

BASELINE = 'original-matched_20261115T153923318073+0000'
CANDIDATE = 'barakah-matched_20261115T154845353654+0000'
MODEL = 'h8notme/barakah1'
REVISION = '912a5697cf9d85adf065ee512f509cfa236459d4'


def test_cli_overrides_recorded_without_rewriting_template():
    template = {'model': 'baseline', 'revision': 'old', 'device': 'auto', 'dtype': 'bfloat16', 'generation': {'max_new_tokens': 384}}
    before = copy.deepcopy(template)
    effective = resolved_config(template, 'candidate', 'new', 'cpu', 'torch.float32')
    assert template == before
    assert effective == {**template, 'model': 'candidate', 'revision': 'new', 'device': 'cpu', 'dtype': 'float32'}


def test_template_identity_never_used_as_actual_identity():
    result = effective_run_settings({'config': {'model': 'template-only', 'revision': 'not-evidence'}})
    assert result['model'] is None and result['revision'] is None and result['identity_evidence'] == []


@pytest.mark.parametrize('source', ['checkpoint_manifest', 'effective_config', 'checkpoint_revision', 'raw_rows'])
def test_conflicting_identity_is_rejected(source):
    meta = {'fingerprint': {'model': MODEL, 'revision': REVISION}}
    records = [{'model': MODEL, 'revision': REVISION}]
    if source == 'checkpoint_revision': meta[source] = 'wrong'
    elif source == 'raw_rows': records[0]['model'] = 'wrong'
    else: meta[source] = {'model': 'wrong', 'revision': REVISION}
    with pytest.raises(ValueError): effective_run_settings(meta, records)


def test_legacy_raw_missing_revision_is_explicitly_partial_not_conflicting():
    result = effective_run_settings({'fingerprint': {'model': MODEL, 'revision': REVISION}}, [{'model': MODEL}])
    assert result['revision'] == REVISION
    assert result['raw_identity_fields'] == ['model'] and 'raw_rows_partial' in result['identity_evidence']
    assert 'raw_rows' not in result['identity_evidence']


def test_historical_candidate_identity_corrected_only_in_new_export():
    a, b = processed(BASELINE), processed(CANDIDATE)
    before = copy.deepcopy(b['metadata'])
    output = compare(a, b)
    actual = output['candidate_effective_run_settings']
    assert actual['model'] == MODEL and actual['revision'] == REVISION
    assert actual['template_identity_differs'] is True
    assert 'raw_rows' in actual['identity_evidence'] and 'checkpoint_manifest' in actual['identity_evidence']
    assert output['candidate_template_config']['model'] == 'LiquidAI/LFM3-1.7B'
    assert 'candidate_config' not in output
    assert b['metadata'] == before
    assert output['paired_numeric_n'] == 40
    assert output['numeric_correctness']['baseline'] == 36 / 40
    assert output['numeric_correctness']['candidate'] == 32 / 40
    assert output['categories']['zakat']['n'] == 15
    assert output['categories']['zakat']['baseline'] == 12 / 15
    assert output['categories']['zakat']['candidate'] == 11 / 15
    assert output['human_reviewed_correctness']['paired_n'] == 0


def test_export_refuses_overwrite_and_preserves_historical_hashes(tmp_path):
    historical = [ROOT / 'results/comparisons/20261115/comparison.json']
    for run in (BASELINE, CANDIDATE):
        historical += [ROOT / f'results/raw/{run}{suffix}' for suffix in ('.jsonl', '.meta.json')]
        historical += [ROOT / f'results/processed/{run}.json']
    before = {str(path): digest(path) for path in historical}
    destination = tmp_path / 'identity-v2.json'
    command = [sys.executable, str(ROOT / 'scripts/compare_models.py'), '--baseline', BASELINE, '--candidate', CANDIDATE, '--output', str(destination)]
    first = subprocess.run(command, capture_output=True, text=True)
    assert first.returncode == 0, first.stderr
    assert json.loads(destination.read_text())['candidate_effective_run_settings']['model'] == MODEL
    exported = digest(destination)
    second = subprocess.run(command, capture_output=True, text=True)
    assert second.returncode != 0 and 'FileExistsError' in second.stderr
    assert digest(destination) == exported
    assert {str(path): digest(path) for path in historical} == before
