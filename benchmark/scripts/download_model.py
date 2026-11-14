"""Pin, reuse/download and hash the official BF16 snapshot; never substitutes models."""
import argparse
import shutil
from pathlib import Path
from common import ROOT, config, digest, save, now

def download(model, revision):
    from huggingface_hub import HfApi, snapshot_download
    # Resolve before executing repository code. A commit SHA pins both code and weights.
    info = HfApi().model_info(model, revision=revision, files_metadata=True)
    sha = info.sha
    kwargs = dict(repo_id=model, revision=sha,
                  allow_patterns=["*.json", "*.safetensors", "*.py", "*.jinja", "LICENSE", "README.md"])
    cached = False
    try:
        path = Path(snapshot_download(**kwargs, local_files_only=True))
        cached = (path / "model.safetensors").exists()
    except Exception:
        path = None
    free = shutil.disk_usage(Path.home()).free
    if not cached:
        if free < 6 * 1024**3:
            raise RuntimeError("Need at least 6 GiB free disk for BF16 checkpoint and download overhead.")
    # The hub reuses existing blobs and retrieves any missing tokenizer/code files.
    path = Path(snapshot_download(**kwargs))
    required = ("config.json", "tokenizer.json", "tokenizer_config.json", "model.safetensors",
                "modeling_lfm3.py", "configuration_lfm3.py", "lfm3_conv.py", "chat_template.jinja", "LICENSE")
    for name in required:
        if not (path / name).is_file():
            raise RuntimeError(f"Incomplete checkpoint: {name}. Rerun download after checking Hugging Face access.")
    from safetensors import safe_open
    with safe_open(path / "model.safetensors", framework="pt", device="cpu") as f:
        tensors = len(list(f.keys()))
    weight = next(s for s in info.siblings if s.rfilename == "model.safetensors")
    expected_weight_sha256 = weight.lfs.sha256 if weight.lfs else None
    actual_weight_sha256 = digest(path / "model.safetensors")
    if not expected_weight_sha256 or actual_weight_sha256 != expected_weight_sha256:
        raise RuntimeError("Checkpoint SHA256 does not match the official pinned Hugging Face LFS object")
    meta = {"model": model, "revision": sha, "snapshot_path": str(path), "timestamp": now(),
            "official_weight_sha256": expected_weight_sha256, "official_weight_hash_verified": True,
            "reused_cache": cached, "weight_format": "safetensors", "weight_precision": "BF16",
            "tensor_count": tensors, "free_disk_bytes": free,
            "hardware": __import__("check_hardware").inspect(),
            "files": {n: {"sha256": actual_weight_sha256 if n == "model.safetensors" else digest(path/n), "bytes": (path/n).stat().st_size} for n in required}}
    save(ROOT / "results/hardware/model_download.json", meta)
    print(f"Verified {model}@{sha}: {path}; reused_cache={cached}")
    return path

if __name__ == "__main__":
    cfg = config()
    p = argparse.ArgumentParser()
    p.add_argument("--model", default=cfg["model"])
    p.add_argument("--revision", default=cfg["revision"])
    args = p.parse_args()
    try:
        download(args.model, args.revision)
    except Exception as e:
        save(ROOT / "results/hardware/download_failure.json", {"timestamp": now(), "error": repr(e)})
        raise SystemExit(f"Download failed: {e}. Check network, disk space, repository ID and model license.")
