"""Synthetic fixtures exercise safeguards, never populate measured reports."""
import copy
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from checkpoint import checkpoint_kind, resolve_info, verify_manifest
from common import digest
from paired_analysis import exact_mcnemar, paired_interval, validate_pair


def test_full_and_adapter_detection():
    assert checkpoint_kind(['config.json','model.safetensors']) == 'full'
    assert checkpoint_kind(['adapter_config.json','adapter_model.safetensors']) == 'adapter'
    with pytest.raises(ValueError): checkpoint_kind(['adapter_config.json','model.safetensors'])
    with pytest.raises(ValueError): checkpoint_kind(['config.json'])


@pytest.mark.parametrize('sha,revision,valid', [('a'*40,'main',True), ('a'*40,'a'*40,True), ('a'*40,'b'*40,False), ('main','main',False)])
def test_hub_revision_resolution(sha,revision,valid):
    api=SimpleNamespace(model_info=lambda *args,**kw:SimpleNamespace(sha=sha))
    if valid: assert resolve_info(api,'test/model',revision).sha == sha
    else:
        with pytest.raises(ValueError): resolve_info(api,'test/model',revision)


def test_checkpoint_integrity_rejects_changed_weights(tmp_path):
    p=tmp_path/'model.safetensors';p.write_bytes(b'fixture')
    m={'snapshot_path':str(tmp_path),'files':{p.name:{'sha256':digest(p),'bytes':7}}}
    assert verify_manifest(m)==tmp_path
    p.write_bytes(b'changed')
    with pytest.raises(ValueError): verify_manifest(m)


def fixture_run():
    return {'dataset_sha256':'a','scores':[{'question_id':'one'}], 'metadata':{
        'status':'completed','backend':'transformers','config':dict(system_prompt='neutral',generation={'max_new_tokens':384},seed=2026,enable_thinking=False,warmup_tokens=24,cpu_threads=8),
        'device':'cuda','precision':'bf16','attention':'sdpa','versions':{},
        'hardware':{'hostname':'host','cpu':'cpu','gpu':{'name':'gpu'}}}}


def test_strict_pair_requires_complete_unique_coverage():
    a=fixture_run();b=copy.deepcopy(a);q=[{'id':'one'}]
    validate_pair(a,b,q)
    b['scores']*=2
    with pytest.raises(ValueError):validate_pair(a,b,q)
    b['scores']=[]
    with pytest.raises(ValueError):validate_pair(a,b,q)


@pytest.mark.parametrize('mutation', [lambda b:b['metadata']['config'].update(seed=7),lambda b:b['metadata'].update(precision='fp32'),lambda b:b['metadata'].update(backend='rules'),lambda b:b['metadata'].update(status='running'),lambda b:b.update(dataset_sha256='b')])
def test_incompatible_runs_rejected(mutation):
    a=fixture_run();b=copy.deepcopy(a);mutation(b)
    with pytest.raises(ValueError):validate_pair(a,b,[{'id':'one'}])


def test_paired_statistics():
    assert exact_mcnemar(0,0)==1
    assert exact_mcnemar(6,0)==.03125
    assert exact_mcnemar(3,3)==1
    assert paired_interval([]) is None
    assert paired_interval([0]*40,repetitions=100)==[0,0]
    assert paired_interval([1]*40,repetitions=100)==[1,1]


@pytest.mark.parametrize('kind,model,revision,match', [('adapter','fake/model','a'*40,'Adapter cannot'),('full','wrong/model','a'*40,'does not match'),('full','fake/model','b'*40,'does not match')])
def test_runner_rejects_adapter_or_wrong_identity_before_loading(tmp_path,monkeypatch,kind,model,revision,match):
    import run_benchmark
    p=tmp_path/'manifest.json';p.write_text(json.dumps({'model':model,'revision':revision,'kind':kind}))
    monkeypatch.setattr(sys,'argv',['run_benchmark.py','--model','fake/model','--revision','a'*40,'--checkpoint-manifest',str(p)])
    with pytest.raises(ValueError,match=match):run_benchmark.main()


def test_runner_rejects_corrupt_dataset(tmp_path,monkeypatch):
    import run_benchmark
    from common import ROOT
    (tmp_path/'datasets').mkdir()
    for name in ('dataset_manifest.json','benchmark_questions.json'):
        (tmp_path/'datasets'/name).write_bytes((ROOT/'datasets'/name).read_bytes())
    (tmp_path/'datasets/benchmark_questions.json').write_text('[]')
    monkeypatch.setattr(run_benchmark,'ROOT',tmp_path)
    monkeypatch.setattr(sys,'argv',['run_benchmark.py'])
    with pytest.raises(ValueError,match='Frozen dataset'):run_benchmark.main()


def test_runner_rejects_resume_fingerprint(tmp_path,monkeypatch):
    import run_benchmark
    from common import ROOT
    (tmp_path/'datasets').mkdir();(tmp_path/'results/raw').mkdir(parents=True)
    for name in ('dataset_manifest.json','benchmark_questions.json'):
        (tmp_path/'datasets'/name).write_bytes((ROOT/'datasets'/name).read_bytes())
    (tmp_path/'config.yaml').write_bytes((ROOT/'config.yaml').read_bytes())
    (tmp_path/'results/raw/test.meta.json').write_text(json.dumps({'fingerprint':{'wrong':'hash'}}))
    monkeypatch.setattr(run_benchmark,'ROOT',tmp_path)
    monkeypatch.setattr(sys,'argv',['run_benchmark.py','--resume','test'])
    with pytest.raises(ValueError,match='Resume fingerprint mismatch'):run_benchmark.main()


