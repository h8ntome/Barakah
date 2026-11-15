"""Immutable one-shot model run. Never resumes or selectively reruns records."""
import argparse
import hashlib
import json
import os
import platform
import random
import sys
import time
import traceback
from pathlib import Path
from benchmark_lib import ROOT, digest, now, save, verify_freeze
# Reuse read-only checkpoint verification and hardware inventory from the copied benchmark.
sys.path.insert(0,str(ROOT.parent/'benchmark/scripts'))
from checkpoint import verify_manifest
from common import versions
from check_hardware import inspect

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--model-key',choices=['base','candidate'],required=True)
    parser.add_argument('--mode',choices=['full','reduced'],required=True)
    args=parser.parse_args()
    verify_freeze()
    cfg=json.loads((ROOT/'inference_config.json').read_text())
    spec=cfg['models'][args.model_key]
    checkpoint_path=ROOT/spec['manifest']
    checkpoint=json.loads(checkpoint_path.read_text())
    if (checkpoint['model'],checkpoint['revision'],checkpoint['kind']) != (spec['model'],spec['revision'],'full'):
        raise ValueError('Checkpoint identity mismatch')
    output=ROOT/'results'/args.model_key
    output.mkdir(exist_ok=False)
    meta=dict(model_key=args.model_key,model=spec['model'],revision=spec['revision'],mode=args.mode,
              started_at=now(),status='loading',freeze_manifest_sha256=digest(ROOT/'freeze_manifest.json'),
              inference_config=cfg,checkpoint_manifest_sha256=digest(checkpoint_path),
              hostname=platform.node(),errors=[],software=versions())
    save(output/'metadata.json',meta)
    started=time.perf_counter()
    try:
        import torch
        import psutil
        from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
        snapshot=verify_manifest(checkpoint)
        if digest(snapshot/'chat_template.jinja') != cfg['template_sha256']:
            raise ValueError('Unexpected chat template')
        base_manifest=json.loads((ROOT/cfg['models']['base']['manifest']).read_text())
        template=(Path(base_manifest['snapshot_path'])/'chat_template.jinja').read_text()
        if hashlib.sha256(template.encode()).hexdigest() != cfg['template_sha256']:
            raise ValueError('Base template changed')
        random.seed(cfg['seed']); torch.manual_seed(cfg['seed'])
        torch.set_num_threads(cfg['cpu_threads'])
        torch.use_deterministic_algorithms(True,warn_only=True)
        torch.backends.cudnn.benchmark=False
        torch.backends.cuda.matmul.allow_tf32=False
        if not torch.cuda.is_available():
            raise RuntimeError('Predeclared CUDA/ROCm device unavailable; no fallback')
        load_start=time.perf_counter()
        tok=AutoTokenizer.from_pretrained(str(snapshot),trust_remote_code=True,local_files_only=True)
        if tok.chat_template != template:
            raise ValueError('Tokenizer template mismatch')
        model=AutoModelForCausalLM.from_pretrained(str(snapshot),trust_remote_code=True,
            local_files_only=True,dtype=getattr(torch,cfg['dtype']),attn_implementation=cfg['attention']).to(cfg['device']).eval()
        torch.cuda.synchronize()
        # Discard checkpoint-specific generation defaults; identical explicit config for both.
        generation=GenerationConfig(**cfg['generation'],pad_token_id=tok.pad_token_id,
                                    eos_token_id=tok.eos_token_id,bos_token_id=tok.bos_token_id)
        meta.update(model_loading_seconds=time.perf_counter()-load_start,hardware=inspect(),
                    precision=str(next(model.parameters()).dtype),parameter_count=sum(p.numel() for p in model.parameters()),
                    effective_generation_config=generation.to_dict(),chat_template_sha256=cfg['template_sha256'],
                    system_prompt_sha256=hashlib.sha256(cfg['system_prompt'].encode()).hexdigest())
        def generate(question,max_tokens=None):
            prompt=tok.apply_chat_template([{'role':'system','content':cfg['system_prompt']},{'role':'user','content':question}],
                     tokenize=False,add_generation_prompt=True,enable_thinking=cfg['enable_thinking'])
            inputs=tok(prompt,add_special_tokens=False,return_tensors='pt').to(cfg['device'])
            torch.cuda.synchronize(); begin=time.perf_counter()
            with torch.inference_mode():
                generated=model.generate(**inputs,generation_config=generation,
                             max_new_tokens=max_tokens or cfg['generation']['max_new_tokens'])[0,inputs.input_ids.shape[1]:]
            torch.cuda.synchronize()
            response=tok.decode(generated,skip_special_tokens=True)
            return dict(response=response,response_sha256=hashlib.sha256(response.encode()).hexdigest(),
                        input_tokens=inputs.input_ids.shape[1],output_tokens=len(generated),
                        output_token_ids=generated.tolist(),truncated=len(generated)==(max_tokens or cfg['generation']['max_new_tokens']),
                        latency_seconds=time.perf_counter()-begin,prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
                        error=None if response.strip() else 'empty_response')
        # Warmup is recorded but not evaluated or inspected before freeze.
        meta['warmup']=generate('What is 2 + 2? Answer briefly.',cfg['warmup_tokens'])
        rows=json.loads((ROOT/'questions.json').read_text())
        subset=[q for q in rows if int(q['id'].rsplit('-',1)[1])<=2]
        rows=subset if args.mode=='reduced' else subset+[q for q in rows if q not in subset]
        meta.update(status='running',question_ids=[q['id'] for q in rows]); save(output/'metadata.json',meta)
        torch.cuda.reset_peak_memory_stats()
        success=0
        with (output/'responses.jsonl').open('x') as f:
            for i,q in enumerate(rows,1):
                item=dict(question_id=q['id'],category=q['category'],timestamp=now())
                begin=time.perf_counter()
                try:
                    item.update(generate(q['question']))
                except Exception as exc:
                    item.update(response='',response_sha256=hashlib.sha256(b'').hexdigest(),error=repr(exc),
                                input_tokens=None,output_tokens=None,truncated=None,latency_seconds=time.perf_counter()-begin)
                    meta['errors'].append(dict(question_id=q['id'],error=repr(exc),traceback=traceback.format_exc()))
                item['process_rss_bytes']=psutil.Process().memory_info().rss
                f.write(json.dumps(item,ensure_ascii=False)+'\n'); f.flush(); os.fsync(f.fileno())
                success+=not bool(item['error'])
                print(f'{args.model_key} {i}/{len(rows)} {q["id"]} tokens={item["output_tokens"]} error={item["error"]}',flush=True)
        meta.update(status='completed',successful_responses=success,generation_failures=len(rows)-success,
                    peak_gpu_allocated_bytes=torch.cuda.max_memory_allocated(),peak_gpu_reserved_bytes=torch.cuda.max_memory_reserved())
    except BaseException as exc:
        meta.update(status='failed',fatal_error=repr(exc),fatal_traceback=traceback.format_exc())
        raise
    finally:
        meta.update(ended_at=now(),total_execution_seconds=time.perf_counter()-started)
        save(output/'metadata.json',meta)

if __name__=='__main__':
    main()
