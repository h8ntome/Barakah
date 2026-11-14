"""Generate all figures and a portable, offline dashboard from saved scored runs."""
import argparse
import html
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from common import ROOT, dataset, load_jsonl
from compare_models import compare, processed

GREEN='#073B2C'; GOLD='#AD8536'; CANVAS='#FCFBF7'; INK='#10241D'; RED='#A3443D'

def figure(title, ylabel=None):
    fig,ax=plt.subplots(figsize=(9,5.2),layout='constrained')
    fig.patch.set_facecolor(CANVAS);ax.set_facecolor(CANVAS)
    ax.set_title(title,loc='left',fontsize=17,pad=22,color=GREEN,fontweight='bold')
    ax.spines[['top','right']].set_visible(False)
    ax.spines[['left','bottom']].set_color('#BCCBBF')
    ax.tick_params(colors=INK)
    if ylabel:ax.set_ylabel(ylabel)
    return fig,ax

def export(fig,name,out):
    for ext in ('png','svg'):
        folder=out/ext;folder.mkdir(parents=True,exist_ok=True)
        fig.savefig(folder/(name+'.'+ext),dpi=170,facecolor=CANVAS)
    plt.close(fig)

def fraction(metric):
    return f"{metric['numerator']}/{metric['denominator']}" if metric['denominator'] else 'Unavailable (n=0)'

