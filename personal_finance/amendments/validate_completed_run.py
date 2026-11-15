"""Independent stdlib final artifact checks; not a subjective evaluator."""
import hashlib
import json
import re
import sys
from decimal import Decimal
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from benchmark_lib import digest, now, verify_freeze

def main():
    release=verify_freeze()
    questions=json.loads((ROOT/'questions.json').read_text())
    cfg=json.loads((ROOT/'inference_config.json').read_text())
    metas={key:json.loads((ROOT/'results'/key/'metadata.json').read_text()) for key in cfg['models']}
    rows={key:[json.loads(x) for x in (ROOT/'results'/key/'responses.jsonl').read_text().splitlines()] for key in cfg['models']}
    expected=[q['id'] for q in questions if int(q['id'].rsplit('-',1)[1])<=2]+[q['id'] for q in questions if int(q['id'].rsplit('-',1)[1])>2]
    checks={}
    checks['original_freeze_integrity']=True
    checks['full_completed_50_each']=all(m['status']=='completed' and len(rows[k])==50 for k,m in metas.items())
    checks['ids_and_order_match_predeclared']=all([r['question_id'] for r in rr]==expected for rr in rows.values())
    checks['checkpoint_revisions_match']=all(metas[k]['revision']==s['revision'] for k,s in cfg['models'].items())
    parity={field:metas['base'].get(field)==metas['candidate'].get(field) for field in ['software','precision','hostname','effective_generation_config','chat_template_sha256','system_prompt_sha256','inference_config']}
    parity['gpu_name']=metas['base']['hardware']['gpu']['name']==metas['candidate']['hardware']['gpu']['name']
    checks['metadata_parity']=all(parity.values())
    checks['all_prompt_hashes_equal']=all(a['prompt_sha256']==b['prompt_sha256'] for a,b in zip(rows['base'],rows['candidate']))
    checks['response_hashes_valid']=all(hashlib.sha256(r['response'].encode()).hexdigest()==r['response_sha256'] for rr in rows.values() for r in rr)
    tokenizer=json.loads((ROOT/'results/tokenizer_compatibility.json').read_text())
    resolved=json.loads((ROOT/'results/resolved_generation_compatibility.json').read_text())
    checks['input_ids_identical_all50']=tokenizer['count']==50 and tokenizer['all_input_ids_equal']
    checks['resolved_generation_configs_identical_all50']=resolved['count']==50 and resolved['all_resolved_configs_equal']
    tby={r['question_id']:r for r in tokenizer['records']}
    checks['actual_prompt_tokens_match_supplement']=all(r['input_tokens']==tby[r['question_id']]['input_tokens'][k] and r['prompt_sha256']==tby[r['question_id']]['prompt_sha256'][k] for k,rr in rows.items() for r in rr)
    checks['freeze_precedes_both_runs']=all(release['frozen_at']<m['started_at'] for m in metas.values())
    by_id={k:{r['question_id']:r for r in rr} for k,rr in rows.items()}
    summary=json.loads((ROOT/'results/analysis/summary.json').read_text())
    independent={}
    for key in cfg['models']:
        correct=0
        for q in questions:
            if not q['numeric']: continue
            record=by_id[key][q['id']]
            text=record['response']
            lines=[x.strip() for x in text.splitlines() if x.strip()]
            if record['error'] or len(lines)<2 or text.count('ANSWER_AMOUNT:')!=1 or text.count('ANSWER_UNIT:')!=1: continue
            m=re.fullmatch('ANSWER_AMOUNT: ([+-]?[0-9]+\\.[0-9]{2})',lines[-2])
            if m and lines[-1]=='ANSWER_UNIT: '+q['numeric']['unit']:
                correct+=abs(Decimal(m.group(1))-Decimal(q['numeric']['expected']))<=Decimal('0.01')
        independent[key]=correct
    checks['independent_numeric_counts_agree']=all(independent[k]==summary['models'][k]['correct'] for k in independent)
    packets=json.loads((ROOT/'results/analysis/reviewer_packets_canonical/pairs.json').read_text())
    mapping={p['packet_id']:p for p in json.loads((ROOT/'results/analysis/private_mapping/identity_mapping.json').read_text())}
    dimensions=set(json.loads((ROOT/'amendments/canonical_parent_rubric.json').read_text())['dimensions'])
    checks['canonical_packets_50_unique']=len(packets)==50 and len({p['question_id'] for p in packets})==50
    checks['human_scores_all_null']=all(set(s)==dimensions and all(v is None for v in s.values()) for p in packets for s in p['scores'].values())
    checks['packets_match_separate_mapping']=all(set(mapping[p['packet_id']][label] for label in ['A','B'])=={'base','candidate'} and all(p['responses'][label]==by_id[mapping[p['packet_id']][label]][p['question_id']]['response'] for label in ['A','B']) for p in packets)
    checks['mapping_not_inside_packets']=not (ROOT/'results/analysis/reviewer_packets_canonical/identity_mapping.json').exists()
    identity_flags=[dict(packet_id=p['packet_id'],label=label) for p in packets for label,text in p['responses'].items() if re.search(r'(?i)barakah|h8notme|liquidai|lfm3',text)]
    result=dict(validated_at=now(),script_sha256=digest(__file__),all_checks_passed=all(checks.values()),checks=checks,
                metadata_parity_fields=parity,independent_numeric_correct=independent,
                explicit_model_identity_text_flags=identity_flags,
                canonical_rubric_sha256=digest(ROOT/'amendments/canonical_parent_rubric.json'))
    with (ROOT/'results/final_validation.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result,indent=2))
    if not result['all_checks_passed']:raise SystemExit(1)

if __name__=='__main__':main()
