"""Strict paired analysis of two complete model runs; no rule baseline or inferred reviews."""
import argparse
import csv
import hashlib
import json
import math
import random
from collections import Counter
from common import ROOT, dataset, digest, load_jsonl, now, save
from compare_models import compare, processed


def exact_mcnemar(improved, regressed):
    n = improved + regressed
    return min(1.0, 2 * sum(math.comb(n, k) for k in range(min(improved, regressed)+1)) / 2**n) if n else 1.0


def paired_interval(differences, seed=2026, repetitions=20000):
    if not differences:
        return None
    rng = random.Random(seed)
    means = sorted(sum(rng.choices(differences, k=len(differences)))/len(differences) for _ in range(repetitions))
    return [means[int(.025*repetitions)], means[int(.975*repetitions)-1]]


def cpu_identity(cpu):
    # lscpu includes current clock scaling and vulnerability status; those are telemetry, not identity.
    fields = ('Architecture', 'CPU(s)', 'Vendor ID', 'Model name', 'CPU family', 'Model', 'Stepping', 'Socket(s)', 'Core(s) per socket', 'Thread(s) per core')
    parsed = dict(line.split(':', 1) for line in cpu.splitlines() if ':' in line)
    stable = {k:parsed[k].strip() for k in fields if k in parsed}
    return stable or cpu


def validate_pair(a, b, questions):
    ids = {q['id'] for q in questions}
    for run in (a, b):
        if run['metadata']['status'] != 'completed':
            raise ValueError('Both runs must be completed')
        scores = run['scores']
        if len(scores) != len(ids) or {s['question_id'] for s in scores} != ids:
            raise ValueError('Missing or duplicate scored question IDs')
        if run['metadata'].get('backend') != 'transformers':
            raise ValueError('Only actual Transformer model runs are eligible')
    if a['dataset_sha256'] != b['dataset_sha256']:
        raise ValueError('Different datasets')
    for key in ('system_prompt', 'generation', 'seed', 'enable_thinking', 'warmup_tokens', 'cpu_threads'):
        if a['metadata']['config'][key] != b['metadata']['config'][key]:
            raise ValueError(f'Incompatible inference configuration: {key}')
    for key in ('device', 'precision', 'attention', 'versions'):
        if a['metadata'][key] != b['metadata'][key]:
            raise ValueError(f'Incompatible execution: {key}')
    if a['metadata']['hardware']['hostname'] != b['metadata']['hardware']['hostname']:
        raise ValueError('Incompatible hardware: hostname')
    if cpu_identity(a['metadata']['hardware']['cpu']) != cpu_identity(b['metadata']['hardware']['cpu']):
        raise ValueError('Incompatible hardware: CPU identity')
    if a['metadata']['hardware']['gpu'].get('name') != b['metadata']['hardware']['gpu'].get('name'):
        raise ValueError('Incompatible GPU')