def charts(original,rules,out,candidate=None):
    scores=original['scores'];s=original['summary'];meta=original['metadata']
    model_label=original['model'];host=meta.get('execution_host','Unknown host')
    hardware=meta.get('hardware',{});gpu=hardware.get('gpu',{})
    planned_numeric={c:sum(q['category']==c and q['scoring_method']=='deterministic' for q in dataset()) for c in s['by_category']}
    by_id={r['question_id']:r for r in rules['scores']}
    paired=[q for q in scores if q['question_id'] in by_id and q['numeric_task']]
    fig,ax=figure('Zakat arithmetic: a matched-task comparison','Correct numeric answers (%)')
    n=len(paired)
    values=[sum(q['automatic_correctness'] is True for q in paired),sum(by_id[q['question_id']]['automatic_correctness'] is True for q in paired)]
    if n:
        ax.bar([model_label,'Formula baseline'],[100*v/n for v in values],color=[GREEN,GOLD],width=.48)
        for i,v in enumerate(values):ax.text(i,100*v/n+2,f'{v}/{n}',ha='center')
    else:
        ax.axis('off');ax.text(.05,.55,'Matched numeric results unavailable (n=0)',fontsize=16,color=GREEN,transform=ax.transAxes)
    ax.set_ylim(0,114);ax.text(.02,-.17,'Same questions; eligibility supplied. Not overall religious correctness.',transform=ax.transAxes,fontsize=9)
    export(fig,'01_overall_performance',out)
    for field,name,title in [('category','02_category_performance','Coverage and numeric correctness by category'),('difficulty','03_difficulty_performance','Numeric correctness by difficulty')]:
        values=s['by_'+field];labels=list(values)
        fig,ax=figure(title,'Automatically correct numeric answers (%)')
        for i,(label,item) in enumerate(values.items()):
            metric=item['automatic_numeric_correctness'];den=metric['denominator']
            if den:
                ax.bar(i,100*metric['rate'],color=GREEN,width=.55)
                ax.text(i,100*metric['rate']+3,f"{fraction(metric)} numeric\n{item['pending_correctness_review']} pending",ha='center',fontsize=9)
            else:
                message='Numeric results unavailable' if field=='difficulty' or planned_numeric.get(label,0) else 'No numeric tasks'
                ax.text(i,8,f"{message}\n{item['pending_correctness_review']} pending",ha='center',fontsize=8,color=INK)
        ax.set_xticks(range(len(labels)),[f"{k.title()}\n(total n={values[k]['sample_size']})" for k in labels]);ax.set_ylim(0,125)
        ax.text(.01,-.24,'Pending conceptual judgments are not scored as incorrect or correct.',transform=ax.transAxes,fontsize=9)
        export(fig,name,out)
    raw=load_jsonl(ROOT/'results/raw'/(original['run_id']+'.jsonl'))
    lat=[r['latency_seconds'] for r in raw if not r['error']]
    fig,ax=figure(f'Generation latency on {host} (n={len(lat)})','Number of responses')
    if lat:
        ax.hist(lat,bins=min(16,max(1,len(lat))),color=GREEN,edgecolor=CANVAS)
        ax.axvline(s['performance']['median_latency_seconds'],color=GOLD,label='Median',linewidth=2)
        ax.legend(frameon=False)
    ax.set_xlabel('Seconds per response (prefill + decode; no tokenization)')
    export(fig,'04_latency_distribution',out)
    fig,ax=figure('Observed automatic evaluation outcomes','Number of responses')
    counts=s['automatic_status_counts']
    labels=['Numeric correct','Numeric incorrect','Unparseable','Generation error','Conceptual pending']
    vals=[counts['correct'],counts['incorrect'],counts['unparseable'],s['generation_failure_rate']['numerator'],s['pending_correctness_review']]
    ax.barh(labels,vals,color=[GREEN,RED,GOLD,RED,'#738F7E'])
    for i,v in enumerate(vals):ax.text(v+.5,i,str(v),va='center')
    ax.set_xlim(0,max(vals+[1])*1.18);ax.set_xlabel('Responses (pending is not a model failure)');ax.set_ylabel(None)
    export(fig,'05_error_distribution',out)
    fig,ax=figure('Safety and hallucinations: review coverage','Responses')
    labels=['Safety reviewed','Hallucinations reviewed','Candidate flags','Safety pending','Hallucinations pending']
    vals=[s['verified_safety_failure_rate']['denominator'],s['verified_hallucination_rate']['denominator'],s['candidate_flagged_responses']['numerator'],s['safety_review_pending'],s['hallucination_review_pending']]
    ax.barh(labels,vals,color=[GREEN,GREEN,GOLD,'#738F7E','#738F7E'])
    for i,v in enumerate(vals):ax.text(v+.5,i,str(v),va='center')
    ax.set_xlim(0,max(vals+[1])*1.2);ax.set_xlabel('Response count; channels overlap');ax.set_ylabel(None)
    ax.text(.01,-.21,'Regex flags are review candidates, not verified failures. Unreviewed rates are unavailable.',transform=ax.transAxes,fontsize=9)
    export(fig,'06_safety_hallucination',out)
    fig,ax=figure('Checkpoint comparison: evidence status')
    m=s['automatic_numeric_correctness']
    if candidate:
        paired_result=compare(original,candidate);metric=paired_result['numeric_correctness']
        ax.bar([original['run_name'],candidate['run_name']],[metric['baseline']*100,metric['candidate']*100],color=[GREEN,GOLD],width=.5)
        ax.set_ylabel('Matched numeric correctness (%)');ax.set_ylim(0,115)
        ax.text(.03,.04,f"Paired n={paired_result['paired_numeric_n']}; not overall religious correctness",transform=ax.transAxes,fontsize=10)
    else:
        ax.axis('off')
        ax.text(.04,.68,f"Evaluated run: {fraction(m)} correct numeric answers",fontsize=19,color=GREEN)
        ax.text(.04,.46,'Additional adapted checkpoint: unavailable',fontsize=18,color=INK)
        ax.text(.04,.25,'No candidate comparison was supplied.\nNo adaptation improvement claim can be made.',fontsize=12,color=INK,linespacing=1.7)
    export(fig,'07_model_comparison',out)
    fig,ax=figure('Hardware performance: one measured execution host')
    ax.axis('off');throughput=s['performance']['aggregate_output_tokens_per_second']
    ax.text(.04,.72,f"{host}: {throughput:.2f} output tokens/second" if throughput is not None else 'Throughput unavailable',fontsize=21,color=GREEN)
    ax.text(.04,.50,f"{gpu.get('name',meta.get('device','Unknown device'))} / {meta.get('precision','unknown precision')} / {meta.get('backend','unknown runtime')}",fontsize=12,color=INK)
    ax.text(.04,.30,f"Aggregate {s['performance']['output_tokens']} tokens / successful generation wall time.\nNo comparable second-host inference was supplied. No cross-host speedup.\nMemory and workload constraints are documented in the hardware report.",fontsize=11,linespacing=1.7,color=INK)
    export(fig,'08_hardware_performance',out)

