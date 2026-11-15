"""Read-only checkpoint compatibility and token-accounting checks; no answer fields enter prompts."""
import argparse
import json
from pathlib import Path
from common import config, dataset, digest, save, now
from checkpoint import verify_manifest


def inspect(a_path,b_path,output):
    from transformers import AutoTokenizer
    from safetensors import safe_open
    manifests=[json.loads(p.read_text()) for p in (a_path,b_path)]
    paths=[verify_manifest(m) for m in manifests]
    tokenizers=[AutoTokenizer.from_pretrained(str(p),trust_remote_code=True) for p in paths]
    cfg=config();token_rows=[]
    for q in dataset():
        messages=[{'role':'system','content':cfg['system_prompt']},{'role':'user','content':q['question']}]
        prompts=[t.apply_chat_template(messages,tokenize=False,add_generation_prompt=True,enable_thinking=False) for t in tokenizers]
        ids=[t(p,add_special_tokens=False)['input_ids'] for t,p in zip(tokenizers,prompts)]
        token_rows.append({'question_id':q['id'],'prompt_equal':prompts[0]==prompts[1], 'token_ids_equal':ids[0]==ids[1],'input_tokens':[len(x) for x in ids]})
    weights=[]
    for p in paths:
        with safe_open(p/'model.safetensors',framework='pt',device='cpu') as f:
            dtypes={f.get_slice(k).get_dtype() for k in f.keys()}
            weights.append({'tensor_dtypes':sorted(dtypes),'stored_parameter_elements':sum(__import__('math').prod(f.get_slice(k).get_shape()) for k in f.keys())})
    result={'timestamp':now(),'models':[{k:m[k] for k in ('model','revision','kind')} for m in manifests],
            'same_files':{n:digest(paths[0]/n)==digest(paths[1]/n) for n in ('modeling_lfm3.py','configuration_lfm3.py','lfm3_conv.py','chat_template.jinja','tokenizer.json','tokenizer_config.json')},
            'tokenization':token_rows,'weights':weights,
            'all_public_prompt_tokens_identical':all(r['token_ids_equal'] for r in token_rows),
            'all_rendered_prompts_identical':all(r['prompt_equal'] for r in token_rows)}
    if Path(output).exists():raise FileExistsError(output)
    save(output,result);print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();inspect(a.baseline,a.candidate,a.output)
