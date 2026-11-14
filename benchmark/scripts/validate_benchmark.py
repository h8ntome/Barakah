"""Validate dataset, run fingerprints and synchronized result checksums."""
import argparse
import json
from common import ROOT, dataset, digest, load_jsonl, save, validate_data

def verify_integrity(manifest_path, base):
    manifest=json.loads(manifest_path.read_text())
    for rel,expected in manifest.items():
        path=(base/rel).resolve()
        if not path.is_relative_to(base.resolve()):raise ValueError("Unsafe manifest path")
        if digest(path)!=expected:raise ValueError(f"Checksum mismatch: {rel}")
    return len(manifest)

def main():
    p=argparse.ArgumentParser();p.add_argument("--write-integrity",action="store_true");a=p.parse_args()
    rows=dataset();validate_data(rows)
    manifest=json.loads((ROOT/"datasets/dataset_manifest.json").read_text())
    assert manifest["sha256"]==digest(ROOT/"datasets/benchmark_questions.json")
    assert manifest["csv_sha256"]==digest(ROOT/"datasets/benchmark_questions.csv")
    for path in (ROOT/"results/raw").glob("*.jsonl"):
        results=load_jsonl(path)
        meta=json.loads(path.with_suffix(".meta.json").read_text())
        assert meta["fingerprint"]["dataset_sha256"]==manifest["sha256"]
        assert {r["question_id"] for r in results}<={q["id"] for q in rows}
        assert meta["hardware"]["cpu"] and meta["hardware"]["ram_total_bytes"]>0
    from compare_models import processed
    for path in (ROOT/"results/processed").glob("*.json"):
        processed(path.stem)
    integrity=ROOT/"results/remote_integrity.json"
    if a.write_integrity:
        files=[p for folder in ("raw","hardware","processed") for p in (ROOT/"results"/folder).rglob("*") if p.is_file() and p.suffix!=".lock"]
        save(integrity,{str(p.relative_to(ROOT)):digest(p) for p in sorted(files)})
    if integrity.exists():print(f"Verified {verify_integrity(integrity,ROOT)} synchronized files")
    print(f"PASS: {len(rows)} questions; valid IDs, references, arithmetic, fingerprints and hardware")

if __name__=="__main__":main()