STYLE='''@font-face{font-family:DM Sans;src:url(fonts/dm-sans.woff2) format("woff2");font-display:swap}*{box-sizing:border-box}body{margin:0;background:#FCFBF7;color:#10241D;font:16px/1.65 "DM Sans",sans-serif}header{background:#073B2C;color:#fff;padding:28px max(6vw,20px)}header a{color:#EBD5A4}nav{display:flex;flex-wrap:wrap;gap:22px;font-size:14px}main{max-width:1160px;margin:auto;padding:45px 24px 70px}h1{font:400 clamp(35px,5vw,60px)/1.1 Georgia,serif;max-width:800px;margin:12px 0 24px}h2{font:400 30px/1.2 Georgia,serif;color:#073B2C;margin:42px 0 18px}h3{font-size:18px}p{max-width:74ch}a{color:#08603E;text-underline-offset:4px}a:hover{text-decoration-thickness:2px}a:focus-visible,summary:focus-visible,select:focus-visible{outline:3px solid #AD8536;outline-offset:5px}::selection{background:#D9C38F;color:#073B2C}code{overflow-wrap:anywhere;font-size:.88em}table{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums}th,td{text-align:left;border-bottom:1px solid #DCE5DC;padding:13px 12px 13px 0}th{font-size:13px;color:#496255}small,.muted{color:#496255}header .muted{color:#D5E6DB}.notice{padding:18px 22px;border:1px solid #C5AA6C;background:#F4ECD9;border-radius:8px}.results{display:grid;grid-template-columns:1.3fr 1fr;gap:44px;align-items:start}.results figure{margin:0}.results img{width:100%;height:auto}dl{display:grid;grid-template-columns:minmax(140px,1fr) 1fr;margin:0}dt,dd{margin:0;padding:14px 0;border-bottom:1px solid #DCE5DC}dd{font-weight:600;font-variant-numeric:tabular-nums}.chart-grid{display:grid;grid-template-columns:1fr 1fr;gap:22px}.chart-grid figure{margin:0}.chart-grid img{width:100%;height:auto}figcaption{font-size:13px;color:#496255;padding:0 8px}details{border-bottom:1px solid #DCE5DC;padding:16px 0}summary{cursor:pointer;font-weight:600}details p{white-space:pre-wrap;overflow-wrap:anywhere}select{font:inherit;background:white;border:1px solid #73917E;border-radius:6px;padding:9px 12px;color:#073B2C}label{margin-right:12px}footer{margin-top:50px;padding-top:24px;border-top:1px solid #C9D8CD}.table-scroll{overflow-x:auto}section{scroll-margin-top:24px}.status{color:#755315;font-weight:600}img{max-width:100%}@media(max-width:760px){main{padding:28px 18px 50px}.results,.chart-grid{grid-template-columns:1fr;gap:22px}header{padding:24px 18px}h2{font-size:27px}th,td{font-size:13px}dl{grid-template-columns:1fr 1fr;gap:10px}nav{gap:12px 20px}}'''

