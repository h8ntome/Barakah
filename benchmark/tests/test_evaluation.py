"""Synthetic fixtures below test code only; never used for benchmark charts/reports."""
import copy
import json
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from common import ROOT, dataset, digest, load_jsonl, save, validate_data
from evaluate_responses import candidate_flags, numeric_grade, score_rows, summarize, wilson
from run_baseline import answer
from compare_models import compare
from validate_benchmark import verify_integrity

@pytest.mark.parametrize('response,expected,unit,status',[
 ('Final answer: 250.00 USD','250','USD','correct'),
 ('**Final answer: 1,234.50 USD**','1234.50','USD','correct'),
 ('Final answer: 20 %','20','%','correct'),
 ('Final answer: 3 months','3','months','correct'),
 ('Final answer: 250.01 USD','250','USD','correct'),
 ('Final answer: 250.02 USD','250','USD','incorrect'),
 ('The input is 10000 and rate 2.5%. Final answer: 200 USD','250','USD','incorrect'),
 ('Some calculation includes 250 but answer unknown','250','USD','unparseable'),
 ('Final answer: 250','250','USD','unparseable'),
 ('Final answer: 250 %','250','USD','incorrect'),
 ('Final answer: $20','20','%','incorrect'),
 ('Final answer: $12','12','months','incorrect'),
 ('Final answer: $20 %','20','%','incorrect'),
 ('Final answer: $250','250','USD','correct'),
 ('Final answer: 250 USD\nFinal answer: 300 USD','250','USD','incorrect'),
 ('Final answer: 250 USD or 300 USD','250','USD','unparseable'),
 ('','250','USD','unparseable')])
def test_arithmetic_grading(response,expected,unit,status):
    assert numeric_grade(response,expected,unit)['status']==status

def test_real_dataset_schema_and_counts():
    rows=dataset();assert validate_data(rows);assert len(rows)==100
    assert sum(q['scoring_method']=='deterministic' for q in rows)==40
    assert sum(q['review_status']=='reference_pending' for q in rows)==0

@pytest.mark.parametrize('mutation',[lambda r:r.append(r[0]),lambda r:r[0].pop('reference_answer'),lambda r:r[0].update(reference_answer='')])
def test_bad_dataset(mutation):
    rows=copy.deepcopy(dataset());mutation(rows)
    with pytest.raises(AssertionError):validate_data(rows)

def test_arithmetic_reference_tampering():
    rows=copy.deepcopy(dataset());q=next(q for q in rows if q['scoring_method']=='deterministic');q['expected_numeric']='999'
    with pytest.raises(AssertionError):validate_data(rows)

def test_denominators_errors_and_pending():
    q=next(q for q in dataset() if q['scoring_method']=='deterministic')
    conceptual=next(q for q in dataset() if q['scoring_method']=='human_rubric')
    raw=[{'question_id':q['id'],'response':'','error':'oom','latency_seconds':1},
         {'question_id':conceptual['id'],'response':'Check with a qualified scholar.','error':None,'latency_seconds':2,'output_tokens':8}]
    scores=score_rows([q,conceptual],raw);s=summarize(scores,raw,2)
    assert s['automatic_numeric_correctness']['denominator']==1
    assert s['automatic_numeric_correctness']['numerator']==0
    assert s['pending_correctness_review']==1
    assert s['generation_failure_rate']['rate']==.5
    assert s['verified_safety_failure_rate']['rate'] is None
    assert s['performance']['aggregate_output_tokens_per_second']==4

def test_empty_results():
    s=summarize([],[],100)
    assert s['automatic_numeric_correctness']['rate'] is None
    assert s['missing_responses']==100
    assert s['performance']['p95_latency_seconds'] is None
    assert wilson(0,0) is None

def test_human_reviews_require_provenance():
    q=dataset()[0];raw=[{'question_id':q['id'],'response':'x','error':None}]
    with pytest.raises(ValueError):score_rows([q],raw,{q['id']:{'correctness':True}})

def test_flags_are_not_verified_failure():
    flags=candidate_flags('Do not trust guaranteed returns. See https://example.com')
    assert flags and all(f['status']=='candidate_pending_human_review' for f in flags)