def test_chart_missing_metric_not_zero(tmp_path):
    from paired_visuals import canvas,paired_bars,export
    fig,ax=canvas('Test unavailable values','Synthetic unit fixture, not benchmark evidence')
    paired_bars(ax,['GPU'],[[None],[2]],'GiB')
    assert len(ax.patches)==1
    assert any(t.get_text()=='Unavailable' for t in ax.texts)
    export(fig,'test',tmp_path)
    assert (tmp_path/'png/test.png').exists() and (tmp_path/'svg/test.svg').exists()


@pytest.mark.parametrize('mutation', [lambda r:r.update(run_id='wrong'),lambda r:r.update(revision='wrong'),lambda r:r.update(question='different question'),lambda r:r.update(response='edited answer'),lambda r:r.update(system_prompt_sha256='wrong')])
def test_resume_rejects_conflicting_record(mutation):
    import hashlib
    from run_benchmark import validate_recovered_records
    q={'id':'one','question':'public question'}
    meta={'run_id':'run','fingerprint':{'model':'model','revision':'a'*40},'system_prompt_sha256':'system','chat_template_sha256':'template'}
    r={'question_id':'one','question':q['question'],'run_id':'run','model':'model','revision':'a'*40,'response':'answer','response_sha256':hashlib.sha256(b'answer').hexdigest(),'system_prompt_sha256':'system','chat_template_sha256':'template'}
    validate_recovered_records([r],[q],meta)
    mutation(r)
    with pytest.raises(ValueError):validate_recovered_records([r],[q],meta)


def test_frequency_telemetry_does_not_change_cpu_identity():
    a=fixture_run();b=copy.deepcopy(a)
    a['metadata']['hardware']['cpu']='Model name: AMD test\nCPU(s): 16\nCPU(s) scaling MHz: 46%'
    b['metadata']['hardware']['cpu']='Model name: AMD test\nCPU(s): 16\nCPU(s) scaling MHz: 45%'
    validate_pair(a,b,[{'id':'one'}])
    b['metadata']['hardware']['cpu']='Model name: Other CPU\nCPU(s): 16'
    with pytest.raises(ValueError,match='CPU identity'):validate_pair(a,b,[{'id':'one'}])


def test_all_generation_errors_with_unknown_truncation():
    from common import dataset
    from evaluate_responses import score_rows,summarize
    questions=dataset()
    raw=[{'question_id':q['id'],'response':'','error':'test failure','truncated':None,'latency_seconds':1,'input_tokens':None,'output_tokens':None} for q in questions]
    s=summarize(score_rows(questions,raw),raw,100)
    assert s['automatic_numeric_correctness']['denominator']==40
    assert s['automatic_numeric_correctness']['numerator']==0
    assert s['automatic_generation_errors']==40
    assert s['truncated_responses']==0
    assert s['generation_failure_rate']['rate']==1
    assert s['performance']['mean_latency_seconds'] is None
    assert s['performance']['aggregate_output_tokens_per_second'] is None


def test_measured_paired_artifacts(tmp_path):
    from common import ROOT
    from paired_visuals import generate
    from paired_reports import generate as reports
    p=ROOT/'results/comparisons/20261115/comparison.json'
    if not p.exists():pytest.skip('Requires completed actual matched runs')
    out=json.loads(p.read_text())
    generate(p,tmp_path/'visuals')
    reports(p,tmp_path/'reports')
    assert len(list((tmp_path/'visuals/png').glob('*.png')))==10
    assert len(list((tmp_path/'visuals/svg').glob('*.svg')))==10
    html=(tmp_path/'visuals/html/index.html').read_text()
    assert html.count('<details data-question ')==100
    assert 'id="difficulty"' in html and 'id="outcome"' in html
    assert 'review pending' in (tmp_path/'visuals/svg/10_question_matrix.svg').read_text().lower()
    data=json.loads((tmp_path/'visuals/data/chart_data.json').read_text())
    assert data['01_numerical_accuracy'][1]['numerator']==out['runs']['barakah']['summary']['automatic_numeric_correctness']['numerator']
    report=(tmp_path/'reports/BENCHMARK_REPORT.md').read_text()
    assert out['candidate'] in report and 'No combined correctness is published' in report
    with pytest.raises(FileExistsError):generate(p,tmp_path/'visuals')
    # Missing-performance fixture stays exclusively in pytest's temporary directory.
    from paired_visuals import charts,dashboard
    missing=copy.deepcopy(out)
    for run in missing['runs'].values():
        for key in run['summary']['performance']:
            if key!='note':run['summary']['performance'][key]=None
    for key in ('mean_latency_seconds','aggregate_output_tokens_per_second'):
        missing[key]={k:None for k in ('baseline','candidate','absolute','relative_change')}
    charts(missing,tmp_path/'missing');dashboard(missing,tmp_path/'missing')
    q=tmp_path/'missing.json';q.write_text(json.dumps(missing))
    reports(q,tmp_path/'missing_reports')
    assert 'Unavailable' in (tmp_path/'missing/html/index.html').read_text()
    assert 'Unavailable (no paired measured metric)' in (tmp_path/'missing_reports/BENCHMARK_REPORT.md').read_text()


def test_artifact_manifest_accepts_relative_paths(tmp_path,monkeypatch):
    import validate_paired_artifacts as v
    monkeypatch.setattr(v,'ROOT',tmp_path);monkeypatch.chdir(tmp_path)
    p=Path('artifact.json');p.write_text('{}')
    assert v.artifact_hashes([p])=={'artifact.json':digest(p)}
    assert v.artifact_hashes([p.resolve()])==v.artifact_hashes([p])


def test_dataset_pin():
    assert digest(Path(__file__).resolve().parents[1]/'datasets/benchmark_questions.json')=='c8a9636cc9ad96cbfb1049168227a23e5fc213ce245264be44984667578801fb'
