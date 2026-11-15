"""Post-freeze numeric summaries and identity-separated randomized human packets."""
import collections
import json
import random
from benchmark_lib import ROOT, digest, now, save, score_numeric, verify_freeze

def load_run(key, questions):
    directory=ROOT/'results'/key
    meta=json.loads((directory/'metadata.json').read_text())
    if meta['freeze_manifest_sha256'] != digest(ROOT/'freeze_manifest.json'):
        raise ValueError('Run freeze differs')
    rows=[json.loads(line) for line in (directory/'responses.jsonl').read_text().splitlines()]
    if len({r['question_id'] for r in rows})!=len(rows):
        raise ValueError('Duplicate response IDs')
    expected={q['id'] for q in questions}
    if not {r['question_id'] for r in rows}<=expected:
        raise ValueError('Unknown response ID')
    for r in rows:
        if digest_text(r['response']) != r['response_sha256']:
            raise ValueError('Response checksum mismatch')
    return meta,{r['question_id']:r for r in rows}

def digest_text(text):
    import hashlib
    return hashlib.sha256(text.encode()).hexdigest()

def main():
    verify_freeze()
    questions=json.loads((ROOT/'questions.json').read_text())
    cfg=json.loads((ROOT/'inference_config.json').read_text())
    runs={k:load_run(k,questions) for k in ('base','candidate')}
    summary=dict(created_at=now(),metric='Limited labeled numeric extraction only; not subjective advice correctness',
                 human_review_status='not_performed',subjective_scores=None,models={})
    numeric_records=[]
    for key,(meta,records) in runs.items():
        scores=[]
        for q in questions:
            if q['id'] in records:
                result=score_numeric(q,records[q['id']])
                numeric_records.append(dict(model_key=key,question_id=q['id'],**result))
                if q['numeric'] is not None:
                    scores.append(result)
        summary['models'][key]=dict(status=meta['status'],observed=len(records),expected=len(questions),
            missing_ids=[q['id'] for q in questions if q['id'] not in records],
            numeric_status_counts=dict(collections.Counter(s['status'] for s in scores)),
            numeric_eligible_observed=len(scores),numeric_eligible_full=sum(q['numeric'] is not None for q in questions),
            correct=sum(s['score']==1 for s in scores),
            inference_errors=sum(bool(r.get('error')) for r in records.values()),
            truncated=sum(r.get('truncated') is True for r in records.values()),
            total_output_tokens=sum(r.get('output_tokens') or 0 for r in records.values()),
            model_loading_seconds=meta.get('model_loading_seconds'),total_execution_seconds=meta['total_execution_seconds'])
    paired=[q for q in questions if all(q['id'] in records for _,records in runs.values())]
    prompt_mismatches=[q['id'] for q in paired if runs['base'][1][q['id']].get('prompt_sha256')!=runs['candidate'][1][q['id']].get('prompt_sha256')]
    summary.update(paired_count=len(paired),prompt_hash_mismatches=prompt_mismatches)
    both=base_only=candidate_only=neither=0
    for q in paired:
        if q['numeric'] is None: continue
        a=score_numeric(q,runs['base'][1][q['id']])['score']==1
        b=score_numeric(q,runs['candidate'][1][q['id']])['score']==1
        both+=a and b; base_only+=a and not b; candidate_only+=b and not a; neither+=not a and not b
    summary['paired_numeric']=dict(both_correct=both,base_only_correct=base_only,candidate_only_correct=candidate_only,neither_correct=neither)
    out=ROOT/'results/analysis'; out.mkdir(exist_ok=False)
    save(out/'summary.json',summary); save(out/'numeric_records.json',numeric_records)
    # Packets omit run metadata/model names. Text itself is not edited to conceal self-identification.
    rng=random.Random(cfg['review_randomization_seed']); rng.shuffle(paired)
    dimensions=list(json.loads((ROOT/'rubric.json').read_text())['dimensions'])
    packets=[]; mapping=[]
    for i,q in enumerate(paired,1):
        keys=['base','candidate']; rng.shuffle(keys)
        packet_id=f'pair-{i:03}'
        packets.append(dict(packet_id=packet_id,question_id=q['id'],category=q['category'],question=q['question'],
            human_reference=q['human_reference'],
            responses={label:runs[key][1][q['id']]['response'] for label,key in zip(('A','B'),keys)},
            scores={label:{d:None for d in dimensions} for label in ('A','B')},
            reviewer_id=None,reviewed_at=None,evidence_notes=None,critical_safety_issue=None,preference=None))
        mapping.append(dict(packet_id=packet_id,question_id=q['id'],A=keys[0],B=keys[1]))
    review=out/'reviewer_packets'; review.mkdir()
    save(review/'pairs.json',packets)
    save(review/'rubric.json',json.loads((ROOT/'rubric.json').read_text()))
    private=out/'private_mapping'; private.mkdir(mode=0o700)
    save(private/'identity_mapping.json',mapping)
    (private/'identity_mapping.json').chmod(0o600)
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
