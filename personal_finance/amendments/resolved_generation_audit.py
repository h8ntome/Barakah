"""No-generation audit of installed Transformers config merge and length resolution."""
import hashlib
import inspect
import json
import sys
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from benchmark_lib import digest, now, verify_freeze

def main():
    verify_freeze()
    from transformers import GenerationConfig
    from transformers.generation.utils import GenerationMixin
    cfg=json.loads((ROOT/'inference_config.json').read_text())
    tokens=json.loads((ROOT/'results/tokenizer_compatibility.json').read_text())
    prepared={}; records=[]; source_configs={}
    for key,spec in cfg['models'].items():
        manifest=json.loads((ROOT/spec['manifest']).read_text())
        snapshot=Path(manifest['snapshot_path'])
        if digest(snapshot/'generation_config.json') != manifest['files']['generation_config.json']['sha256']:
            raise ValueError('Checkpoint generation config changed')
        source=GenerationConfig.from_pretrained(str(snapshot),local_files_only=True)
        meta=json.loads((ROOT/'results'/key/'metadata.json').read_text())
        declared=GenerationConfig.from_dict(meta['effective_generation_config'])
        dummy=SimpleNamespace(generation_config=source)
        merged,kwargs=GenerationMixin._prepare_generation_config(dummy,declared,max_new_tokens=cfg['generation']['max_new_tokens'])
        source_configs[key]=source.to_dict()
        prepared[key]=dict(merged_before_length=merged.to_dict(),model_kwargs=kwargs)
    for row in tokens['records']:
        resolved={}
        for key in cfg['models']:
            merged=GenerationConfig.from_dict(prepared[key]['merged_before_length'])
            resolved[key]=GenerationMixin._prepare_generated_length(SimpleNamespace(),merged,
                has_default_max_length=False,has_default_min_length=True,model_input_name='input_ids',
                input_ids_length=row['input_tokens'][key],inputs_tensor=None).to_dict()
        differences={k:{model:config.get(k) for model,config in resolved.items()} for k in set(resolved['base'])|set(resolved['candidate']) if resolved['base'].get(k)!=resolved['candidate'].get(k)}
        records.append(dict(question_id=row['question_id'],equal=not differences,differences=differences,
            resolved_config_sha256={k:hashlib.sha256(json.dumps(v,sort_keys=True).encode()).hexdigest() for k,v in resolved.items()},
            resolved_max_length={k:v['max_length'] for k,v in resolved.items()}))
    merge_differences={k:{model:item['merged_before_length'].get(k) for model,item in prepared.items()} for k in set(prepared['base']['merged_before_length'])|set(prepared['candidate']['merged_before_length']) if prepared['base']['merged_before_length'].get(k)!=prepared['candidate']['merged_before_length'].get(k)}
    output=dict(audited_at=now(),script_sha256=digest(__file__),generation_performed=False,weights_loaded=False,
        method='Invoke installed GenerationMixin._prepare_generation_config and _prepare_generated_length on checkpoint generation configs and frozen declared configs; no model forward pass. Both have max_new_tokens=384, so input length determines operative max_length.',
        caveat='Frozen metadata field effective_generation_config is pre-merge. This supplement resolves inherited defaults; special-token tensors and backend kernels are not replayed.',
        transformer_methods_sha256={name:hashlib.sha256(inspect.getsource(getattr(GenerationMixin,name)).encode()).hexdigest() for name in ['_prepare_generation_config','_prepare_generated_length']},
        checkpoint_generation_configs=source_configs,prepared=prepared,pre_length_differences=merge_differences,
        count=len(records),all_resolved_configs_equal=all(r['equal'] for r in records),records=records)
    with (ROOT/'results/resolved_generation_compatibility.json').open('x') as f:
        json.dump(output,f,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in output.items() if k not in ['checkpoint_generation_configs','prepared','records']},indent=2))
    if not output['all_resolved_configs_equal']: raise SystemExit(1)

if __name__=='__main__': main()
