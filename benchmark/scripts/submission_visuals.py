"""Submission charts from immutable recorded results; never invent missing review scores."""
import json
import re
from collections import Counter
from pathlib import Path
from common import ROOT, digest, save
from paired_visuals import canvas, export, paired_bars, COLORS, LABELS
import matplotlib.pyplot as plt


def load_evidence():
    pf = ROOT.parent / 'personal_finance'
    questions = json.loads((pf / 'questions.json').read_text())
    summary = json.loads((pf / 'results/analysis/summary.json').read_text())
    records = json.loads((pf / 'results/analysis/numeric_records.json').read_text())
    audit = json.loads((ROOT / 'rescue/evidence/original_numeric_audit.json').read_text())
    for key in ('base', 'candidate'):
        model = summary['models'][key]
        if model['status'] != 'completed' or model['observed'] != len(questions) or model['missing_ids']:
            raise ValueError('These full-run charts require both complete runs; do not hide missing coverage')
        eligible = [r for r in records if r['model_key'] == key and r['score'] is not None]
        if len(eligible) != model['numeric_eligible_full'] or sum(r['score'] for r in eligible) != model['correct']:
            raise ValueError('Score records do not match summary')
    if summary['prompt_hash_mismatches']:
        raise ValueError('Mismatched model prompts')
    return questions, summary, records, audit


def test_count(path, word):
    matches = re.findall(r'(\d+) ' + re.escape(word), Path(path).read_text())
    if not matches:
        raise ValueError(f'Missing executed test receipt: {path}')
    return int(matches[-1])


def main():
    questions, summary, records, audit = load_evidence()
    folder = ROOT / 'rescue/visuals'
    if folder.exists():
        raise FileExistsError('Preserve published charts; choose a new release instead')
    keys = ['base', 'candidate']
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 13, 'svg.fonttype': 'none'})
    fig, ax = canvas('Two evaluations. No combined headline score.',
        'A: unchanged original benchmark. B: post-comparison exploratory personal-finance benchmark.\n'
        'Format-sensitive numeric components only; subjective advice scores are unreviewed.\n'
        'Compare models within each benchmark, not accuracy across different benchmarks.')
    metrics = [[r['strict_counts']['correct'], summary['models'][k]['correct']]
               for r, k in zip(audit['runs'], keys)]
    denominators = [audit['runs'][0]['numeric_denominator'], summary['models']['base']['numeric_eligible_full']]
    annotations = [[f'{v}/{denominators[i]} · {100*v/denominators[i]:.1f}%' for i, v in enumerate(row)] for row in metrics]
    paired_bars(ax, ['A · Original', 'B · Personal finance'],
                [[100*v/denominators[i] for i, v in enumerate(row)] for row in metrics],
                'Strict numerical pass rate (%)', annotations)
    ax.set_ylim(0, 125); ax.set_yticks(range(0, 101, 20))
    export(fig, '01_separate_model_evaluations', folder)

    categories = list(dict.fromkeys(q['category'] for q in questions))
    by_id = {q['id']: q for q in questions}
    values, labels = [], []
    counts = []
    for key in keys:
        eligible = [r for r in records if r['model_key'] == key and r['score'] is not None]
        ns = Counter(by_id[r['question_id']]['category'] for r in eligible)
        correct = Counter(by_id[r['question_id']]['category'] for r in eligible if r['score'] == 1)
        counts.append({c: {'correct': correct[c], 'n': ns[c]} for c in categories})
        values.append([100*correct[c]/ns[c] if ns[c] else None for c in categories])
        labels.append([f'{correct[c]}/{ns[c]}' for c in categories])
    fig, ax = canvas('Personal finance: numerical components by category',
        'Small category denominators; this is not a category-wide advice-quality rating.\n'
        'All 50 scenarios per model need independent five-dimension human review.')
    paired_bars(ax, [c.title() for c in categories], values, 'Strict numeric-field pass rate (%)', labels)
    ax.set_ylim(0, 125); ax.set_yticks(range(0, 101, 20))
    export(fig, '02_personal_finance_categories', folder)

    evidence = ROOT / 'rescue/evidence'
    backend = test_count(evidence / 'backend_tests.log', 'passed')
    skipped = test_count(evidence / 'backend_tests.log', 'skipped')
    benchmark = test_count(evidence / 'benchmark_tests.log', 'passed')
    calculations = test_count(evidence / 'calculation_tests.log', 'passed')
    front_text = (evidence / 'frontend_tests.log').read_text()
    frontend = int(re.findall(r'pass (\d+)', front_text)[-1])
    public_text = (evidence / 'public_demo_verified.log').read_text()
    public = json.loads(public_text[public_text.index('{'):])
    if public['failed'] or 'built in' not in (evidence / 'frontend_build.log').read_text():
        raise ValueError('Application check/build did not pass')
    app = {'backend_passed': backend, 'backend_skipped': skipped, 'frontend_passed': frontend,
           'original_benchmark_tests_passed': benchmark, 'public_browser_checks': public['passed'],
           'calculation_regressions_passed': calculations}
    fig, ax = canvas('Application reliability is a separate engineering result',
        'Decimal accounting, not model-assisted arithmetic. Public chat is explicitly disconnected.\n'
        'Test passes do not establish advice quality, religious correctness, production security or competition eligibility.')
    ax.axis('off')
    lines = [f'Backend API tests                 {backend} passed · {skipped} skipped',
             f'Frontend tests                     {frontend} passed · build passed',
             f'Evaluation tooling tests         {benchmark} passed',
             f'Fresh public browser journey   {public["passed"]} checks passed',
             f'Calculation regressions          {calculations} passed · post-observation fixtures',
             'Independent advice review       Not completed · no ratings invented']
    for i, line in enumerate(lines):
        ax.text(.02, .92-i*.15, line, transform=ax.transAxes, fontsize=20, color=COLORS[i%2])
    export(fig, '03_application_reliability', folder)
    save(folder / 'chart_data.json', {'models': LABELS, 'comparison_correct': metrics,
         'comparison_denominators': denominators, 'personal_finance_categories': counts, 'application': app,
         'source_sha256': {'personal_summary': digest(ROOT.parent/'personal_finance/results/analysis/summary.json'),
                           'original_audit': digest(evidence/'original_numeric_audit.json')}})


if __name__ == '__main__':
    main()
