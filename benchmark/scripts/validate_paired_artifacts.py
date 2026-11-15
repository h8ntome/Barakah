"""Validate paired measurements, chart data, rendered links and a new artifact manifest."""
import argparse
import json
import re
import struct
from pathlib import Path
from common import ROOT, digest, load_jsonl, save
from compare_models import processed
from paired_analysis import build
from validate_benchmark import verify_integrity


def validate(comparison, visuals):
    out=json.loads(comparison.read_text())
    a=processed(out['baseline']);b=processed(out['candidate']);actual=build(a,b)
    for key in ('questions','outcome_counts','statistics','numeric_correctness'):
        if out[key]!=actual[key]:raise ValueError(f'Paired data mismatch: {key}')
    data=json.loads((visuals/'data/chart_data.json').read_text())
    if len(data)!=10:raise ValueError('Expected ten chart datasets')
    if data['01_numerical_accuracy']!=[r['summary']['automatic_numeric_correctness'] for r in (a,b)]:
        raise ValueError('Chart accuracy differs from scores')
    for i,r in enumerate((a,b)):
        perf=r['summary']['performance']
        if data['05_latency']['seconds'][i]!=[perf[k] for k in data['05_latency']['fields']]:raise ValueError('Chart latency mismatch')
        if data['06_throughput']['tokens_per_second'][i]!=perf['aggregate_output_tokens_per_second']:raise ValueError('Chart throughput mismatch')
    for chart,field in (('02_category_accuracy','category'),('03_difficulty_accuracy','difficulty')):
        for i,r in enumerate((a,b)):
            expected=[r['summary']['by_'+field][k]['automatic_numeric_correctness'] for k in data[chart]['labels']]
            if data[chart]['percent'][i]!=[100*m['rate'] if m['rate'] is not None else None for m in expected]:raise ValueError('Grouped chart accuracy mismatch')
    for i,r in enumerate((a,b)):
        expected=[r['metadata'].get(k)/1024**3 if r['metadata'].get(k) is not None else None for k in data['07_resources']['fields']]
        if data['07_resources']['GiB'][i]!=expected:raise ValueError('Resource chart mismatch')
    if data['04_paired_outcomes']!={k:actual['outcome_counts'][k] for k in ('improved','regressed','both_correct','both_incorrect')}:raise ValueError('Paired outcomes mismatch')
    if sum(data['04_paired_outcomes'].values())!=40:raise ValueError('Paired outcome denominator mismatch')
    if sum(data['08_coverage']['numeric'])!=40 or sum(data['08_coverage']['pending'])!=60:raise ValueError('Coverage mismatch')
    if data['10_question_matrix']!=[{'id':r['question_id'],'outcome':r['outcome']} for r in actual['questions']]:raise ValueError('Matrix outcomes mismatch')
    for ext in ('png','svg'):
        files=list((visuals/ext).glob('*.'+ext))
        if len(files)!=10:raise ValueError(f'Expected ten {ext} charts')
        if ext=='png':
            for f in files:
                width,height=struct.unpack('>II',f.read_bytes()[16:24])
                if width<1920 or height<1080:raise ValueError(f'Insufficient chart resolution: {f}')
    page=(visuals/'html/index.html').read_text()
    if len(re.findall(r'<details data-question ',page))!=100:raise ValueError('Dashboard question coverage')
    for f in (visuals/'html').glob('*.html'):
        for rel in re.findall(r'(?:href|src)="([^"#]+)"',f.read_text()):
            if not rel.startswith(('http:','https:','data:')) and not (f.parent/rel).exists():raise ValueError(f'Broken dashboard link: {rel}')
    archived=ROOT/'results/hardware/matched_run_benchmark.py'
    for r in (a,b):
        if r['metadata']['fingerprint']['runner_sha256']!=digest(archived):raise ValueError('Evaluated source snapshot mismatch')
    return {'status':'passed','runs':[a['run_id'],b['run_id']],'raw_records':[100,100],
            'numerical_denominator_per_model':40,'conceptual_pending_per_model':60,
            'charts':{'png':10,'svg':10,'minimum_dimensions':[1920,1080]},
            'checks':['processed raw/metadata provenance','paired question data','paired statistics','chart accuracy/latency/throughput/coverage','dashboard coverage and local links','evaluated source hash']}


def artifact_hashes(paths):
    return {str(f.resolve().relative_to(ROOT.resolve())):digest(f) for f in sorted(set(paths))}


def main():
    p=argparse.ArgumentParser();p.add_argument('--comparison',required=True,type=Path);p.add_argument('--visuals',required=True,type=Path)
    p.add_argument('--write-manifest',type=Path);p.add_argument('--verify-manifest',type=Path)
    a=p.parse_args();result=validate(a.comparison,a.visuals)
    if a.verify_manifest:result['manifest_files_verified']=verify_integrity(a.verify_manifest,ROOT)
    if a.write_manifest:
        if a.write_manifest.exists():raise FileExistsError(a.write_manifest)
        out=json.loads(a.comparison.read_text());runs=[out['baseline'],out['candidate']]
        paths=[]
        for run in runs:
            paths += [ROOT/'results/raw'/f'{run}.jsonl',ROOT/'results/raw'/f'{run}.meta.json',ROOT/'results/processed'/f'{run}.json']
        for folder in (a.comparison.parent,a.visuals,ROOT/'reports/20261115',ROOT/'scripts',ROOT/'tests'):
            paths.extend(f for f in folder.rglob('*') if f.is_file() and '__pycache__' not in f.parts and '.pytest_cache' not in f.parts)
        paths.extend(f for f in (ROOT/'results/hardware').glob('*') if f.is_file() and f.name in ('original_checkpoint.json','barakah1_checkpoint.json','checkpoint_compatibility.json','matched_run_benchmark.py','matched_inference_environment.txt','matched_analysis_environment.txt','workload_samples.jsonl','workload_samples_candidate.jsonl','remote_matched_integrity.json','weight_difference.json'))
        remote_manifest=ROOT/'results/hardware/remote_matched_integrity.json'
        if remote_manifest.exists():
            verify_integrity(remote_manifest,ROOT)
            paths.extend(ROOT/rel for rel in json.loads(remote_manifest.read_text()))
        paths.extend((ROOT/'results/comparisons/20261115_scoring_archive').glob('*.json'))
        paths += [ROOT/'README.md',ROOT/'config.yaml',ROOT/'datasets/benchmark_questions.json',ROOT/'datasets/dataset_manifest.json',ROOT/'results/hardware/historical_baseline_audit_20261115.json',ROOT/'results/hardware/session_workload_20261115.txt']
        save(a.write_manifest,artifact_hashes(paths))
        result['manifest_files_verified']=verify_integrity(a.write_manifest,ROOT)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