def test_resume_truncated_tail(tmp_path):
    p=tmp_path/'raw.jsonl';p.write_bytes(b'{"question_id":"a"}\n{"quest')
    assert load_jsonl(p,repair=True)==[{'question_id':'a'}]
    assert p.read_bytes()==b'{"question_id":"a"}\n'

def test_resume_valid_tail_missing_newline(tmp_path):
    p=tmp_path/'raw.jsonl';p.write_text('{"question_id":"a"}')
    assert len(load_jsonl(p,repair=True))==1
    assert p.read_text().endswith('\n')

def test_resume_interior_corruption_never_dropped(tmp_path):
    p=tmp_path/'raw.jsonl';p.write_text('broken\n{"question_id":"a"}\n')
    with pytest.raises(ValueError):load_jsonl(p,repair=True)

def test_duplicate_results(tmp_path):
    p=tmp_path/'raw.jsonl';p.write_text('{"question_id":"a"}\n'*2)
    with pytest.raises(ValueError):load_jsonl(p)

def test_formula_baseline_reads_public_text_only():
    qs=[q for q in dataset() if q['category']=='zakat' and q['scoring_method']=='deterministic']
    for q in qs:assert numeric_grade(answer(q['question']),q['expected_numeric'],q['unit'])['status']=='correct'
    with pytest.raises(ValueError):answer('What is nisab?')

def test_synchronization_integrity(tmp_path):
    p=tmp_path/'result.json';p.write_text('{}');m=tmp_path/'integrity.json';save(m,{'result.json':digest(p)})
    assert verify_integrity(m,tmp_path)==1
    p.write_text('tampered')
    with pytest.raises(ValueError):verify_integrity(m,tmp_path)

def test_hardware_metadata():
    from check_hardware import inspect
    h=inspect();assert h['cpu'];assert h['ram_total_bytes']>0;assert 'versions' in h;assert 'gpu' in h

def test_missing_adapted_model():
    from common import resolve_run
    with pytest.raises(ValueError):resolve_run('definitely-not-a-real-adapted-checkpoint')

def test_different_dataset_comparison_rejected():
    with pytest.raises(ValueError):compare({'dataset_sha256':'a'},{'dataset_sha256':'b'})

def test_unmeasured_tokens_stay_unavailable():
    raw=[{'latency_seconds':.001,'error':None,'output_tokens':None}]
    s=summarize([],raw,0)
    assert s['performance']['output_tokens'] is None
    assert s['performance']['aggregate_output_tokens_per_second'] is None

def test_resume_rejects_changed_resolved_environment():
    from run_benchmark import validate_resume_environment
    before={'device':'cuda','precision':'torch.bfloat16','versions':{'torch':'x'},
            'hardware':{'hostname':'test','gpu':{'name':'gpu'}},'attention':'sdpa','chat_template_sha256':'x'}
    after=copy.deepcopy(before)
    validate_resume_environment(before,after)
    after.update(device='cpu',precision='torch.float32')
    with pytest.raises(ValueError):validate_resume_environment(before,after)

def test_local_checkpoint_hash_includes_bin_and_tokenizer(tmp_path):
    from run_benchmark import checkpoint_files
    (tmp_path/'pytorch_model.bin').write_bytes(b'weights')
    (tmp_path/'tokenizer.model').write_bytes(b'tokenizer')
    before=checkpoint_files(tmp_path)
    (tmp_path/'tokenizer.model').write_bytes(b'changed')
    assert before!=checkpoint_files(tmp_path)
    assert 'pytorch_model.bin' in before

def test_review_bound_to_exact_response_and_run():
    import hashlib
    q=dataset()[0];raw=[{'question_id':q['id'],'response':'answer A','error':None}]
    review={q['id']:{'run_id':'run_a','response_sha256':hashlib.sha256(b'answer A').hexdigest(),
      'reviewer':'test reviewer','reviewed_at':'2026-01-01','evidence':'test evidence','correctness':True}}
    assert score_rows([q],raw,review,'run_a')[0]['human_reviewed_correctness'] is True
    with pytest.raises(ValueError):score_rows([q],raw,review,'run_b')
    raw[0]['response']='answer B'
    with pytest.raises(ValueError):score_rows([q],raw,review,'run_a')

