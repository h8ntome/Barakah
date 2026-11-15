"""Prospective corrected-dimension packets; never modifies original frozen exports."""
import hashlib
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent

def main():
    manifest=json.loads((HERE/'amendment_manifest.json').read_text())
    for relative,expected in manifest['files'].items():
        if hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()!=expected:
            raise ValueError(f'Amendment changed: {relative}')
    rubric=json.loads((HERE/'rubric_prospective_v1.json').read_text())
    packets=json.loads((ROOT/'results/analysis/reviewer_packets/pairs.json').read_text())
    for packet in packets:
        if packet['reviewer_id'] is not None or any(value is not None for scores in packet['scores'].values() for value in scores.values()):
            raise ValueError('Never replace completed human reviews')
        packet['scores']={label:{name:None for name in rubric['dimensions']} for label in ('A','B')}
        packet['rubric_release']='prospective_v1_late_amendment'
    output=ROOT/'results/analysis/reviewer_packets_amended'
    output.mkdir(exist_ok=False)
    for name,obj in [('pairs.json',packets),('rubric.json',rubric)]:
        (output/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
    print(f'Exported {len(packets)} amended paired packets; all five human scores null; mapping unchanged and separate.')

if __name__=='__main__': main()
