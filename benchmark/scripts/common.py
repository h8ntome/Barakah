"""Shared file formats; paths resolve relative to benchmark/, not the caller."""
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = ("zakat", "investing", "principles", "budgeting", "safety")

def now():
    return datetime.now(timezone.utc).isoformat()

def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def save(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")
    os.replace(tmp, path)

def config(path=None):
    import yaml
    return yaml.safe_load(Path(path or ROOT / "config.yaml").read_text())

def dataset(cfg=None):
    return json.loads((ROOT / (cfg or config())["dataset"]).read_text())

def validate_data(rows):
    assert rows, "Empty dataset"
    ids = set()
    for q in rows:
        for k in ("id", "category", "difficulty", "question", "reference_answer", "key_facts",
                  "expected_behavior", "source_references", "answer_type", "scoring_method", "review_status"):
            assert k in q, f"{q.get('id')}: missing {k}"
        assert q["id"] not in ids, "Duplicate question ID"
        ids.add(q["id"])
        assert q["category"] in CATEGORIES
        assert q["difficulty"] in ("easy", "medium", "difficult")
        assert q["reference_answer"].strip(), "Missing reference answer"
        assert q["source_references"], "Missing sources"
        if q["scoring_method"] == "deterministic":
            from decimal import Decimal
            spec = q["calculation"]
            a = [Decimal(str(x)) for x in spec["operands"]]
            operations = {"zakat": lambda: sum(a) * Decimal(".025"),
                          "sum": lambda: sum(a),
                          "difference": lambda: a[0] - sum(a[1:]),
                          "savings_rate": lambda: a[0] / a[1] * 100,
                          "multiply": lambda: a[0] * a[1],
                          "divide": lambda: a[0] / a[1]}
            expected = operations[spec["operation"]]().quantize(Decimal(".01"))
            assert expected == Decimal(str(q["expected_numeric"])), f"Bad arithmetic {q['id']}"
    return True

def load_jsonl(path, repair=False):
    """Only an incomplete final line may be truncated; never discard interior corruption."""
    path = Path(path)
    if not path.exists():
        return []
    data = path.read_bytes()
    lines = data.splitlines(keepends=True)
    rows, offset = [], 0
    for i, line in enumerate(lines):
        try:
            row = json.loads(line)
        except (ValueError, UnicodeDecodeError):
            if repair and i == len(lines)-1 and not line.endswith(b"\n"):
                with path.open("r+b") as f:
                    f.truncate(offset)
                break
            raise ValueError(f"Corrupt JSONL line {i+1} in {path}")
        rows.append(row)
        offset += len(line)
    if repair and rows and not path.read_bytes().endswith(b"\n"):
        with path.open("ab") as f:
            f.write(b"\n")
    ids = [r["question_id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate results")
    return rows

def append(path, row):
    with Path(path).open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())

def resolve_run(name):
    direct = ROOT / "results/raw" / name
    if direct.with_suffix(".meta.json").exists():
        return direct
    matches = sorted((ROOT / "results/raw").glob(name + "_*.meta.json"))
    if len(matches) != 1:
        raise ValueError(f"Run {name!r} resolves to {len(matches)} runs. Use exact run ID.")
    return Path(str(matches[0])[:-10])

def versions():
    import importlib.metadata
    import sys
    names = ("torch", "transformers", "huggingface_hub", "accelerate", "safetensors",
             "triton", "psutil", "PyYAML", "matplotlib")
    out = {"python": sys.version}
    for name in names:
        try:
            out[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            out[name] = None
    return out