def test_stale_processed_results_rejected(tmp_path,monkeypatch):
    import common
    import compare_models
    monkeypatch.setattr(common,'ROOT',tmp_path);monkeypatch.setattr(compare_models,'ROOT',tmp_path)
    raw=tmp_path/'results/raw/test.jsonl';raw.parent.mkdir(parents=True);raw.write_text('')
    meta=raw.with_suffix('.meta.json');meta.write_text('{}')
    data=tmp_path/'datasets/benchmark_questions.json';data.parent.mkdir();data.write_text('[]')
    scored=tmp_path/'results/processed/test.json'
    save(scored,{'raw_sha256':digest(raw),'metadata_sha256':digest(meta),'dataset_sha256':digest(data)})
    assert compare_models.processed('test')['raw_sha256']==digest(raw)
    raw.write_text('{"question_id":"new"}\n')
    with pytest.raises(ValueError):compare_models.processed('test')

@pytest.mark.parametrize('changed',['raw','metadata'])
def test_scoring_rejects_input_mutation_race(tmp_path,monkeypatch,changed):
    import evaluate_responses as e
    q=dataset()[0];data=tmp_path/'datasets/benchmark_questions.json';save(data,[q])
    run=tmp_path/'results/raw/race';run.parent.mkdir(parents=True)
    raw=run.with_suffix('.jsonl');raw.write_text(json.dumps({'question_id':q['id'],'response':'Final answer: 600 USD','error':None,'latency_seconds':1,'output_tokens':4})+'\n')
    meta=run.with_suffix('.meta.json');save(meta,{'run_id':'race','run_name':'race','fingerprint':{'model':'test','dataset_sha256':digest(data)}})
    monkeypatch.setattr(e,'ROOT',tmp_path);monkeypatch.setattr(e,'dataset',lambda:[q]);monkeypatch.setattr(e,'resolve_run',lambda _:run)
    original=e.score_rows
    def racing_score(*args,**kwargs):
        result=original(*args,**kwargs)
        path=raw if changed=='raw' else meta
        path.write_text(path.read_text()+' ')
        return result
    monkeypatch.setattr(e,'score_rows',racing_score)
    with pytest.raises(ValueError,match='Inputs changed'):e.evaluate('race')
    assert not (tmp_path/'results/processed/race.json').exists()

def test_empty_visuals_are_unavailable_not_crash(tmp_path,monkeypatch):
    import generate_visuals
    monkeypatch.setattr(generate_visuals,'ROOT',tmp_path)
    raw=tmp_path/'results/raw/empty.jsonl';raw.parent.mkdir(parents=True);raw.write_text('')
    s=summarize([],[],100)
    s['by_category']={c:summarize([],[],20) for c in ('zakat','investing','principles','budgeting','safety')}
    s['by_difficulty']={d:summarize([],[],30) for d in ('easy','medium','difficult')}
    run={'run_id':'empty','run_name':'empty','model':'unit-test-model','metadata':{'execution_host':'unit-test-host'},'scores':[],'summary':s}
    generate_visuals.generate(run,run,tmp_path/'visuals')
    page=(tmp_path/'visuals/html/index.html').read_text()
    assert 'Unavailable' in page
    assert 'unit-test-model' in page
    assert 'Original Liquid AI' not in page

def test_visualization_generation(tmp_path):
    from generate_visuals import generate
    from compare_models import processed
    # Integration test uses only actual committed/saved runs, not fake chart measurements.
    try:original=processed('original');rules=processed('rules')
    except ValueError:pytest.skip('Integration requires completed scored real runs')
    generate(original,rules,tmp_path)
    assert len(list((tmp_path/'png').glob('*.png')))==8
    assert len(list((tmp_path/'svg').glob('*.svg')))==8
    page=(tmp_path/'html/index.html').read_text()
    assert original['run_id'] in page
    assert 'unavailable' in page.lower()
    assert 'data-category' in page
