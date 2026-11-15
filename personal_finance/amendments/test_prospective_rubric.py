"""Supplemental validation for the disclosed late rubric amendment and packets."""
import hashlib
import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DIMENSIONS={'financial_correctness','practical_usefulness','personalization','reasoning_and_tradeoffs','safety_and_uncertainty'}

class ProspectiveRubricTests(unittest.TestCase):
    def test_separate_amendment_integrity(self):
        manifest=json.loads((ROOT/'amendments/amendment_manifest.json').read_text())
        for name,expected in manifest['files'].items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),expected)
        self.assertFalse(manifest['model_answer_text_inspected_by_author'])
        self.assertFalse(manifest['numeric_outcomes_inspected_by_author'])
        self.assertIsNone(manifest['subjective_scores'])
        canonical=ROOT/'amendments/canonical_parent_rubric.json'
        self.assertEqual(hashlib.sha256(canonical.read_bytes()).hexdigest(),'27ab3aa1571a66d0b637355caf0284b999e0c6a836b32d41484c8f43d8ed5503')
        adoption=json.loads((ROOT/'amendments/canonical_adoption.json').read_text())
        self.assertTrue(adoption['worker_no_PF_answer_text_or_numeric_outcomes_inspected_at_adoption'])

    def test_exact_five_dimensions_and_anchors(self):
        rubric=json.loads((ROOT/'amendments/canonical_parent_rubric.json').read_text())
        self.assertEqual(set(rubric['dimensions']),DIMENSIONS)
        for anchors in rubric['dimensions'].values(): self.assertEqual(set(anchors),set('01234'))

    def test_completed_packets_when_available(self):
        path=ROOT/'results/analysis/reviewer_packets_canonical/pairs.json'
        if not path.exists(): self.skipTest('Inference/export not yet complete')
        packets=json.loads(path.read_text())
        mapping=json.loads((ROOT/'results/analysis/private_mapping/identity_mapping.json').read_text())
        self.assertEqual(len(packets),50)
        self.assertEqual(len({p['question_id'] for p in packets}),50)
        self.assertEqual({p['packet_id'] for p in packets},{p['packet_id'] for p in mapping})
        for packet in packets:
            self.assertIsNone(packet['reviewer_id'])
            self.assertIsNone(packet['reviewed_at'])
            self.assertNotIn('model',packet)
            self.assertIsNone(packet['reviewer_qualifications'])
            for label,text in packet['responses'].items():
                self.assertEqual(packet['response_sha256'][label],hashlib.sha256(text.encode()).hexdigest())
            for scores in packet['scores'].values():
                self.assertEqual(set(scores),DIMENSIONS)
                self.assertTrue(all(value is None for value in scores.values()))
        self.assertNotIn('identity_mapping.json',{p.name for p in path.parent.iterdir()})

if __name__=='__main__': unittest.main()