def dashboard(original,rules,out,candidate=None):
    s=original['summary'];m=original['metadata'];esc=lambda v:html.escape(str(v))
    raw=load_jsonl(ROOT/'results/raw'/(original['run_id']+'.jsonl'))
    raw_by={r['question_id']:r for r in raw}
    numeric=s['automatic_numeric_correctness'];perf=s['performance']
    number=lambda v:f'{v:.2f}' if v is not None else 'Unavailable'
    numeric_percent=f" ({100*numeric['rate']:.1f}%)" if numeric['rate'] is not None else ''
    candidate_note=(f"Candidate {candidate['model']} was evaluated; see the matched comparison chart and comparison JSON." if candidate else 'No candidate checkpoint comparison was supplied. No adaptation improvement is claimed.')
    category_rows=''.join(f"<tr><td>{esc(k.title())}</td><td>{v['sample_size']}</td><td>{fraction(v['automatic_numeric_correctness'])}</td><td>{v['pending_correctness_review']}</td></tr>" for k,v in s['by_category'].items())
    examples=[]
    for status,title in [('correct','Correct numeric examples'),('incorrect','Incorrect numeric examples'),('unparseable','Unparseable numeric examples'),('truncated','Responses reaching the output cap')]:
        matching=[q for q in original['scores'] if (q.get('truncated') if status=='truncated' else q.get('status')==status)][:3]
        examples.append('<h3>'+title+'</h3>')
        if not matching:examples.append('<p>No observed examples in this run.</p>')
        for q in matching:
            r=raw_by[q['question_id']]
            examples.append(f"<details><summary>{esc(q['question_id'])}: {esc(r['question'][:100])}</summary><p>{esc(r['question'])}</p><p>{esc(r['response'])}</p><small>Observed status: {esc(status)}. Prose not expert-certified.</small></details>")
    question_rows=[]
    for q in original['scores']:
        r=raw_by[q['question_id']]
        question_rows.append(f"<details data-category='{esc(q['category'])}'><summary>{esc(q['question_id'])} / {esc(q.get('status',q['evaluation_status']))}</summary><p>{esc(r['question'])}</p><p>{esc(r['response'])}</p><small>Safety / hallucination review: pending unless recorded in processed results.</small></details>")
    chart_names=['02_category_performance','03_difficulty_performance','04_latency_distribution','05_error_distribution','06_safety_hallucination','07_model_comparison','08_hardware_performance']
    gallery=''.join(f"<figure><a href='../svg/{name}.svg'><img src='../svg/{name}.svg' alt='{esc(name.replace('_',' ')[3:])}' loading='lazy'></a></figure>" for name in chart_names)
    gpu=m.get('hardware',{}).get('gpu',{})
    content=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Barakah • LFM3 benchmark evidence</title><style>{STYLE}</style></head><body>
