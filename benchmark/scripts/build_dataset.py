"""Rebuild the authored held-out dataset. Never call during an active evaluation."""
import csv
import json
from decimal import Decimal, ROUND_HALF_EVEN
from collections import Counter
from common import ROOT, digest, save, validate_data, now

ZAKAT_SOURCE = "https://www.islamic-relief.org.uk/giving/islamic-giving/zakat/"
BUDGET_SOURCE = "https://www.consumerfinance.gov/an-essential-guide-to-building-an-emergency-fund/"
IMF_SOURCE = "https://www.imf.org/external/themes/islamicfinance/"

def arithmetic():
    rows = []
    def add(id, category, difficulty, question, operation, operands, unit="USD", source=BUDGET_SOURCE):
        a = [Decimal(str(x)) for x in operands]
        result = {"zakat": lambda: sum(a)*Decimal(".025"), "difference": lambda:a[0]-sum(a[1:]),
                  "sum":lambda:sum(a), "savings_rate":lambda:a[0]/a[1]*100,
                  "multiply":lambda:a[0]*a[1], "divide":lambda:a[0]/a[1]}[operation]()
        result = result.quantize(Decimal(".01"), rounding=ROUND_HALF_EVEN)
        rows.append(dict(id=id, category=category, difficulty=difficulty,
            question=question+" Round to two decimal places and end with 'Final answer: <number> "+unit+"'.",
            reference_answer=f"{result:.2f} {unit}. This is the calculation under the explicit scenario assumptions, not a ruling.",
            key_facts=[f"The requested result is {result:.2f} {unit}."],
            expected_behavior="Compute only the requested quantity using the supplied assumptions; no invented eligibility decisions.",
            source_references=[source, "Arithmetic independently rechecked with decimal.Decimal by validate_benchmark.py"],
            answer_type="calculation", scoring_method="deterministic", review_status="arithmetic_verified",
            expected_numeric=str(result), numeric_tolerance="0.01", unit=unit,
            calculation={"operation":operation,"operands":[str(x) for x in operands]}))
    for i, amount in enumerate([10000,24000,8000,12500,50000,18320,9876.40,32145.60,100000,15000.80,27549.24,61023.76,49999.96,123456.72,76543.28],1):
        add(f"ZAKAT_{i:03}","zakat", "easy" if i<=5 else "medium" if i<=10 else "difficult",
            f"Eligible zakatable wealth is USD {amount:.2f}. Assume nisab and one lunar year are satisfied, eligibility and debt treatment have already been reviewed, and use a 2.5% rate. What is the zakat amount?",
            "zakat",[amount],source=ZAKAT_SOURCE)
    cases = [
      ("Monthly income is USD 3000 and total monthly spending is USD 2400. How much remains?","difference",[3000,2400],"USD"),
      ("You save USD 400 from monthly take-home pay of USD 2000. What percentage of take-home pay is saved?","savings_rate",[400,2000],"%"),
      ("Rent is USD 900, groceries USD 350 and transport USD 150. What is the total?","sum",[900,350,150],"USD"),
      ("You set aside USD 75 per month for 8 months with no returns. How much accumulates?","multiply",[75,8],"USD"),
      ("A USD 1200 savings goal is funded at USD 100 monthly with no returns. How many months are needed?","divide",[1200,100],"months"),
      ("Monthly income is USD 4250; rent USD 1400, food USD 480, transport USD 210 and other spending USD 760. What remains?","difference",[4250,1400,480,210,760],"USD"),
      ("Save USD 525 from USD 3500 take-home pay. What is the savings rate as a percentage of that pay?","savings_rate",[525,3500],"%"),
      ("A family chooses an emergency reserve target equal to 4 months of essential costs of USD 1850 per month. What is the target?","multiply",[4,1850],"USD"),
      ("A charity budget is USD 160 and actual donations are USD 205. How much did donations exceed the budget?","difference",[205,160],"USD"),
      ("Weekly discretionary spending falls from USD 145 to USD 92. What is the weekly saving?","difference",[145,92],"USD"),
      ("Monthly take-home pay is USD 2875.50 and spending is USD 2399.35. How much remains?","difference",[2875.50,2399.35],"USD"),
      ("Save USD 387.50 out of USD 3100 take-home pay. What percentage of pay is saved?","savings_rate",[387.50,3100],"%"),
      ("Monthly essentials are rent USD 1125.75, food USD 389.40, utilities USD 157.85 and transport USD 126.20. What is the total?","sum",[1125.75,389.40,157.85,126.20],"USD"),
      ("An emergency fund target is USD 9000 and the current balance is USD 3275.50. How much more is needed?","difference",[9000,3275.50],"USD"),
      ("You save USD 142.75 each month for 12 months with no returns. What is the total?","multiply",[142.75,12],"USD"),
      ("Take-home pay is USD 5120.80. Expenses are USD 1775.45, USD 628.90, USD 351.25 and USD 920.60. What remains?","difference",[5120.80,1775.45,628.90,351.25,920.60],"USD"),
      ("You save USD 613.25 from USD 4675.80 take-home pay. What percentage of pay is saved?","savings_rate",[613.25,4675.80],"%"),
      ("An annual insurance bill of USD 1374 is spread over 12 equal monthly sinking-fund deposits with no returns. What is one deposit?","divide",[1374,12],"USD"),
      ("Monthly income is USD 2800 but spending is USD 3027.45. What is the positive amount of the shortfall?","difference",[3027.45,2800],"USD"),
      ("A family chooses a reserve target of 6 months of essentials costing USD 2134.65 each month. What is the target?","multiply",[6,2134.65],"USD")]
    for i,(q,op,a,u) in enumerate(cases,1):
        add(f"BUDGET_{i:03}","budgeting","easy" if i<=5 else "medium" if i<=14 else "difficult",q,op,a,u)
    for i,(profit,share) in enumerate([(1000,.4),(2500,.6),(1840,.35),(7325.60,.45),(12347.80,.375)],16):
        add(f"PRINCIPLE_{i:03}","principles","medium" if i<=18 else "difficult",
            f"In a hypothetical profit-sharing exercise, realized distributable profit is USD {profit:.2f}. The agreed investor share of this actual profit is {share*100:g}%. Calculate the investor's allocation only; do not assess the contract's Sharia compliance.",
            "multiply",[profit,share],source=IMF_SOURCE)
    return rows

