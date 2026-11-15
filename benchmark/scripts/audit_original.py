"""Non-mutating audit of the original numerical comparison; never changes its grader."""
import argparse
import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path
from common import ROOT, dataset, digest, load_jsonl, now, save
from compare_models import processed
from evaluate_responses import numeric_grade
from paired_analysis import validate_pair


def independent_reference(question):
    """Rational arithmetic, independent of the dataset's Decimal reference builder."""
    spec = question['calculation']
    a = [Fraction(str(value)) for value in spec['operands']]
    operations = {
        'zakat': lambda: sum(a) / 40,
        'sum': lambda: sum(a),
        'difference': lambda: a[0] - sum(a[1:]),
        'savings_rate': lambda: 100 * a[0] / a[1],
        'multiply': lambda: a[0] * a[1],
        'divide': lambda: a[0] / a[1],
    }
    return Fraction(round(operations[spec['operation']]() * 100), 100)


def audit(baseline, candidate):
    questions = dataset()
    runs = [processed(name) for name in (baseline, candidate)]
    validate_pair(*runs, questions)
    numeric = [q for q in questions if q['scoring_method'] == 'deterministic']
    for q in numeric:
        if independent_reference(q) != Fraction(q['expected_numeric']):
            raise ValueError(f"Reference arithmetic mismatch: {q['id']}")
    receipts = []
    prompt_hashes = []
    for run in runs:
        path = ROOT / 'results/raw' / (run['run_id'] + '.jsonl')
        raw = load_jsonl(path)
        if [r['question_id'] for r in raw] != [q['id'] for q in questions]:
            raise ValueError('Missing, reordered or extra responses')
        counts = Counter()
        extraction = []
        for q, r in zip(questions, raw):
            if r['question'] != q['question']:
                raise ValueError('Question text mismatch')
            response_hash = hashlib.sha256(r['response'].encode()).hexdigest()
            # Earlier immutable records have whole-file hashes but no per-row hash.
            if r.get('response_sha256', response_hash) != response_hash:
                raise ValueError('Response checksum mismatch')
            if q['scoring_method'] != 'deterministic':
                continue
            grade = ({'status': 'generation_error', 'parsed_value': None} if r.get('error') else
                     numeric_grade(r['response'], q['expected_numeric'], q['unit'], q['numeric_tolerance']))
            counts[grade['status']] += 1
            extraction.append({'question_id': q['id'], 'expected': q['expected_numeric'],
                               'unit': q['unit'], 'response_sha256': response_hash, **grade})
        expected = run['summary']['automatic_numeric_correctness']
        if (counts['correct'], len(numeric)) != (expected['numerator'], expected['denominator']):
            raise ValueError('Published strict score differs from fresh audit')
        receipts.append({'run_id': run['run_id'], 'model': run['model'],
                         'raw_sha256': digest(path), 'attempted': len(raw),
                         'numeric_denominator': len(numeric),
                         'strict_counts': {k: counts[k] for k in ('correct', 'incorrect', 'unparseable', 'generation_error')},
                         'numeric_extractions': extraction})
        prompt_hashes.append([r['prompt_sha256'] for r in raw])
    if prompt_hashes[0] != prompt_hashes[1]:
        raise ValueError('Rendered prompts differ')
    return {'created_at': now(), 'dataset_sha256': digest(ROOT / 'datasets/benchmark_questions.json'),
            'audit_source_sha256': digest(__file__), 'independently_checked_references': len(numeric),
            'rendered_prompt_hashes_equal': True, 'runs': receipts,
            'semantic_rescore_applied': False,
            'scope': 'Strict terminal numeric claims only. No human review or surrounding-prose correctness implied.',
            'conclusion': 'No unparseable numerical answers in this matched pair; no formatting correction is justified.'
                if all(not r['strict_counts']['unparseable'] for r in receipts)
                else 'Unparseable answers require a separate model-blind audit; no semantic score inferred.'}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--baseline', required=True)
    p.add_argument('--candidate', required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        raise FileExistsError('Preserve existing audits; choose a new output path')
    save(args.output, audit(args.baseline, args.candidate))
