"""Export only the supervisor's canonical prospective rubric; preserve earlier artifacts."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RUBRIC_SHA='27ab3aa1571a66d0b637355caf0284b999e0c6a836b32d41484c8f43d8ed5503'

def main():
    source=ROOT/'amendments/canonical_parent_rubric.json'
    if hashlib.sha256(source.read_bytes()).hexdigest()!=RUBRIC_SHA:
        raise ValueError('Canonical rubric checksum changed')
    rubric=json.loads(source.read_text())
    packets=json.loads((ROOT/'results/analysis/reviewer_packets/pairs.json').read_text())
    for packet in packets:
        if packet['reviewer_id'] is not None or any(v is not None for scores in packet['scores'].values() for v in scores.values()):
            raise ValueError('Cannot replace completed human scores')
        packet['scores']={label:{name:None for name in rubric['dimensions']} for label in ('A','B')}
        packet['rubric_sha256']=RUBRIC_SHA
        packet['reviewer_qualifications']=None
        packet['response_sha256']={label:hashlib.sha256(text.encode()).hexdigest() for label,text in packet['responses'].items()}
    output=ROOT/'results/analysis/reviewer_packets_canonical'
    output.mkdir(exist_ok=False)
    for name,obj in [('pairs.json',packets),('rubric.json',rubric)]:
        (output/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
    print(f'Exported {len(packets)} canonical paired packets, five dimensions, all human scores null. Original private mapping unchanged.')

if __name__=='__main__': main()
