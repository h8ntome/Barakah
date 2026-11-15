"""Serial greedy inference with durable per-question writes and strict resume fingerprints."""
import argparse
import hashlib
import json
import os
import re
import time
from pathlib import Path
from common import ROOT, append, config, dataset, digest, load_jsonl, now, save, validate_data, versions

def checkpoint_files(path):
    return {str(f.relative_to(path)): digest(f) for f in sorted(Path(path).rglob("*"))
            if f.is_file() and ".git" not in f.relative_to(path).parts}

def execution_signature(meta):
    return {"device":meta["device"], "precision":meta["precision"], "versions":meta["versions"],
            "hostname":meta["hardware"]["hostname"], "gpu":meta["hardware"]["gpu"].get("name"),
            "attention":meta["attention"], "chat_template_sha256":meta["chat_template_sha256"]}

def validate_resume_environment(previous, current):
    if execution_signature(previous) != execution_signature(current):
        raise ValueError("Resolved resume environment changed (device, precision, host, runtime or template); start a new run")

def main():
    cfg = config()
    p = argparse.ArgumentParser()
    p.add_argument("--model", default=cfg["model"])
    p.add_argument("--revision", default=None)
    p.add_argument("--run-name", default="original")
    p.add_argument("--resume", help="Exact existing run ID")
    p.add_argument("--device", default=cfg["device"])
    p.add_argument("--smoke-only", action="store_true")
    p.add_argument("--checkpoint-manifest", type=Path, help="Verified immutable snapshot inventory")
    args = p.parse_args()
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", args.run_name):
        p.error("run-name must contain only letters, digits, underscores or hyphens")
    rows = dataset(cfg)
    validate_data(rows)
    release = json.loads((ROOT/'datasets/dataset_manifest.json').read_text())
    if digest(ROOT/cfg['dataset']) != release['sha256']:
        raise ValueError('Frozen dataset checksum mismatch')
    checkpoint = None
    model_source = args.model
    if args.checkpoint_manifest:
        from checkpoint import verify_manifest
        checkpoint = json.loads(args.checkpoint_manifest.read_text())
        if checkpoint['model'] != args.model or checkpoint['revision'] != args.revision:
            raise ValueError('Checkpoint manifest does not match model/revision')
        if checkpoint['kind'] != 'full':
            raise ValueError('Adapter cannot be loaded as a full model; explicit compatible PEFT base required')
        model_source = str(verify_manifest(checkpoint))
    if any(q["review_status"] == "reference_pending" for q in rows):
        raise ValueError("Unverified references in dataset; resolve before evaluation")
    revision = args.revision or (cfg["revision"] if args.model == cfg["model"] else None)
    if not Path(args.model).is_dir() and (not revision or not re.fullmatch(r"[a-f0-9]{40}",revision)):
        from huggingface_hub import HfApi
        revision = HfApi().model_info(args.model, revision=revision or "main").sha
    run_id = args.resume or args.run_name + "_" + now().replace(":", "").replace("-", "").replace(".", "")
    if not re.fullmatch(r"[a-zA-Z0-9_+T-]+", run_id):
        raise ValueError("Invalid run ID")
    raw = ROOT / "results/raw" / (run_id + ".jsonl")
    meta_path = raw.with_suffix(".meta.json")
    fingerprint = {"model": args.model, "revision": revision, "dataset_sha256": digest(ROOT/cfg["dataset"]),
                   "config_sha256": digest(ROOT/"config.yaml"), "device_requested": args.device}
    if checkpoint:
        fingerprint['checkpoint_manifest_sha256'] = digest(args.checkpoint_manifest)
    fingerprint['runner_sha256'] = digest(Path(__file__))
    if args.resume:
        old = json.loads(meta_path.read_text())
        if old["fingerprint"] != fingerprint:
            raise ValueError("Resume fingerprint mismatch: dataset/model/config/device changed")
        if revision is None and not Path(args.model).is_dir():
            raise ValueError("Resuming a remote candidate requires --revision pinned to its commit")
        meta = old
    else:
        meta = {"run_id": run_id, "run_name": args.run_name, "fingerprint": fingerprint,
                "started_at": now(), "segments": [], "status": "loading", "execution_host": "server2" if __import__("platform").node()=="server2" else "local"}
    raw.parent.mkdir(parents=True, exist_ok=True)
    if not args.resume and (raw.exists() or meta_path.exists()):
        raise FileExistsError('Never overwrite an existing run')
    lock = raw.with_suffix(".lock")
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.write(fd, str(os.getpid()).encode())
    os.close(fd)
    session_start = time.perf_counter()
    segment_info = {}
    try:
        done = load_jsonl(raw, repair=True)
        if not {r["question_id"] for r in done} <= {q["id"] for q in rows}:
            raise ValueError("Unknown recovered question IDs")
        save(meta_path, meta)
        import random
        import torch
        import psutil
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from check_hardware import inspect
        random.seed(cfg["seed"])
        torch.manual_seed(cfg["seed"])
        torch.set_num_threads(cfg["cpu_threads"])
        torch.use_deterministic_algorithms(True, warn_only=True)
        if torch.cuda.is_available():
            torch.backends.cudnn.benchmark = False
            torch.backends.cuda.matmul.allow_tf32 = False
        device = args.device
        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
        dtype = getattr(torch, cfg["dtype"])
        if device == "cpu":
            dtype = torch.float32
        if Path(args.model).is_dir():
            local_fingerprint = checkpoint_files(Path(args.model))
            if args.resume and old.get("local_checkpoint_files") != local_fingerprint:
                raise ValueError("Local checkpoint changed since initial run")
            meta["local_checkpoint_files"] = local_fingerprint
        load_start = time.perf_counter()
        tok = AutoTokenizer.from_pretrained(model_source, revision=revision, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(model_source, revision=revision, code_revision=revision,
                    trust_remote_code=True, dtype=dtype, attn_implementation=cfg["attention"]).to(device).eval()
        if device == 'cuda':
            torch.cuda.synchronize()
        loading_seconds = time.perf_counter() - load_start
        meta['checkpoint_manifest'] = checkpoint
        meta['parameter_count'] = sum(p.numel() for p in model.parameters())
        meta['model_loading_seconds'] = loading_seconds
        meta['effective_generation_config'] = model.generation_config.to_dict()
        meta['system_prompt_sha256'] = hashlib.sha256(cfg['system_prompt'].encode()).hexdigest()
        def sync():
            if device == "cuda":
                torch.cuda.synchronize()
            elif device == "mps":
                torch.mps.synchronize()
        def generate(question, limit=None):
            messages = [{"role":"system","content":cfg["system_prompt"]},{"role":"user","content":question}]
            prompt = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True,
                                            enable_thinking=cfg["enable_thinking"])
            inputs = tok(prompt, add_special_tokens=False, return_tensors="pt").to(device)
            settings = dict(cfg["generation"])
            if limit:
                settings["max_new_tokens"] = limit
            sync()
            started = time.perf_counter()
            with torch.inference_mode():
                output = model.generate(**inputs, **settings, pad_token_id=tok.pad_token_id, eos_token_id=tok.eos_token_id)
            sync()
            elapsed = time.perf_counter()-started
            generated = output[0, inputs.input_ids.shape[1]:]
            response = tok.decode(generated, skip_special_tokens=True)
            if not response.strip():
                raise RuntimeError('Model generated an empty response')
            return {"response":response, "latency_seconds":elapsed,
                    "input_tokens":inputs.input_ids.shape[1], "output_tokens":len(generated),
                    "output_token_ids":generated.tolist(),
                    "truncated":len(generated)==settings["max_new_tokens"],
                    "prompt_sha256":hashlib.sha256(prompt.encode()).hexdigest()}
        warmup = generate("What is 2 + 2? Answer briefly.", cfg["warmup_tokens"])
        template = tok.chat_template
        segment_info = dict(versions=versions(), hardware=inspect(), device=device, precision=str(dtype),
                    quantization=None, backend="transformers", attention=cfg["attention"],
                    checkpoint_revision=getattr(model.config,"_commit_hash",None) or revision,
                    config=cfg, chat_template_sha256=hashlib.sha256(str(template).encode()).hexdigest(),
                    chat_template=template, warmup=warmup)
        if args.resume:
            validate_resume_environment(meta, segment_info)
        else:
            meta.update(segment_info)
        meta["status"]="running"
        if device == "cuda":
            torch.cuda.reset_peak_memory_stats()
        save(meta_path,meta)
        if args.smoke_only:
            meta["status"]="smoke_only"
        else:
            for q in rows:
                if q["id"] in {r["question_id"] for r in done}:
                    continue
                result = {"run_id":run_id,"question_id":q["id"],"model":args.model,
                          "question":q["question"],"timestamp":now(),"error":None,
                          "category":q['category'],"difficulty":q['difficulty'],"revision":revision,
                          "system_prompt_sha256":meta['system_prompt_sha256'],
                          "chat_template_sha256":meta['chat_template_sha256'],
                          "metadata_reference":meta_path.name}
                started = time.perf_counter()
                try:
                    result.update(generate(q["question"]))
                except Exception as e:
                    result.update(response="",latency_seconds=time.perf_counter()-started,
                                  input_tokens=None,output_tokens=None,truncated=None,error=repr(e))
                    if device == "cuda":
                        torch.cuda.empty_cache()
                result["process_rss_bytes"] = psutil.Process().memory_info().rss
                append(raw,result)
                done.append(result)
                print(f"{len(done)}/{len(rows)} {q['id']} {result['latency_seconds']:.3f}s error={result['error']}",flush=True)
            if len(done) != len(rows) or {r['question_id'] for r in done} != {q['id'] for q in rows}:
                raise ValueError('Cannot complete run with missing or conflicting IDs')
            meta["status"]="completed"
            meta['successful_responses'] = sum(not r.get('error') for r in done)
            meta['generation_failures'] = sum(bool(r.get('error')) for r in done)
        meta["completed_at"] = now()
        meta["peak_process_rss_bytes"] = max([r.get("process_rss_bytes",0) for r in done]+[psutil.Process().memory_info().rss])
        meta["peak_gpu_allocated_bytes"] = max(meta.get("peak_gpu_allocated_bytes") or 0, torch.cuda.max_memory_allocated()) if device=="cuda" else None
        meta["peak_gpu_reserved_bytes"] = max(meta.get("peak_gpu_reserved_bytes") or 0, torch.cuda.max_memory_reserved()) if device=="cuda" else None
    except BaseException as e:
        meta.update(status="interrupted" if isinstance(e,KeyboardInterrupt) else "failed", fatal_error=repr(e))
        raise
    finally:
        meta["segments"].append({"ended_at":now(),"duration_seconds":time.perf_counter()-session_start, **segment_info})
        meta["total_execution_seconds"] = sum(s["duration_seconds"] for s in meta["segments"])
        save(meta_path,meta)
        lock.unlink(missing_ok=True)
        print(run_id,flush=True)

if __name__=="__main__":
    main()
