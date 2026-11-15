"""Audit existing evidence without regenerating or overwriting published scores."""
from fractions import Fraction
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from audit_original import audit, independent_reference
from common import dataset


def test_all_frozen_numeric_references_with_rational_arithmetic():
    numeric = [q for q in dataset() if q['scoring_method'] == 'deterministic']
    assert len(numeric) == 40
    for q in numeric:
        assert independent_reference(q) == Fraction(q['expected_numeric'])


def test_actual_matched_audit_does_not_invent_format_corrections():
    result = audit('original-matched_20261115T153923318073+0000',
                   'barakah-matched_20261115T154845353654+0000')
    assert result['rendered_prompt_hashes_equal'] is True
    assert result['semantic_rescore_applied'] is False
    assert [r['strict_counts']['correct'] for r in result['runs']] == [36, 32]
    assert [r['strict_counts']['unparseable'] for r in result['runs']] == [0, 0]