def build(a, b):
    questions = dataset()
    validate_pair(a, b, questions)
    raws = [load_jsonl(ROOT/'results/raw'/f"{r['run_id']}.jsonl") for r in (a, b)]
    maps = [{r['question_id']:r for r in rows} for rows in raws]
    expected = [q['id'] for q in questions]
    for run, rows in zip((a, b), raws):
        if [r['question_id'] for r in rows] != expected:
            raise ValueError('Raw IDs or ordering do not match frozen dataset')
        for q, r in zip(questions, rows):
            if r['run_id'] != run['run_id'] or r['question'] != q['question']:
                raise ValueError('Raw record identity mismatch')
            if not r.get('error') and not r['response'].strip():
                raise ValueError('Empty response mislabeled as successful')
    scores = [{s['question_id']:s for s in r['scores']} for r in (a, b)]
    paired = []
    for q in questions:
        rs = [m[q['id']] for m in maps]
        ss = [s[q['id']] for s in scores]
        numeric = q['scoring_method'] == 'deterministic'
        correct = [s['automatic_correctness'] is True for s in ss]
        outcome = ('both_correct' if all(correct) else 'improved' if correct[1] else 'regressed' if correct[0] else 'both_incorrect') if numeric else 'unreviewed'
        row = {k:q[k] for k in ('category', 'difficulty', 'question')}
        row.update(question_id=q['id'], numeric=numeric, outcome=outcome)
        for label, run, r, s in zip(('baseline', 'barakah'), (a, b), rs, ss):
            row.update({f'{label}_run_id':run['run_id'], f'{label}_response':r['response'],
                        f'{label}_response_sha256':hashlib.sha256(r['response'].encode()).hexdigest(),
                        f'{label}_score':s['automatic_correctness'] if numeric else s['human_reviewed_correctness'],
                        f'{label}_status':s.get('status', s['evaluation_status']),
                        f'{label}_error':r.get('error'), f'{label}_latency_seconds':r.get('latency_seconds'),
                        f'{label}_output_tokens':r.get('output_tokens'), f'{label}_truncated':r.get('truncated')})
        paired.append(row)
    out = compare(a, b)
    counts = Counter(r['outcome'] for r in paired)
    diffs = [int(r['barakah_score'] is True)-int(r['baseline_score'] is True) for r in paired if r['numeric']]
    out.update(created_at=now(), dataset_sha256=a['dataset_sha256'], questions=paired,
               outcome_counts={k:counts[k] for k in ('improved','regressed','both_correct','both_incorrect','unreviewed')},
               statistics={'mcnemar_exact_two_sided_p':exact_mcnemar(counts['improved'], counts['regressed']),
                           'paired_accuracy_delta_bootstrap_95':paired_interval(diffs),
                           'bootstrap_seed':2026, 'bootstrap_repetitions':20000,
                           'note':'Descriptive uncertainty for 40 authored, nonrandom, partly repetitive items; not population-level proof.'},
               performance_comparability='Same host, precision, runtime and protocol; sequential single runs on a shared server, not isolated repeated trials.',
               runs={'baseline':a, 'barakah':b})
    latency_diffs = [r['barakah_latency_seconds']-r['baseline_latency_seconds'] for r in paired if not r['baseline_error'] and not r['barakah_error']]
    out['statistics']['paired_latency_delta_seconds_bootstrap_95'] = paired_interval(latency_diffs)
    out['template_hashes_equal'] = a['metadata']['chat_template_sha256'] == b['metadata']['chat_template_sha256']
    out['input_token_counts_equal'] = all(x['input_tokens'] == y['input_tokens'] for x,y in zip(*raws))
    return out


def export_review(out, folder):
    """Deterministic A/B order, separate identity key; no provisional grades invented."""
    blind, key = [], {}
    for row in out['questions']:
        if row['numeric']:
            continue
        order = ['baseline','barakah']
        if int(hashlib.sha256((out['baseline']+row['question_id']).encode()).hexdigest(),16) % 2:
            order.reverse()
        entry = {'question_id':row['question_id'], 'question':row['question'], 'category':row['category']}
        for label, model in zip(('A','B'), order):
            entry[f'response_{label}'] = row[f'{model}_response']
            key[f"{row['question_id']}:{label}"] = {'run_id':row[f'{model}_run_id'], 'response_sha256':row[f'{model}_response_sha256']}
        blind.append(entry)
    save(folder/'blinded_responses.json', blind)
    save(folder/'review_identity_key.json', key)
    for model in ('baseline','barakah'):
        run = out['runs'][model]
        reviews = {r['question_id']:{'run_id':run['run_id'], 'response_sha256':r[f'{model}_response_sha256'],
                   'reviewer':None, 'reviewed_at':None, 'evidence':None, 'correctness':None,
                   'safety_failure':None, 'hallucination':None, 'factual_accuracy':None,
                   'completeness':None, 'unsupported_assertions':None, 'appropriate_uncertainty':None,
                   'religious_interpretation_differences':None, 'invented_definitive_fatwa':None,
                   'dangerous_financial_claims':None} for r in out['questions'] if not r['numeric']}
        save(folder/f'{model}_review_template.json', {'run_id':run['run_id'], 'dataset_sha256':out['dataset_sha256'], 'reviews':reviews})


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--baseline', required=True); p.add_argument('--candidate', required=True)
    p.add_argument('--output', required=True, type=__import__('pathlib').Path)
    a = p.parse_args()
    if a.output.exists():
        raise FileExistsError('Choose a new analysis output directory; preserve published comparisons')
    out = build(processed(a.baseline), processed(a.candidate))
    save(a.output/'comparison.json', out)
    with (a.output/'questions.csv').open('w',newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(out['questions'][0])); writer.writeheader(); writer.writerows(out['questions'])
    export_review(out, a.output/'review')
    print(json.dumps({k:out[k] for k in ('outcome_counts','statistics','numeric_correctness')},indent=2))


if __name__ == '__main__':
    main()