<header><nav aria-label="Benchmark navigation"><strong>Barakah / Research</strong><a href="#results">Results</a><a href="#coverage">Coverage</a><a href="#examples">Examples</a><a href="#responses">All responses</a><a href="../../reports/BENCHMARK_REPORT.md">Full report</a></nav>
<h1>A measured starting point for faith-aligned finance.</h1><p>{esc(original['model'])}. A held-out benchmark for Barakah, not a certification of financial advice or religious authority.</p><p class="muted">{esc(original['run_id'])}<br>Checkpoint <code>{esc(m.get('checkpoint_revision'))}</code></p></header>
<main><div class="notice"><strong>Read the denominator.</strong> {s['sample_size']}/{s['dataset_size']} questions answered; {numeric['denominator']} numeric tasks automatically scored. {s['pending_correctness_review']} conceptual judgments await expert review. Safety and hallucination rates are <strong>unavailable</strong> until reviewed—not zero.</div>
<section id="results"><h2>What the evidence says</h2><div class="results"><figure><img src="../svg/01_overall_performance.svg" alt="Matched zakat arithmetic comparison"><figcaption>The formula baseline receives the same public question text. Its scope is calculation, not eligibility or religious guidance.</figcaption></figure><dl><dt>Numeric correctness</dt><dd>{fraction(numeric)}{numeric_percent}</dd><dt>Human-reviewed correctness</dt><dd>{fraction(s['human_reviewed_correctness'])}</dd><dt>Median generation</dt><dd>{number(perf['median_latency_seconds'])} seconds</dd><dt>P95 generation</dt><dd>{number(perf['p95_latency_seconds'])} seconds</dd><dt>Output throughput</dt><dd>{number(perf['aggregate_output_tokens_per_second'])} tokens/s</dd><dt>Generation errors</dt><dd>{fraction(s['generation_failure_rate'])}</dd></dl></div></section>
<section id="coverage"><h2>Coverage, not blanket confidence</h2><div class="table-scroll"><table><thead><tr><th>Category</th><th>Responses</th><th>Verified numeric</th><th>Conceptual pending</th></tr></thead><tbody>{category_rows}</tbody></table></div><p class="muted">Numeric correctness verifies the final requested quantity only. It does not certify every claim in the surrounding answer. Wilson intervals and exact denominators are available in the processed JSON.</p></section>
<section><h2>Safety needs independent review</h2><p>{s['candidate_flagged_responses']['numerator']}/{s['sample_size']} responses contain heuristic review flags. Negation, quotations and warnings can trigger them. No flag is counted as a verified hallucination or safety failure without evidence-based human adjudication.</p><div class="chart-grid">{gallery}</div></section>
<section><h2>Execution provenance</h2><dl><dt>Host</dt><dd>{esc(m.get('execution_host'))}</dd><dt>Accelerator</dt><dd>{esc(gpu.get('name','Unavailable'))}</dd><dt>Precision / runtime</dt><dd>{esc(m.get('precision'))} / Transformers</dd><dt>PyTorch</dt><dd>{esc(m.get('versions',{}).get('torch'))}</dd><dt>Completed</dt><dd>{esc(m.get('completed_at'))}</dd></dl><p>{esc(candidate_note)} No comparable second-host inference was supplied; hardware speedups are not claimed.</p></section>
<section id="examples"><h2>Read the actual answers</h2>{''.join(examples)}</section>
<section id="responses"><h2>Inspect every response</h2><label for="category">Category</label><select id="category"><option value="all">All categories</option>{''.join(f'<option value="{c}">{c.title()}</option>' for c in s['by_category'])}</select><p id="visible-count" aria-live="polite">{len(question_rows)} responses</p>{''.join(question_rows)}</section>
<footer><p><a href="../../README.md">Reproduce this run</a> · <a href="../../reports/METHODOLOGY.md">Methodology</a> · <a href="../../reports/LIMITATIONS.md">Limitations</a> · <a href="../../reports/HARDWARE_COMPARISON.md">Hardware evidence</a> · <a href="../../results/processed/{esc(original['run_id'])}.json">Processed JSON</a></p><p class="muted">Built from saved inference outputs. No external scripts, APIs, hosted fonts or backend required.</p></footer></main>
<script>document.getElementById('category').addEventListener('change',function(){{let n=0;document.querySelectorAll('[data-category]').forEach(el=>{{el.hidden=this.value!=='all'&&el.dataset.category!==this.value;if(!el.hidden)n++;}});document.getElementById('visible-count').textContent=n+' responses';}});</script></body></html>'''
    folder=out/'html';folder.mkdir(parents=True,exist_ok=True)
    (folder/'index.html').write_text(content)

def generate(original,rules,out=None,candidate=None):
    out=Path(out or ROOT/'visuals');charts(original,rules,out,candidate);dashboard(original,rules,out,candidate)
    print(f'Generated 8 PNG + 8 SVG figures and {out}/html/index.html')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',default='original');p.add_argument('--baseline',default='rules');p.add_argument('--candidate');a=p.parse_args()
    generate(processed(a.run),processed(a.baseline),candidate=processed(a.candidate) if a.candidate else None)
