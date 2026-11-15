"""Small standard-library utilities and strict limited numeric extraction."""
import hashlib
import json
import re
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def now():
    return datetime.now(timezone.utc).isoformat()

def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest()

def save(path,obj):
    Path(path).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')

def verify_freeze():
    manifest=json.loads((ROOT/'freeze_manifest.json').read_text())
    for relative, expected in manifest['files'].items():
        if digest(ROOT/relative) != expected:
            raise ValueError(f'Frozen file changed: {relative}')
    return manifest

def score_numeric(question, record):
    if question['numeric'] is None:
        return dict(status='not_applicable',score=None)
    if record.get('error'):
        return dict(status='inference_error',score=0)
    text=record['response']
    lines=[line.strip() for line in text.splitlines() if line.strip()]
    if (text.count('ANSWER_AMOUNT:') != 1 or text.count('ANSWER_UNIT:') != 1 or len(lines)<2):
        return dict(status='unparseable',score=0)
    amount=re.fullmatch(r'ANSWER_AMOUNT: ([+-]?\d+\.\d{2})',lines[-2])
    unit=re.fullmatch(r'ANSWER_UNIT: (USD|percent)',lines[-1])
    if not amount or not unit:
        return dict(status='unparseable',score=0)
    if unit.group(1) != question['numeric']['unit']:
        return dict(status='incorrect',score=0,extracted=amount.group(1),unit=unit.group(1),reason='wrong_unit')
    correct=abs(Decimal(amount.group(1))-Decimal(question['numeric']['expected']))<=Decimal(question['numeric']['tolerance'])
    return dict(status='correct' if correct else 'incorrect',score=int(correct),extracted=amount.group(1),unit=unit.group(1))
