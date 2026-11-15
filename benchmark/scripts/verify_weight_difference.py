"""CPU-only, post-inference check that candidate tensor values differ from the baseline."""
import argparse
import json
from pathlib import Path
from common import now, save
from checkpoint import verify_manifest


def compare_weights(baseline, candidate, output):
    import torch
    from safetensors import safe_open
    from transformers import AutoTokenizer
    torch.set_num_threads(1)
    manifests=[json.loads(p.read_text()) for p in (baseline,candidate)]
    paths=[verify_manifest(m) for m in manifests]
    changed=[];same=[]
    with safe_open(paths[0]/'model.safetensors',framework='pt',device='cpu') as a, safe_open(paths[1]/'model.safetensors',framework='pt',device='cpu') as b:
        if set(a.keys())!=set(b.keys()):raise ValueError('Different tensor keys')
        for key in a.keys():
            x,y=a.get_tensor(key),b.get_tensor(key)
            if x.shape!=y.shape:raise ValueError(f'Different tensor shape: {key}')
            (same if torch.equal(x,y) else changed).append(key)
    if not changed:raise ValueError('Candidate tensor values equal the original; do not claim adaptation')
    toks=[AutoTokenizer.from_pretrained(str(p),trust_remote_code=True) for p in paths]
    result={'timestamp':now(),'compared_tensor_count':len(changed)+len(same),
            'changed_tensor_count':len(changed),'unchanged_tensor_count':len(same),
            'changed_tensor_names':changed,'unchanged_tensor_names':same,
            'tokenizer_vocabulary_equal':toks[0].get_vocab()==toks[1].get_vocab(),
            'special_tokens_equal':toks[0].special_tokens_map==toks[1].special_tokens_map,
            'method':'torch.equal over every corresponding CPU tensor; no inference; performed after both full runs'}
    if output.exists():raise FileExistsError(output)
    save(output,result);print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--baseline',required=True,type=Path);p.add_argument('--candidate',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();compare_weights(a.baseline,a.candidate,a.output)
