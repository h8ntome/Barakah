"""Charts use recorded measurements; synthetic receipts only test log parsing."""
from pathlib import Path
import sys
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from submission_visuals import load_evidence, test_count as receipt_count


def test_receipts_require_an_executed_test_count(tmp_path):
    receipt = tmp_path / 'tests.log'
    receipt.write_text('7 passed, 1 skipped in 0.40s\n')
    assert receipt_count(receipt, 'passed') == 7
    assert receipt_count(receipt, 'skipped') == 1
    receipt.write_text('Tests have not run.\n')
    with pytest.raises(ValueError, match='Missing executed test receipt'):
        receipt_count(receipt, 'passed')


def test_chart_inputs_cover_real_complete_runs():
    questions, summary, records, audit = load_evidence()
    assert len(questions) == 50
    assert len(records) == 100
    assert summary['human_review_status'] == 'not_performed'
    assert summary['subjective_scores'] is None
    assert [r['numeric_denominator'] for r in audit['runs']] == [40, 40]
    assert all(summary['models'][key]['numeric_eligible_full'] == 23 for key in ('base', 'candidate'))
