"""Narrow public-question-only zakat calculator; does not read reference answers."""
import argparse
import re
import time
from decimal import Decimal, ROUND_HALF_EVEN
from common import ROOT, append, dataset, digest, now, save, versions

def answer(question):
    m=re.search(r"Eligible zakatable wealth is USD (\d+\.\d{2})\.",question)
    if not m or "use a 2.5% rate" not in question:
        raise ValueError("Outside baseline scope")
    amount=(Decimal(m.group(1))*Decimal(".025")).quantize(Decimal(".01"),rounding=ROUND_HALF_EVEN)
    return f"Final answer: {amount:.2f} USD"

def main():
    p=argparse.ArgumentParser();p.add_argument("--run-name",default="rules");a=p.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]+",a.run_name):p.error("Invalid run name")
    run_id=a.run_name+"_"+now().replace(":","").replace("-","").replace(".","")
    raw=ROOT/"results/raw"/(run_id+".jsonl")
    rows=[q for q in dataset() if q["category"]=="zakat" and q["scoring_method"]=="deterministic"]
    start=now();total_start=time.perf_counter()
    for q in rows:
        t=time.perf_counter()
        try:response=answer(q["question"]);error=None
        except Exception as e:response="";error=repr(e)
        append(raw,{"run_id":run_id,"question_id":q["id"],"model":"deterministic-zakat-v1",
          "question":q["question"],"response":response,"latency_seconds":time.perf_counter()-t,
          "input_tokens":None,"output_tokens":None,"error":error,"truncated":False})
    save(raw.with_suffix(".meta.json"),{"run_id":run_id,"run_name":a.run_name,"started_at":start,"completed_at":now(),
        "status":"completed","execution_host":"local","hardware":__import__("check_hardware").inspect(),
        "total_execution_seconds":time.perf_counter()-total_start,"versions":versions(),
        "fingerprint":{"model":"deterministic-zakat-v1","revision":None,
            "dataset_sha256":digest(ROOT/"datasets/benchmark_questions.json")},
        "scope":"15 public question-text zakat calculations only; no reference answer access; not a religious eligibility engine"})
    print(run_id)

if __name__=="__main__":main()
