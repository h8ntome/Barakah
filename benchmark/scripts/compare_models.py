"""Paired task comparison; never compare incompatible overall denominators."""
import argparse
import json
from common import ROOT, digest, resolve_run, save

def processed(name):
    run=resolve_run(name)
    result=json.loads((ROOT/"results/processed"/(run.name+".json")).read_text())
    if result.get("raw_sha256") != digest(run.with_suffix(".jsonl")) or result.get("metadata_sha256") != digest(run.with_suffix(".meta.json")):
        raise ValueError("Processed scores are stale: raw responses or metadata changed; re-evaluate first")
    if result["dataset_sha256"] != digest(ROOT/"datasets/benchmark_questions.json"):
        raise ValueError("Processed scores refer to a different dataset")
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
    result={"baseline":a["run_id"],"candidate":b["run_id"],"paired_numeric_n":len(paired),
       "numeric_correctness":metric(paired),"categories":{},"question_disagreements":[],
       "hardware_differences":{"baseline":a["metadata"].get("hardware"),"candidate":b["metadata"].get("hardware")},
       "speed_comparison_caveat":"Different hardware/runtime and task coverage are not model speed improvements.",
       "candidate_config":b["metadata"].get("config"),"baseline_config":a["metadata"].get("config")}
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
    if result["baseline_config"] and result["candidate_config"] and result["baseline_config"]!=result["candidate_config"]:
        result["decoding_warning"]="Generation configurations differ; comparison not controlled."
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--baseline",required=True);p.add_argument("--candidate",required=True)
    args=p.parse_args()
    try:a=processed(args.baseline);b=processed(args.candidate);out=compare(a,b)
    except (ValueError,FileNotFoundError) as e:raise SystemExit(f"Comparison unavailable: {e}. Run and score the candidate first; no adapted model is bundled.")
    save(ROOT/"results/comparisons"/(a["run_id"]+"__"+b["run_id"]+".json"),out)
    print(json.dumps(out,indent=2))
