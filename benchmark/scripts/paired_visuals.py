"""Slide-ready measured figures and an offline paired-response dashboard."""
import argparse
import csv
import html
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from common import save
from generate_visuals import GREEN, GOLD, CANVAS, INK, RED, STYLE

COLORS = [GOLD, GREEN]
LABELS = ['Original LFM3-1.7B', 'Barakah fine-tuned']
NAMES = ['01_numerical_accuracy','02_category_accuracy','03_difficulty_accuracy','04_paired_outcomes','05_latency','06_throughput','07_resources','08_coverage','09_accuracy_latency','10_question_matrix']
TITLES = ['Numerical accuracy','Numerical accuracy by category','Numerical accuracy by difficulty','Improvements and regressions','Model response latency','Measured inference throughput','Resource usage','Benchmark coverage and review status','Numerical accuracy versus latency','Question-level evaluation matrix']


def number(v, suffix=''):
    return f'{v:.2f}{suffix}' if v is not None else 'Unavailable'


def canvas(title, note):
    fig, ax = plt.subplots(figsize=(16,9))
    fig.patch.set_facecolor(CANVAS); ax.set_facecolor(CANVAS)
    fig.subplots_adjust(left=.12,right=.95,top=.82,bottom=.20)
    fig.text(.07,.92,title,fontsize=25,color=GREEN,weight='bold')
    fig.text(.07,.065,note,fontsize=12,color=INK,wrap=True)
    ax.spines[['top','right']].set_visible(False)
    ax.tick_params(labelsize=13)
    return fig,ax


def export(fig, name, folder):
    for ext in ('png','svg'):
        (folder/ext).mkdir(parents=True,exist_ok=True)
        fig.savefig(folder/ext/f'{name}.{ext}',dpi=150,facecolor=CANVAS)
    plt.close(fig)


def paired_bars(ax, labels, values, ylabel, annotations=None, missing='Unavailable'):
    for model in range(2):
        for i, label in enumerate(labels):
            v=values[model][i]
            x=i+(model-.5)*.34
            if v is not None:
                ax.bar(x,v,width=.30,color=COLORS[model],label=LABELS[model] if i==0 else None)
                ax.annotate(annotations[model][i] if annotations else f'{v:.2f}',(x,v),xytext=(0,8),textcoords='offset points',ha='center',fontsize=12)
            else:
                if values[1-model][i] is not None or model == 0:
                    ax.text(i if values[1-model][i] is None else x,8,missing,ha='center',fontsize=11)
    ax.set_xticks(range(len(labels)),labels);ax.set_ylabel(ylabel,fontsize=14)
    ax.set_xlim(-.6,len(labels)-.4)
    if ax.get_legend_handles_labels()[0]:
        ax.legend(frameon=False,loc='upper right',fontsize=12)
    ax.margins(y=.22)


