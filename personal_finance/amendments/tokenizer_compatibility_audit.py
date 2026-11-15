"""Supplemental no-generation token-ID parity audit; frozen inference is unchanged."""
import hashlib
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from benchmark_lib import digest, now, verify_freeze

def main():
    verify_freeze()
    from transformers import AutoTokenizer
    cfg=json.loads((ROOT/'inference_config.json').read_text())
    questions=json.loads((ROOT/'questions.json').read_text())
    tokenizers={}
    for key,spec in cfg['models'].items():
        manifest=json.loads((ROOT/spec['manifest']).read_text())
        snapshot=Path(manifest['snapshot_path'])
        for name in ['tokenizer.json','tokenizer_config.json','chat_template.jinja']:
            if digest(snapshot/name)!=manifest['files'][name]['sha256']:
                raise ValueError(f'Tokenizer artifact changed: {key} {name}')
        tokenizers[key]=AutoTokenizer.from_pretrained(str(snapshot),trust_remote_code=True,local_files_only=True)
    records=[]
    for q in questions:
        inputs={}; prompts={}
        for key,tok in tokenizers.items():
            prompt=tok.apply_chat_template([{'role':'system','content':cfg['system_prompt']},{'role':'user','content':q['question']}],
                tokenize=False,add_generation_prompt=True,enable_thinking=cfg['enable_thinking'])
            prompts[key]=hashlib.sha256(prompt.encode()).hexdigest()
            inputs[key]=tok(prompt,add_special_tokens=False)['input_ids']
        records.append(dict(question_id=q['id'],prompt_sha256=prompts,input_ids_equal=inputs['base']==inputs['candidate'],
                            input_ids_sha256={k:hashlib.sha256(json.dumps(ids,separators=(',',':')).encode()).hexdigest() for k,ids in inputs.items()},
                            input_tokens={k:len(ids) for k,ids in inputs.items()}))
    out=dict(audited_at=now(),script_sha256=digest(__file__),freeze_manifest_sha256=digest(ROOT/'freeze_manifest.json'),
             generation_performed=False,count=len(records),all_input_ids_equal=all(r['input_ids_equal'] for r in records),records=records)
    with (ROOT/'results/tokenizer_compatibility.json').open('x') as f:
        json.dump(out,f,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in out.items() if k!='records'},indent=2))
    if not out['all_input_ids_equal']: raise SystemExit(1)

if __name__=='__main__': main()