def main():
    conceptual = json.loads((ROOT/"datasets/conceptual_questions.json").read_text())
    rows = sorted(arithmetic()+conceptual,key=lambda q:q["id"])
    validate_data(rows)
    counts = dict(Counter(q["category"] for q in rows))
    assert counts == {"budgeting":20,"investing":25,"principles":20,"safety":10,"zakat":25}, counts
    path = ROOT/"datasets/benchmark_questions.json"
    save(path,rows)
    with (ROOT/"datasets/benchmark_questions.csv").open("w",newline="") as f:
        keys = list(dict.fromkeys(k for q in rows for k in q))
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader()
        w.writerows({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in q.items()} for q in rows)
    save(ROOT/"datasets/dataset_manifest.json",{"version":"1.0.0","created_at":now(),"count":len(rows),
        "category_counts":counts,"difficulty_counts":dict(Counter(q["difficulty"] for q in rows)),
        "sha256":digest(path),"csv_sha256":digest(ROOT/"datasets/benchmark_questions.csv"),
        "split":"held_out_evaluation_only","training_use":"prohibited for benchmark comparisons",
        "automatic_arithmetic_count":40,"reference_checked_pending_expert_count":60,
        "expert_reviewed_count":0,"construction":"40 Decimal-verified arithmetic scenarios; 60 institution-backed conceptual rubrics; source review is not expert endorsement"})
    print(f"Validated {len(rows)} questions; SHA256 {digest(path)}")

if __name__=="__main__":
    main()
