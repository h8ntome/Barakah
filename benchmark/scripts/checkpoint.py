"""Immutable Hub snapshots and file-level integrity for full models or PEFT adapters."""
import argparse
import json
import re
from pathlib import Path
from common import digest, now, save


def checkpoint_kind(names):
    names = set(names)
    adapter = 'adapter_config.json' in names
    if adapter:
        if 'adapter_model.safetensors' not in names:
            raise ValueError('Incomplete adapter: safetensors weights missing')
        return 'adapter'
    if 'config.json' not in names or not any(n.endswith('.safetensors') for n in names):
        raise ValueError('Incomplete full checkpoint')
    return 'full'


def resolve_info(api, model, revision):
    info = api.model_info(model, revision=revision, files_metadata=True)
    if not re.fullmatch('[a-f0-9]{40}', info.sha):
        raise ValueError('Hub did not resolve an immutable revision')
    if re.fullmatch('[a-f0-9]{40}', revision or '') and info.sha != revision:
        raise ValueError('Resolved revision differs from requested pin')
    return info


def verify_manifest(manifest):
    path = Path(manifest['snapshot_path'])
    for name, item in manifest['files'].items():
        f = path / name
        if not f.resolve().is_file() or f.stat().st_size != item['bytes'] or digest(f) != item['sha256']:
            raise ValueError(f'Checkpoint changed: {name}')
    return path


def download(model, revision, output, cache_dir=None):
    from huggingface_hub import HfApi, snapshot_download
    from safetensors import safe_open
    # Public access is tested explicitly; no credentials are serialized.
    public = True
    try:
        info = resolve_info(HfApi(token=False), model, revision)
    except Exception:
        public = False
        info = resolve_info(HfApi(), model, revision)
    kind = checkpoint_kind(s.rfilename for s in info.siblings)
    path = Path(snapshot_download(model, revision=info.sha, cache_dir=cache_dir))
    inventory = {}
    for sibling in info.siblings:
        f = path / sibling.rfilename
        sha = digest(f)
        if sibling.size is not None and f.stat().st_size != sibling.size:
            raise ValueError(f'File size mismatch: {sibling.rfilename}')
        if sibling.lfs and sha != sibling.lfs.sha256:
            raise ValueError(f'LFS hash mismatch: {sibling.rfilename}')
        inventory[sibling.rfilename] = {'bytes': f.stat().st_size, 'sha256': sha,
                                       'hub_lfs_sha256': sibling.lfs.sha256 if sibling.lfs else None}
    tensors = {}
    for f in path.glob('*.safetensors'):
        with safe_open(f, framework='pt', device='cpu') as handle:
            tensors[f.name] = len(handle.keys())
    index = path / 'model.safetensors.index.json'
    if index.exists() and not set(json.loads(index.read_text())['weight_map'].values()) <= set(inventory):
        raise ValueError('Missing weight shards')
    config_name = 'adapter_config.json' if kind == 'adapter' else 'config.json'
    result = {'model': model, 'revision': info.sha, 'public_without_authentication': public,
              'kind': kind, 'snapshot_path': str(path), 'timestamp': now(), 'files': inventory,
              'tensor_counts': tensors, 'model_config': json.loads((path/config_name).read_text()),
              'model_card': info.card_data.to_dict() if info.card_data else {}}
    output = Path(output)
    if output.exists():
        raise FileExistsError(f'Preserve previous provenance: {output}')
    save(output, result)
    print(json.dumps(result, indent=2))
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--model', required=True)
    p.add_argument('--revision', default='main')
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--cache-dir')
    a = p.parse_args()
    download(a.model, a.revision, a.output, a.cache_dir)