def charts(out, folder):
    runs=list(out['runs'].values()); summaries=[r['summary'] for r in runs]
    note='40 numerical questions • terminal-answer grading only • 60 conceptual questions per model await human review'
    chart_data={}
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':13,'svg.fonttype':'none'})
    fig,ax=canvas(TITLES[0],note+'\nWhiskers show Wilson 95% intervals; not population-level guarantees.')
    vals=[s['automatic_numeric_correctness'] for s in summaries]
    ax.bar(LABELS,[100*v['rate'] for v in vals],color=COLORS,width=.48)
    for i,v in enumerate(vals):
        ax.text(i,100*v['rate']+3,f"{v['numerator']}/{v['denominator']}  ·  {100*v['rate']:.1f}%",ha='center',fontsize=18)
        low,high=v['wilson_95_interval'];ax.errorbar(i,100*v['rate'],yerr=[[100*(v['rate']-low)],[100*(high-v['rate'])]],fmt='none',ecolor=INK,capsize=6)
    ax.set_ylim(0,115);ax.set_ylabel('Correct numerical answers (%)');export(fig,NAMES[0],folder)
    chart_data[NAMES[0]]=vals
    for idx,field in [(1,'category'),(2,'difficulty')]:
        keys=list(summaries[0]['by_'+field]);values=[];annotations=[]
        for s in summaries:
            ms=[s['by_'+field][k]['automatic_numeric_correctness'] for k in keys]
            values.append([100*m['rate'] if m['rate'] is not None else None for m in ms])
            annotations.append([f"{m['numerator']}/{m['denominator']}" for m in ms])
        fig,ax=canvas(TITLES[idx],note)
        paired_bars(ax,[k.title() for k in keys],values,'Correct numerical answers (%)',annotations,missing='Review pending')
        ax.set_ylim(0,125);ax.set_yticks(range(0,101,20));export(fig,NAMES[idx],folder)
        chart_data[NAMES[idx]]={'labels':keys,'percent':values,'counts':annotations}
    counts=out['outcome_counts'];keys=['improved','regressed','both_correct','both_incorrect']
    fig,ax=canvas(TITLES[3],'Paired n=40 • every numerical question is retained • unparseable answers and generation failures count as not correct')
    ax.barh(['Baseline incorrect → Barakah correct','Baseline correct → Barakah incorrect','Both correct','Both incorrect'],[counts[k] for k in keys],color=[GREEN,RED,'#668575','#897451'])
    for i,k in enumerate(keys):ax.text(counts[k]+.3,i,str(counts[k]),va='center',fontsize=18)
    ax.set_xlim(0,max(counts[k] for k in keys)*1.2+1);ax.set_xlabel('Questions');ax.invert_yaxis();export(fig,NAMES[3],folder);chart_data[NAMES[3]]={k:counts[k] for k in keys}
    perf=[s['performance'] for s in summaries]
    fig,ax=canvas(TITLES[4],'100 successful responses per model if no failures • same server2 / BF16 / ROCm • sequential shared-host measurements, lower is better')
    fields=['mean_latency_seconds','median_latency_seconds','p95_latency_seconds']
    values=[[s[k] for k in fields] for s in perf];paired_bars(ax,['Mean','Median','P95'],values,'Seconds per response')
    export(fig,NAMES[4],folder);chart_data[NAMES[4]]={'fields':fields,'seconds':values}
    fig,ax=canvas(TITLES[5],'Total generated tokens / total successful generation seconds • includes prefill and decode, excludes tokenization • not decode-only speed')
    values=[s['aggregate_output_tokens_per_second'] for s in perf]
    for i,v in enumerate(values):
        if v is not None:ax.bar(i,v,color=COLORS[i],width=.48);ax.text(i,v+.3,number(v)+' tok/s',ha='center',fontsize=18)
        else:ax.text(i,.1,'Unavailable',ha='center',fontsize=16)
    ax.set_xticks([0,1],LABELS);ax.set_ylabel('Output tokens / second');ax.margins(y=.2);export(fig,NAMES[5],folder)
    chart_data[NAMES[5]]={'tokens_per_second':values,'output_tokens':[s['output_tokens'] for s in perf]}
    fig,ax=canvas(TITLES[6],'PyTorch process allocation, not total GPU use • RSS sampled after answers, not continuous peak • integrated GPU shares system RAM')
    fields=['peak_gpu_allocated_bytes','peak_process_rss_bytes'];values=[[r['metadata'].get(k)/1024**3 if r['metadata'].get(k) is not None else None for k in fields] for r in runs]
    paired_bars(ax,['Peak GPU allocation','Peak sampled process RSS'],values,'GiB');export(fig,NAMES[6],folder);chart_data[NAMES[6]]={'fields':fields,'GiB':values}
    fig,ax=canvas(TITLES[7],'100 unique questions, each answered by both models • review pending: 60 questions / 120 model responses • no combined accuracy')
    cats=list(summaries[0]['by_category']);numeric=[summaries[0]['by_category'][c]['automatic_numeric_correctness']['denominator'] for c in cats]
    pending=[summaries[0]['by_category'][c]['pending_correctness_review'] for c in cats]
    ax.barh([c.title() for c in cats],numeric,color=GREEN,label='Automatically scored numerical')
    ax.barh([c.title() for c in cats],pending,left=numeric,color=GOLD,label='Conceptual: human review pending')
    for i,(n,p) in enumerate(zip(numeric,pending)):
        if n:ax.text(n/2,i,str(n),ha='center',va='center',color='white',weight='bold')
        if p:ax.text(n+p/2,i,str(p),ha='center',va='center',color=INK,weight='bold')
    ax.set_xlim(0,31);ax.set_xlabel('Unique questions');ax.legend(frameon=False,loc='lower right');export(fig,NAMES[7],folder)
    chart_data[NAMES[7]]={'categories':cats,'numeric':numeric,'pending':pending}
    fig,ax=canvas(TITLES[8],'Accuracy: 40 numerical questions only • latency: all 100 responses • shorter answers can reduce latency without better decoding speed')
    for i,(s,p) in enumerate(zip(summaries,perf)):
        x=p['mean_latency_seconds'];y=100*s['automatic_numeric_correctness']['rate']
        if x is None:
            ax.text(.03,.85-i*.12,LABELS[i]+': latency unavailable',transform=ax.transAxes)
            continue
        ax.scatter([x],[y],s=220,color=COLORS[i],label=LABELS[i],edgecolor=INK)
        ax.annotate(f'{LABELS[i]}\n{y:.1f}% / {x:.2f}s',(x,y),xytext=(14,14 if i else -38),textcoords='offset points',fontsize=14)
    ax.set_ylim(0,105);ax.set_xlim(0,max([p['mean_latency_seconds'] for p in perf if p['mean_latency_seconds'] is not None]+[1])*1.55);ax.set_xlabel('Mean generation latency (seconds; lower is better)');ax.set_ylabel('Numerical accuracy (%; higher is better)')
    export(fig,NAMES[8],folder);chart_data[NAMES[8]]={'mean_seconds':[p['mean_latency_seconds'] for p in perf],'accuracy_percent':[100*s['automatic_numeric_correctness']['rate'] for s in summaries]}
    fig,ax=canvas(TITLES[9],'All 100 questions in frozen order • + improved   − regressed   = both correct   × both incorrect   ? conceptual review pending')
    codes={'unreviewed':0,'both_correct':1,'both_incorrect':2,'improved':3,'regressed':4};marks={'unreviewed':'?','both_correct':'=','both_incorrect':'×','improved':'+','regressed':'−'}
    rows=out['questions'];matrix=[[codes[r['outcome']] for r in rows[i:i+10]] for i in range(0,100,10)]
    ax.imshow(matrix,cmap=ListedColormap(['#E4EAE2','#DFF3E3','#E4CFAB',GREEN,RED]),vmin=0,vmax=4,aspect='auto')
    for i,r in enumerate(rows):
        ax.text(i%10,i//10,r['question_id'].replace('PRINCIPLE','PRINC').replace('_',' ')+'\n'+marks[r['outcome']],ha='center',va='center',fontsize=9,color='white' if r['outcome'] in ('improved','regressed') else INK)
    ax.set_xticks([]);ax.set_yticks([]);export(fig,NAMES[9],folder);chart_data[NAMES[9]]=[{'id':r['question_id'],'outcome':r['outcome']} for r in rows]
    save(folder/'data/chart_data.json',chart_data)
    with (folder/'data/chart_values.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['chart','data_json'])
        for k,v in chart_data.items():w.writerow([k,json.dumps(v)])


def dashboard(out, folder):
    esc=lambda x:html.escape(str(x));runs=list(out['runs'].values());s=[r['summary'] for r in runs]
    delta=out['numeric_correctness']['percentage_points']
    heading='Fine-tuning, measured against the original.'
    cards=''.join(f'<article><h3>{LABELS[i]}</h3><strong class="metric">{100*r["automatic_numeric_correctness"]["rate"]:.1f}%</strong><p>{r["automatic_numeric_correctness"]["numerator"]}/40 numerical answers correct</p><p>{number(r["performance"]["mean_latency_seconds"])}s mean · {number(r["performance"]["aggregate_output_tokens_per_second"])} tokens/s</p></article>' for i,r in enumerate(s))
    rows=[]
    for r in out['questions']:
        answers=''.join(f'<article><h3>{LABELS[i]}</h3><p class="answer">{esc(r[label+"_response"])}</p><p class="muted">{esc(r[label+"_status"])} · {number(r[label+"_latency_seconds"])} seconds · {r[label+"_output_tokens"]} output tokens</p></article>' for i,label in enumerate(('baseline','barakah')))
        rows.append(f'<details data-question data-category="{r["category"]}" data-difficulty="{r["difficulty"]}" data-outcome="{r["outcome"]}" data-numeric="{int(r["numeric"])}" data-a="{int(r["baseline_score"] is True)}" data-b="{int(r["barakah_score"] is True)}"><summary>{r["question_id"]} <span>{r["outcome"].replace("_"," ")}</span></summary><p>{esc(r["question"])}</p><div class="answers">{answers}</div></details>')
    selectors=''
    for field,options in [('category',['budgeting','investing','principles','safety','zakat']),('difficulty',['easy','medium','difficult']),('outcome',['improved','regressed','both_correct','both_incorrect','unreviewed'])]:
        selectors+=f'<label>{field.title()}<select id="{field}"><option value="all">All {field} values</option>'+''.join(f'<option value="{v}">{v.replace("_"," ").title()}</option>' for v in options)+'</select></label>'
    metadata=''.join(f'<tr><th>{LABELS[i]}</th><td>{esc(r["model"])}<br><code>{esc(r["metadata"]["fingerprint"]["revision"])}</code><br><code>{esc(r["run_id"])}</code></td></tr>' for i,r in enumerate(runs))
    css=STYLE.replace('fonts/dm-sans.woff2','../../html/fonts/dm-sans.woff2')+'''header h1{max-width:900px}main{max-width:1280px}.scoreboard,.answers{display:grid;grid-template-columns:1fr 1fr;gap:36px}.scoreboard{margin:26px 0 40px;border-bottom:1px solid #CCD9C6}.scoreboard article{padding:12px 0 24px}.scoreboard article:first-child h3{color:#755315}.scoreboard article:last-child h3{color:#073B2C}.metric{font-size:48px;font-variant-numeric:tabular-nums;font-weight:600}.filters{display:flex;gap:18px;flex-wrap:wrap}.filters label{display:flex;flex-direction:column;gap:6px}.filters select{min-height:44px}summary{display:flex;justify-content:space-between;gap:16px}summary span{font-size:14px;font-weight:400}.answer{white-space:pre-wrap;max-width:72ch}.answers article{min-width:0}.answers h3{margin-bottom:8px}.chart-view{margin:18px 0 42px}.chart-view img{width:100%;height:auto}.filter-stats{display:flex;gap:30px;flex-wrap:wrap;padding:18px 0}.filter-stats meter{width:180px;accent-color:#073B2C}input{font:inherit;padding:10px;border:1px solid #73917E;border-radius:6px;max-width:100%;caret-color:#073B2C}input:focus-visible{outline:3px solid #AD8536;outline-offset:3px}button{font:inherit;cursor:pointer;border:1px solid #73917E;background:#fff;color:#073B2C;padding:10px 16px;border-radius:6px;min-height:44px}button:hover{background:#DFF3E3}button:focus-visible{outline:3px solid #AD8536;outline-offset:3px}[hidden]{display:none!important}html{scrollbar-color:#73917E #FCFBF7}.notice{max-width:none}@media(max-width:700px){.scoreboard,.answers{grid-template-columns:1fr;gap:12px}.metric{font-size:38px}.filters{display:grid;grid-template-columns:1fr 1fr;gap:12px}.filters label{margin:0}.filters select{min-width:0;width:100%}summary{font-size:14px}.scoreboard{margin-bottom:24px}}'''
    content=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Barakah AI | Paired benchmark</title><style>{css}</style></head><body>
<header><nav aria-label="Benchmark navigation"><strong>Barakah AI</strong><a href="#evidence">Measured results</a><a href="#questions">Compare answers</a><a href="#method">Methodology</a><a href="../../../reports/20261115/BENCHMARK_REPORT.md">Technical report</a></nav><h1>{heading}</h1><p>Original LFM3-1.7B versus Barakah’s full fine-tuned checkpoint. Same 100 questions. Same neutral prompt. Real inference on server2.</p></header><main>
<section id="evidence"><h2>Numerical results, not a blanket quality claim</h2><div class="scoreboard">{cards}</div><div class="notice"><strong>{delta:+.1f} percentage points on 40 numerical questions.</strong> {out['outcome_counts']['improved']} improvements, {out['outcome_counts']['regressed']} regressions. McNemar exact p={out['statistics']['mcnemar_exact_two_sided_p']:.4f}. Conceptual correctness, hallucinations and safety remain unverified: 60 conceptual answers per model await qualified review.</div>
<h2>Explore the measurements</h2><label for="chart">Chart</label><select id="chart">{''.join(f'<option value="{n}">{t}</option>' for n,t in zip(NAMES,TITLES))}</select><figure class="chart-view"><img id="chart-image" src="../svg/{NAMES[0]}.svg" alt="{TITLES[0]}"><figcaption><a id="chart-svg" href="../svg/{NAMES[0]}.svg">Open SVG</a> · <a id="chart-png" href="../png/{NAMES[0]}.png">Download high-resolution PNG</a> · <a href="../data/chart_data.json">Underlying chart data</a></figcaption></figure></section>
<section id="questions"><h2>Every answer, including regressions</h2><p>Choose a subset to update its numerical scores and inspect the paired responses. Conceptual answers are illustrative, not correctness judgments.</p><div class="filters">{selectors}<label>Search question or answer<input id="search" type="search" placeholder="Search all response text"></label></div><div class="filter-stats" aria-live="polite"><strong id="visible-count">100 questions</strong><span id="filtered-a"></span><span id="filtered-b"></span></div><button id="reset">Reset filters</button><p id="empty" hidden>No matching questions. Reset filters to see all 100.</p>{''.join(rows)}</section>
<section id="method"><h2>What this evidence can—and cannot—say</h2><p>The frozen v1.0.0 dataset has 25 zakat, 25 investing, 20 principles, 20 budgeting and 10 safety questions. Only 40 have deterministic numerical grading. The other 60 require qualified human review. There is no combined 100-question accuracy score.</p><p>Greedy generation, 384-token limit, seed 2026, BF16, SDPA, eight CPU threads and one identical warm-up. Latency includes prompt prefill and decode, excludes tokenization. Throughput is total output tokens divided by generation time. Longer answers can take longer without a slower decoder.</p><p>Both runs use the same server2 hardware and runtime. These are sequential single runs on a shared server, not isolated repeated performance trials. Training-data overlap has not been ruled out; the exact training base revision is not established by the model card. No religious certification or comprehensive fiqh expertise is implied.</p><div class="table-scroll"><table>{metadata}</table></div><p>Dataset SHA-256: <code>{out['dataset_sha256']}</code></p><p><a href="../../../results/comparisons/20261115/comparison.json">Complete paired data</a> · <a href="review.html">Blinded conceptual review packet</a> · <a href="../../../reports/20261115/REPRODUCIBILITY.md">Reproduce the evaluation</a> · <a href="../../../reports/20261115/LIMITATIONS.md">Limitations</a></p></section><footer>Saved model outputs only. No live model, external scripts or API required.</footer></main>
<script>
const questions=[...document.querySelectorAll('[data-question]')];
function filter(){{let n=0,den=0,a=0,b=0;const search=document.querySelector('#search').value.toLowerCase();questions.forEach(el=>{{el.hidden=['category','difficulty','outcome'].some(k=>{{const v=document.getElementById(k).value;return v!=='all'&&el.dataset[k]!==v;}})||!el.textContent.toLowerCase().includes(search);if(!el.hidden){{n++;if(el.dataset.numeric==='1'){{den++;a+=Number(el.dataset.a);b+=Number(el.dataset.b);}}}}}});document.querySelector('#visible-count').textContent=n+' questions shown';document.querySelector('#filtered-a').textContent='Original: '+(den?a+'/'+den+' numerical ('+(100*a/den).toFixed(1)+'%)':'No numerical score');document.querySelector('#filtered-b').textContent='Barakah: '+(den?b+'/'+den+' numerical ('+(100*b/den).toFixed(1)+'%)':'No numerical score');document.querySelector('#empty').hidden=n!==0;}}
['category','difficulty','outcome'].forEach(k=>document.getElementById(k).addEventListener('change',filter));document.querySelector('#search').addEventListener('input',filter);document.querySelector('#reset').addEventListener('click',()=>{{['category','difficulty','outcome'].forEach(k=>document.getElementById(k).value='all');document.querySelector('#search').value='';filter();}});filter();
document.querySelector('#chart').addEventListener('change',function(){{document.querySelector('#chart-image').src='../svg/'+this.value+'.svg';document.querySelector('#chart-image').alt=this.selectedOptions[0].textContent;document.querySelector('#chart-svg').href='../svg/'+this.value+'.svg';document.querySelector('#chart-png').href='../png/'+this.value+'.png';}});
</script></body></html>'''
    (folder/'html').mkdir(parents=True,exist_ok=True);(folder/'html/index.html').write_text(content)


def review_page(comparison_path, folder):
    rows=json.loads((comparison_path.parent/'review/blinded_responses.json').read_text());esc=html.escape
    body=''.join(f'<details><summary>{r["question_id"]}</summary><p>{esc(r["question"])}</p><div class="answers">'+''.join(f'<article><h2>Response {label}</h2><p>{esc(r["response_"+label])}</p></article>' for label in ('A','B'))+'</div></details>' for r in rows)
    content='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Barakah blinded review</title><style>'''+STYLE.replace('fonts/dm-sans.woff2','../../html/fonts/dm-sans.woff2')+'''.answers{display:grid;grid-template-columns:1fr 1fr;gap:32px}.answers article{min-width:0}.answers h2{font-size:18px}@media(max-width:700px){.answers{grid-template-columns:1fr}}</style></head><body><main><h1>Conceptual review packet</h1><p>60 questions. A/B identity is independently shuffled for each question. Share this page and blinded_responses.json with reviewers, not the identity key or main dashboard.</p><p>For each response record reviewer identity and qualification, timestamp, evidence and judgments on accuracy, completeness, unsupported assertions, financial safety, hallucinations, uncertainty, religious differences and invented definitive fatwas. Use true / false / unresolved; unresolved is not incorrect. Two independent qualified reviewers and adjudication are recommended.</p><p>Record question ID and response letter. The coordinator uses review_identity_key.json to attach the exact run ID and response SHA-256, then fills the corresponding response-bound review template. See HUMAN_REVIEW.md. No review has been completed by this tool.</p>'''+body+'</main></body></html>'
    (folder/'html/review.html').write_text(content)


def generate(comparison_path, folder):
    if folder.exists():raise FileExistsError('Choose a fresh visual output directory')
    out=json.loads(comparison_path.read_text());charts(out,folder);dashboard(out,folder);review_page(comparison_path,folder)
    print(f'Generated 10 PNG + 10 SVG charts and {folder}/html/index.html')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--comparison',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();generate(a.comparison,a.output)
