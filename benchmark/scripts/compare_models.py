"""Paired task comparison; never compare incompatible overall denominators."""
import argparse
import json
from pathlib import Path
from common import ROOT, digest, resolve_run, load_jsonl


def effective_run_settings(meta, records=None):
    """Fingerprint identifies the run; config is only the input template, never an identity fallback."""
    fingerprint = meta.get('fingerprint') or {}
    identity = {key: fingerprint.get(key) for key in ('model', 'revision')}
    evidence = ['fingerprint'] if identity['model'] else []
    for name in ('checkpoint_manifest', 'effective_config'):
        source = meta.get(name)
        if source:
            if any(source.get(key) != identity[key] for key in identity):
                raise ValueError(f'Conflicting effective identity: {name}')
            evidence.append(name)
    if meta.get('checkpoint_revision') and meta['checkpoint_revision'] != identity['revision']:
        raise ValueError('Conflicting effective checkpoint revision')
    raw_fields = []
    if records:
        if not identity['model'] or any(any(key in row and row[key] != identity[key] for key in identity) for row in records):
            raise ValueError('Raw rows disagree with effective run identity')
        raw_fields = [key for key in identity if all(key in row for row in records)]
        evidence.append('raw_rows' if len(raw_fields) == len(identity) else 'raw_rows_partial')
    template = meta.get('config') or {}
    return {**identity, 'identity_evidence': evidence, 'raw_identity_fields': raw_fields,
            'identity_caveat': 'Artifact-recorded identity; not proof of training lineage or independent checkpoint execution.',
            'template_identity_differs': bool(identity['model'] and template and any(template.get(k) != identity[k] for k in identity)),
            'device_requested': fingerprint.get('device_requested'), 'device_resolved': meta.get('device'),
            'precision': meta.get('precision'), 'attention': meta.get('attention'),
            'generation': template.get('generation'), 'enable_thinking': template.get('enable_thinking'),
            'seed': template.get('seed'), 'system_prompt_sha256': meta.get('system_prompt_sha256'),
            'chat_template_sha256': meta.get('chat_template_sha256')}


def processed(name):
    run=resolve_run(name)
    result=json.loads((ROOT/"results/processed"/(run.name+".json")).read_text())
    if result.get("raw_sha256") != digest(run.with_suffix(".jsonl")) or result.get("metadata_sha256") != digest(run.with_suffix(".meta.json")):
        raise ValueError("Processed scores are stale: raw responses or metadata changed; re-evaluate first")
    if result["dataset_sha256"] != digest(ROOT/"datasets/benchmark_questions.json"):
        raise ValueError("Processed scores refer to a different dataset")
    metadata = json.loads(run.with_suffix('.meta.json').read_text())
    if result.get('metadata', {}) != metadata:
        raise ValueError('Processed metadata differs from its hashed source')
    result['effective_run_settings'] = effective_run_settings(metadata, load_jsonl(run.with_suffix('.jsonl')))
    return result

def change(old,new):
    if old is None or new is None:return {"baseline":old,"candidate":new,"absolute":None,"percentage_points":None,"relative_change":None}
    return {"baseline":old,"candidate":new,"absolute":new-old,"percentage_points":100*(new-old),
            "relative_change":(new-old)/old if old else None}

def compare(a,b):
    if a["dataset_sha256"]!=b["dataset_sha256"]:raise ValueError("Different held-out datasets")
    amap={s["question_id"]:s for s in a["scores"]};bmap={s["question_id"]:s for s in b["scores"]}
    paired=sorted(k for k in amap.keys()&bmap.keys() if amap[k]["numeric_task"] and bmap[k]["numeric_task"])
    if not paired:raise ValueError("No paired automatically scored examples")
    def metric(ids):
        return change(sum(amap[k]["automatic_correctness"] is True for k in ids)/len(ids),
                      sum(bmap[k]["automatic_correctness"] is True for k in ids)/len(ids))
    result={"schema_version":2,"exporter_sha256":digest(__file__),"baseline":a["run_id"],"candidate":b["run_id"],"paired_numeric_n":len(paired),
       "numeric_correctness":metric(paired),"categories":{},"question_disagreements":[],
       "hardware_differences":{"baseline":a["metadata"].get("hardware"),"candidate":b["metadata"].get("hardware")},
       "speed_comparison_caveat":"Different hardware/runtime and task coverage are not model speed improvements.",
       "candidate_template_config":b["metadata"].get("config"),"baseline_template_config":a["metadata"].get("config"),
       "candidate_effective_run_settings":b.get('effective_run_settings') or effective_run_settings(b['metadata']),
       "baseline_effective_run_settings":a.get('effective_run_settings') or effective_run_settings(a['metadata']),
       "provenance_note":"Legacy *_config fields copied template defaults, not CLI-resolved identity. This v2 export separates them; historical evidence is unchanged.",
       "source_hashes":{label:{key:run.get(key) for key in ('raw_sha256','metadata_sha256','dataset_sha256','scoring_code_sha256')} for label,run in (('baseline',a),('candidate',b))}}
    for category in sorted({amap[k]["category"] for k in paired}):
        ids=[k for k in paired if amap[k]["category"]==category]
        result["categories"][category]={"n":len(ids),**metric(ids)}
    for k in paired:
        if amap[k]["automatic_correctness"]!=bmap[k]["automatic_correctness"]:
            result["question_disagreements"].append({"id":k,"baseline":amap[k]["automatic_correctness"],"candidate":bmap[k]["automatic_correctness"]})
    for field,channel in (("verified_safety_failure_rate","verified_safety_failures"),("verified_hallucination_rate","verified_hallucinations"),("human_reviewed_correctness","human_reviewed_correctness")):
        ids=[k for k in amap.keys()&bmap.keys() if amap[k][channel] is not None and bmap[k][channel] is not None]
        old=sum(amap[k][channel] is True for k in ids)/len(ids) if ids else None
        new=sum(bmap[k][channel] is True for k in ids)/len(ids) if ids else None
        result[field]={"paired_n":len(ids),**change(old,new),"note":"Paired independently reviewed channels only."}
    for field in ("mean_latency_seconds","aggregate_output_tokens_per_second"):
        x=a["summary"]["performance"][field];y=b["summary"]["performance"][field]
        result[field]={"baseline":x,"candidate":y,"absolute":y-x if x is not None and y is not None else None,
                       "relative_change":(y-x)/x if x and y is not None else None}
    before, after = result['baseline_template_config'], result['candidate_template_config']
    if before and after and any(before.get(k) != after.get(k) for k in ('generation','enable_thinking','seed','system_prompt')):
        result["decoding_warning"]="Generation or prompt configurations differ; comparison not controlled."
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--baseline",required=True);p.add_argument("--candidate",required=True)
    p.add_argument('--output', type=Path, help='New export path; existing files are never overwritten')
    args=p.parse_args()
    try:a=processed(args.baseline);b=processed(args.candidate);out=compare(a,b)
    except (ValueError,FileNotFoundError) as e:raise SystemExit(f"Comparison unavailable: {e}. Run and score the candidate first; no adapted model is bundled.")
    output = args.output or ROOT/"results/comparisons"/(a["run_id"]+"__"+b["run_id"]+".identity-v2.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x') as stream:
        json.dump(out, stream, indent=2, ensure_ascii=False)
        stream.write('\n')
    print(json.dumps(out,indent=2))
