#!/usr/bin/env python3
"""Read-only check of authored benchmark and isolated local API; never saves credentials."""
import hashlib, json, pathlib, urllib.request, urllib.error
from decimal import Decimal
ROOT=pathlib.Path(__file__).resolve().parents[2]
OUT=ROOT/'demo-video/reports'
def read(path):return json.loads((ROOT/path).read_text())
questions=read('benchmark/datasets/benchmark_questions.json')
assert len(questions)==100 and len({q['id'] for q in questions})==100
counts={c:sum(q['category']==c for q in questions) for c in ['zakat','investing','principles','budgeting','safety']}
assert counts==dict(zakat=25,investing=25,principles=20,budgeting=20,safety=10)
assert sum(q['review_status']=='arithmetic_verified' for q in questions)==40
assert sum(q['review_status']=='reference_checked_pending_expert' for q in questions)==60
raw=ROOT/'benchmark/results/raw/original_20261114T184206126429+0000.jsonl'
rows=[json.loads(l) for l in raw.read_text().splitlines()]
failure=next(r for r in rows if r['question_id']=='ZAKAT_007')
assert 'Final answer: 246.61 USD' in failure['response']
assert Decimal('9876.40')*Decimal('.025')==Decimal('246.91000')
assert Decimal('15000')*Decimal('.025')==Decimal('375')
evidence={'category_counts':counts,'questions':100,'arithmetic':40,'expert_review_pending':60,'failure':{k:failure[k] for k in ['question_id','model','question','timestamp','response']},'raw_sha256':hashlib.sha256(raw.read_bytes()).hexdigest()}
BASE='http://127.0.0.1:8095/api/v1'
def req(path,method='GET',data=None,token=None):
    headers={'Origin':'http://127.0.0.1:8095'}
    if token:headers['Authorization']='Bearer '+token
    body=None
    if data is not None:body=json.dumps(data).encode();headers['Content-Type']='application/json'
    r=urllib.request.Request(BASE+path,data=body,headers=headers,method=method)
    try:
        with urllib.request.urlopen(r,timeout=10) as response:return response.status,json.load(response)
    except urllib.error.HTTPError as e:return e.code,json.load(e)
status,demo=req('/auth/demo','POST',{})
assert status==201, (status,demo.keys())
token=demo['access_token']
status,health=req('/ai/health',token=token)
assert status==200 and health['status']=='unavailable'
status,result=req('/advisor/messages','POST',{'text':"I have $12,000 in savings and I’m planning for Hajj next year. How should I think about zakat and keeping that money safe?"},token)
assert status==503 and result['response'] is None and result['error']['code']=='ai_unavailable'
s,history=req('/advisor/conversations',token=token)
assert s==200 and history==[],history
evidence['api']={'ai_health':health,'send_status':status,'send_result':result,'conversation_count_after_send':len(history),'environment':'isolated loopback 127.0.0.1:8095'}
(OUT/'verified-evidence.json').write_text(json.dumps(evidence,indent=2))
print('PASS: dataset counts, arithmetic, archival response, actual AI unavailable response, no saved conversations')
