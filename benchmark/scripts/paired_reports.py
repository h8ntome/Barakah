"""Reports derived from paired results; unavailable expert metrics remain explicit."""
import argparse
import json
from pathlib import Path
from common import ROOT


def fmt(v):
    if isinstance(v,int):return f'{v:,}'
    return f'{v:.3f}' if v is not None else 'Unavailable'


def delta_text(metric, unit):
    if metric['absolute'] is None:
        return 'Unavailable (no paired measured metric)'
    relative = f"{100*metric['relative_change']:+.2f}%" if metric['relative_change'] is not None else 'relative change unavailable'
    return f"{metric['absolute']:+.3f} {unit} ({relative})"


def generate(path,folder):
    out=json.loads(path.read_text());runs=list(out['runs'].values());summaries=[r['summary'] for r in runs]
    metric=out['numeric_correctness'];counts=out['outcome_counts'];stats=out['statistics']
    n=[s['automatic_numeric_correctness']['numerator'] for s in summaries]
    change=metric['percentage_points'];relative=metric['relative_change']
    conclusion=('The fine-tuned checkpoint improved the measured numerical score' if change>0 else 'The fine-tuned checkpoint regressed on the measured numerical score' if change<0 else 'Fine-tuning did not change the measured numerical score')
    caveat='This does not establish improved conceptual Islamic-finance quality; those answers are unreviewed, and training overlap and the exact training base revision are unresolved.'
    rows=[]
    for title,field in [('Mean latency (s)','mean_latency_seconds'),('Median latency (s)','median_latency_seconds'),('P95 latency (s)','p95_latency_seconds'),('Output tokens/s','aggregate_output_tokens_per_second'),('Total output tokens','output_tokens')]:
        rows.append(f"| {title} | {fmt(summaries[0]['performance'][field])} | {fmt(summaries[1]['performance'][field])} |")
    for title,field in [('Model loading (s)','model_loading_seconds'),('Peak GPU allocated (GiB)','peak_gpu_allocated_bytes'),('Peak sampled process RSS (GiB)','peak_process_rss_bytes'),('Parameter count','parameter_count')]:
        vals=[r['metadata'].get(field) for r in runs]
        if 'bytes' in field:vals=[v/1024**3 if v is not None else None for v in vals]
        rows.append(f'| {title} | {fmt(vals[0])} | {fmt(vals[1])} |')
    group_tables=[]
    for field in ('category','difficulty'):
        group_tables.append(f'### By {field}\n\n| Group | Original numeric | Barakah numeric | Conceptual pending per model |\n|---|---:|---:|---:|')
        for k,a in summaries[0]['by_'+field].items():
            b=summaries[1]['by_'+field][k];ms=[r['automatic_numeric_correctness'] for r in (a,b)]
            vs=[f"{m['numerator']}/{m['denominator']} ({100*m['rate']:.1f}%)" if m['denominator'] else 'Unavailable: no numerical tasks' for m in ms]
            group_tables.append(f"| {k} | {vs[0]} | {vs[1]} | {a['pending_correctness_review']} |")
    selected=[]
    # Predeclared transparent example rule: first improvement, first regression, then first unchanged error/correct.
    for outcome in ('improved','regressed','both_incorrect','both_correct'):
        row=next((r for r in out['questions'] if r['outcome']==outcome),None)
        if row and len(selected)<3:selected.append(row)
    brief='| Question | Original final answer | Barakah final answer | Outcome |\n|---|---|---|---|\n'
    for r in selected:
        terminal=lambda label:r[label+'_response'].strip().splitlines()[-1].replace('Final answer:','').strip()
        brief+=f"| {r['question_id']} | {terminal('baseline')} | {terminal('barakah')} | {r['outcome'].replace('_',' ')} |\n"
    examples=[]
    for r in selected:
        examples.append(f"### {r['question_id']} — {r['outcome'].replace('_',' ')}\n\n{r['question']}\n\n**Original ({r['baseline_status']}):**\n\n> "+r['baseline_response'].replace('\n','\n> ')+"\n\n**Barakah ("+r['barakah_status']+"):**\n\n> "+r['barakah_response'].replace('\n','\n> '))
    ci=stats['paired_accuracy_delta_bootstrap_95'];lat=out['mean_latency_seconds'];through=out['aggregate_output_tokens_per_second']
    report=f'''# Barakah AI matched benchmark report

Evaluation date: 2026-11-15 UTC. All values below derive from immutable saved model responses.

## Executive summary

**{conclusion}: {n[0]}/40 ({100*metric['baseline']:.1f}%) → {n[1]}/40 ({100*metric['candidate']:.1f}%).**
Absolute change: **{change:+.1f} percentage points**; relative accuracy change: **{f'{100*relative:+.2f}%' if relative is not None else 'Unavailable (zero baseline)'}**.
{caveat}

Both actual models completed 100 question attempts each. No rule engine, external API,
calculator, retrieval system or simulated response was substituted. Historical reports,
charts and original/rules runs are preserved separately.

## Models and provenance

| | Original | Barakah |
|---|---|---|
| Repository | {runs[0]['model']} | {runs[1]['model']} |
| Immutable revision | {runs[0]['metadata']['fingerprint']['revision']} | {runs[1]['metadata']['fingerprint']['revision']} |
| Run ID | {runs[0]['run_id']} | {runs[1]['run_id']} |
| Format | Full BF16 checkpoint | Full BF16 checkpoint, not a PEFT adapter |

See MODEL_PROVENANCE.md for file hashes, snapshot locations, licenses and unknown training details.

## Dataset, hardware and settings

Dataset v1.0.0, SHA-256 `{out['dataset_sha256']}`. 100 English questions: zakat 25,
investing 25, principles 20, budgeting 20, safety 10. Forty numerical and sixty conceptual.
No question/reference changes. Full DATASET_CARD.md and SOURCE_EVIDENCE.md remain authoritative.

Server2: AMD Ryzen AI MAX+ 395, Radeon 8060S integrated GPU, approximately 123 GiB usable
system RAM. Same ROCm PyTorch, BF16, Transformers, SDPA and tokenizer input IDs.
Neutral system prompt, greedy decoding, 384-token cap, seed 2026, 8 CPU threads,
identical 24-token-capped warm-up. No unrelated workloads stopped.
See METHODOLOGY.md for the exact prompt, timing protocol and shared-host caveats.

## Correctness and response coverage

| Metric | Original | Barakah |
|---|---:|---:|
| Verified numerical accuracy | {n[0]}/40 ({100*metric['baseline']:.1f}%) | {n[1]}/40 ({100*metric['candidate']:.1f}%) |
| Numerically incorrect | {summaries[0]['automatic_status_counts']['incorrect']} | {summaries[1]['automatic_status_counts']['incorrect']} |
| Numerically unparseable | {summaries[0]['automatic_status_counts']['unparseable']} | {summaries[1]['automatic_status_counts']['unparseable']} |
| Numerical generation errors | {summaries[0]['automatic_generation_errors']} | {summaries[1]['automatic_generation_errors']} |
| Missing questions | {summaries[0]['missing_responses']} | {summaries[1]['missing_responses']} |
| Successful generations | {summaries[0]['performance']['successful_n']}/100 | {summaries[1]['performance']['successful_n']}/100 |
| All generation failures | {summaries[0]['generation_failure_rate']['numerator']}/100 | {summaries[1]['generation_failure_rate']['numerator']}/100 |
| Responses reaching token cap | {summaries[0]['truncated_responses']}/100 | {summaries[1]['truncated_responses']}/100 |
| Conceptual review | Unavailable; 60 pending | Unavailable; 60 pending |
| Verified hallucination / unsafe rates | Unavailable; no adjudication | Unavailable; no adjudication |

{'\n'.join(group_tables)}

## Paired improvements, regressions and uncertainty

- Baseline incorrect → Barakah correct: **{counts['improved']}**.
- Baseline correct → Barakah incorrect: **{counts['regressed']}**.
- Both correct: **{counts['both_correct']}**.
- Both not correct: **{counts['both_incorrect']}** (includes strict-format failures).
- Conceptual outcomes not conclusively graded: **{counts['unreviewed']}**.
- Exact two-sided McNemar p-value: **{stats['mcnemar_exact_two_sided_p']:.6f}**.
- Paired bootstrap 95% accuracy-change interval: **[{100*ci[0]:+.1f}, {100*ci[1]:+.1f}] percentage points**.

These are exploratory results on a small, nonrandom, repetitive task set. McNemar
is the primary paired significance check. A percentile bootstrap interval can exclude
zero with sparse discordant outcomes even when the exact test is not significant;
do not use the bootstrap interval to overrule the exact test. A p-value
is not proof of broad financial or religious competence. Unknown training overlap
prevents a clean held-out generalization claim. No combined correctness is published.

## Performance and resources

| Metric | Original | Barakah |
|---|---:|---:|
{'\n'.join(rows)}

Mean latency change: {delta_text(lat,'seconds')}; lower is better.
Throughput change: {delta_text(through,'output tokens/s')}; higher is better.
Paired mean latency-change bootstrap interval: {stats['paired_latency_delta_seconds_bootstrap_95']} seconds.
These are same-host single-session observations, **not** randomized isolated speed trials.
Response length affects total latency; throughput includes prefill. See workload logs
and the discussion of shared integrated-GPU memory in METHODOLOGY.md.

## Question-level error analysis and demo examples

All 100 paired answers, statuses, exact prompts, token counts and errors are available
in `results/comparisons/20261115/questions.csv` and comparison.json, and in the dashboard.
Examples below use the first improvement, first regression, then first shared error or
success in frozen question order (up to three). They are not cherry-picked best answers.
No conceptual illustration is presented as verified correctness.

{'\n\n'.join(examples)}

## Limitations and conclusion

{conclusion}. {caveat}
Read LIMITATIONS.md and LEAKAGE_CHECK.md before presenting this result. A broader,
independently authored private holdout and qualified blinded review are the next
credible steps—not a stronger marketing claim from these same 40 calculations.
'''
    from common import dataset
    references={q['id']:q for q in dataset()}
    error_report='# Question-level error analysis\n\nAll 100 paired responses are retained in questions.csv. No conceptual judgment is verified.\n\n'
    for outcome in ('improved','regressed','both_correct','both_incorrect','unreviewed'):
        ids=[r['question_id'] for r in out['questions'] if r['outcome']==outcome]
        error_report+=f"## {outcome.replace('_',' ').title()} ({len(ids)})\n\n"+(', '.join(ids) if ids else 'None.')+'\n\n'
    error_report+='## Every numerical failure\n\n| Question | Reference quantity | Original parsed quantity | Barakah parsed quantity | Outcome |\n|---|---|---|---|---|\n'
    score_maps=[{s['question_id']:s for s in run['scores']} for run in runs]
    for row in out['questions']:
        if row['numeric'] and row['outcome']!='both_correct':
            q=references[row['question_id']];ss=[m[q['id']] for m in score_maps]
            error_report+=f"| {q['id']} | {q['expected_numeric']} {q['unit']} | {ss[0].get('parsed_value','Unavailable')} | {ss[1].get('parsed_value','Unavailable')} | {row['outcome']} |\n"
    error_report+='\nReferences appear only in evaluation artifacts, never in model inference. Wrong final quantities are measured numerical errors, not automatically verified hallucinations or unsafe advice.\n'
    folder.mkdir(parents=True,exist_ok=True)
    for name,text in [('ERROR_ANALYSIS.md',error_report),('BENCHMARK_REPORT.md',report),('DEMO_EXAMPLES.md','# Three traceable numerical comparisons\n\nSelection: first improvement if any, first regression, then first unchanged failure/success.\n\n'+brief+f"\nNumerical improvements: {counts['improved']}; regressions: {counts['regressed']}. Full response evidence follows.\n\n"+'\n\n'.join(examples))]:
        p=folder/name
        if p.exists():raise FileExistsError(p)
        p.write_text(text)
    judge=f'''# Barakah AI: what the benchmark actually shows

Barakah is an Islamic personal-finance application. Its AI candidate is a full
fine-tuned checkpoint published by h8notme, attributed to LiquidAI's LFM3-1.7B.
The card credits Unsloth/TRL; the training dataset and exact training recipe are not verified.

## The measured result

**Original: {n[0]}/40 ({100*metric['baseline']:.1f}%) → Barakah: {n[1]}/40 ({100*metric['candidate']:.1f}%).**

**{change:+.1f} percentage points. {counts['improved']} improvements. {counts['regressed']} regressions.**

{conclusion}. The paired test p-value is {stats['mcnemar_exact_two_sided_p']:.4f};
the 95% paired interval is [{100*ci[0]:+.1f}, {100*ci[1]:+.1f}] percentage points.
Only 40 authored calculations are scored—not all of Islamic finance.

Both models answered the same 100 questions on server2 with the same prompt,
output budget and runtime. All responses, including regressions, are preserved.
Mean generation latency was {fmt(summaries[0]['performance']['mean_latency_seconds'])}s versus
{fmt(summaries[1]['performance']['mean_latency_seconds'])}s; throughput was
{fmt(summaries[0]['performance']['aggregate_output_tokens_per_second'])} versus
{fmt(summaries[1]['performance']['aggregate_output_tokens_per_second'])} output tokens/s.
These are single shared-server measurements, not guaranteed serving performance.
Output token totals: original {fmt(summaries[0]['performance']['output_tokens'])},
Barakah {fmt(summaries[1]['performance']['output_tokens'])}. Lower average latency alone
is not evidence of a faster decoder; response length matters.
Responses reaching the output cap: {summaries[0]['truncated_responses']}/100 original,
{summaries[1]['truncated_responses']}/100 Barakah.

## What remains unverified

- 60 conceptual answers per model still need qualified human review.
- No verified hallucination, safety or religious-certification claim is supported.
- Training overlap has not been ruled out; exact training base revision is unknown.
- A full checkpoint is confirmed; a specific LoRA training process is not.

## Open the evidence

- [Interactive dashboard](../../visuals/20261115/html/index.html)
- [Ten presentation charts](../../visuals/20261115/png/)
- [Complete report](BENCHMARK_REPORT.md) and [three demo examples](DEMO_EXAMPLES.md)
- [All 100 paired responses](../../results/comparisons/20261115/questions.csv)
- [Reproduce it](REPRODUCIBILITY.md)

**Bottom line:** {conclusion.lower()}. {caveat}
'''
    p=folder/'JUDGES_SUMMARY.md'
    if p.exists():raise FileExistsError(p)
    p.write_text(judge)
    print(folder)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--comparison',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();generate(a.comparison,a.output)
